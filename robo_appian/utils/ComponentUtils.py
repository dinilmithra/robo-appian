"""Shared low-level helpers used by robo_appian UI components."""

import logging
from pathlib import Path
from typing import Optional

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    expect,
)
from robo_automation import RoboLocator, Scope

logger = logging.getLogger(__name__)


class ComponentUtils:
    """Shared browser automation operations used by Appian components."""

    @staticmethod
    def normalize_timeout_seconds(value: float | int | None) -> float | None:
        """Normalize an optional Appian component timeout expressed in seconds.

        ``None`` preserves the framework/context default timeout (normally
        configured from ``WAIT_TIME``). A positive finite number overrides that
        default for waits/actions performed by the component.
        """
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("timeout must be a positive number of seconds or None.")
        timeout = float(value)
        if timeout <= 0 or timeout == float("inf") or timeout != timeout:
            raise ValueError("timeout must be a positive finite number of seconds.")
        return timeout

    @staticmethod
    def timeout_kwargs(value: float | int | None) -> dict[str, float]:
        """Return runtime timeout kwargs for an optional seconds value."""
        timeout = ComponentUtils.normalize_timeout_seconds(value)
        return {} if timeout is None else {"timeout": timeout * 1000}

    @staticmethod
    def normalize_visibility(value: bool | str | None) -> bool | None:
        """Normalize the shared tri-state Appian visibility constraint.

        ``None`` and blank/whitespace strings mean no visibility filter.
        Boolean ``True`` and ``False`` retain their normal meanings.
        """
        if value is None:
            return None
        if isinstance(value, str):
            if not value.strip():
                return None
            raise ValueError("visible must be True, False, None, or a blank string.")
        if isinstance(value, bool):
            return value
        raise TypeError("visible must be a bool, None, or a blank string.")

    @staticmethod
    def unwrap_scope(scope):
        """Return the underlying browser scope for framework locator wrappers.

        AppianLocator derives from RoboLocator and exposes its underlying locator
        through the ``locator`` property. Legacy helpers in this module perform
        low-level scoped lookups, so they must operate on that underlying locator
        rather than treating the property as a callable locator factory.
        """
        if isinstance(scope, RoboLocator):
            return scope.locator
        return scope

    @staticmethod
    def xpath_literal(value: str) -> str:
        """Quote arbitrary text for insertion into an XPath expression.

        Args:
            value: Text that may contain single or double quotes.

        Returns:
            str: A valid XPath literal or ``concat`` expression.
        """
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def click(locator: Locator) -> None:
        """Click a visible, enabled locator and log the dispatched interaction.

        browser automation's actionability checks determine when the target is ready. The
        method logs immediately before dispatch and after ``click()`` returns so
        failures can distinguish a click that never became actionable from one
        that browser automation successfully dispatched. One force-click recovery is
        retained only for the existing pointer-interception case.

        Args:
            locator: Resolved element or element collection to filter by visibility.
        """
        visible_locator = locator.filter(visible=True)

        expect(visible_locator).to_be_visible()
        expect(visible_locator).to_be_enabled()

        logger.info(
            "Before button/element click: Playwright target is visible and enabled."
        )

        try:
            visible_locator.click()
        except PlaywrightError as exc:
            message = str(exc).lower()
            if "intercepts pointer events" not in message:
                logger.exception("Playwright click failed before completion.")
                raise

            logger.warning(
                "Click intercepted by overlapping element; retrying once with force click."
            )
            expect(visible_locator).to_be_visible()
            expect(visible_locator).to_be_enabled()
            visible_locator.click(force=True)
            logger.info("Forced Playwright click completed after pointer interception.")
            return

        logger.info(
            "After button/element click: Playwright click completed successfully."
        )

    @staticmethod
    def click_by_text(scope: Scope, text: str, excat_match: bool = False) -> None:
        """Click the first visible element whose text matches the requested text.

        Use this only when the visible text identifies the clickable element
        itself. Duplicate matches are resolved by choosing the first visible one.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Text to locate.
            excat_match: Whether the element text must match exactly.
        """
        raw_scope = ComponentUtils.unwrap_scope(scope)
        link = raw_scope.get_by_text(text, exact=excat_match).filter(visible=True).first
        expect(link).to_be_visible()
        link.click()

    @staticmethod
    def click_by_title(scope: Scope, title: str) -> None:
        """Click the first visible element with the requested title attribute.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            title: Title attribute value to locate.
        """
        raw_scope = ComponentUtils.unwrap_scope(scope)
        link = raw_scope.get_by_title(title).filter(visible=True).first
        expect(link).to_be_visible()
        link.click()

    @staticmethod
    def click_by_id(scope: Scope, button_id: str) -> None:
        """Click the first visible, enabled element with an exact HTML ID.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            button_id: Literal HTML ID, including IDs that begin with numbers.
        """
        raw_scope = ComponentUtils.unwrap_scope(scope)
        locator = raw_scope.locator(f'[id="{button_id}"]:not([disabled])')
        active_locator = locator.filter(visible=True).first
        expect(active_locator).to_be_visible()
        active_locator.click()

    @staticmethod
    def is_visible_by_xpath(scope: Scope, xpath: str) -> bool:
        """Return whether at least one XPath match is currently visible.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            xpath: XPath expression without application-specific CSS classes.

        Returns:
            bool: ``True`` when at least one matching element is visible.
        """
        expression = str(xpath or "").strip()
        if not expression:
            raise ValueError("XPath cannot be empty or whitespace.")

        raw_scope = ComponentUtils.unwrap_scope(scope)
        return raw_scope.locator(f"xpath={expression}").filter(visible=True).count() > 0

    @staticmethod
    def is_visible_by_attribute(
        scope: Scope,
        attribute: str,
        value: str,
    ) -> bool:
        """Return whether an element with an exact attribute value is visible.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            attribute: HTML attribute name to match.
            value: Exact attribute value to match.

        Returns:
            bool: ``True`` when at least one matching element is visible.
        """
        attribute_name = str(attribute or "").strip()
        if not attribute_name:
            raise ValueError("Attribute cannot be empty or whitespace.")

        value_literal = ComponentUtils.xpath_literal(str(value or ""))
        return ComponentUtils.is_visible_by_xpath(
            scope,
            f"//*[@{attribute_name}={value_literal}]",
        )

    @staticmethod
    def get_component_by_attribute(
        scope: Scope,
        attribute: str,
        value: str,
        visible_only: bool = False,
    ) -> Optional[Locator]:
        """Return the first component matching an exact attribute value.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            attribute: HTML attribute name used to locate the component.
            value: Exact attribute value used to locate the component.
            visible_only: When true, require the component to be visible.

        Returns:
            Optional[Locator]: The first matching framework locator, or ``None`` when no matching
            component exists.
        """
        attribute_name = str(attribute or "").strip()
        if not attribute_name:
            raise ValueError("Attribute cannot be empty or whitespace.")

        value_literal = ComponentUtils.xpath_literal(str(value or ""))
        raw_scope = ComponentUtils.unwrap_scope(scope)
        components = raw_scope.locator(f"xpath=//*[@{attribute_name}={value_literal}]")
        if visible_only:
            components = components.filter(visible=True)

        if components.count() == 0:
            return None
        return components.first

    @staticmethod
    def get_ancestor_attribute_value(
        component: Locator,
        attribute: str,
    ) -> str:
        """Read an attribute from the nearest ancestor that defines it.

        Args:
            component: framework locator whose ancestors are searched.
            attribute: HTML attribute to read from the nearest matching ancestor.

        Returns:
            str: The normalized attribute value, or an empty string when no matching
            ancestor or value exists.
        """
        attribute_name = str(attribute or "").strip()
        if not attribute_name:
            raise ValueError("Attribute cannot be empty or whitespace.")

        ancestor = component.locator(f"xpath=ancestor::*[@{attribute_name}][1]")
        if ancestor.count() == 0:
            return ""

        return str(ancestor.first.get_attribute(attribute_name) or "").strip()

    @staticmethod
    def get_descendant_texts_by_component_id(
        scope: Scope,
        component_id: str,
        descendant_xpath: str,
        visible_only: bool = False,
    ) -> list[str]:
        """Read descendant text under the component with the supplied DOM ID.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            component_id: Exact DOM ``id`` of the parent component.
            descendant_xpath: Relative XPath selecting descendants, for example
                ``.//p``.
            visible_only: When true, read only visible descendant matches.

        Returns:
            list[str]: Unique non-empty normalized text values in DOM order.
        """
        component_id_value = str(component_id or "").strip()
        relative_xpath = str(descendant_xpath or "").strip()
        if not component_id_value:
            raise ValueError("Component ID cannot be empty or whitespace.")
        if not relative_xpath:
            raise ValueError("Descendant XPath cannot be empty or whitespace.")

        component_id_literal = ComponentUtils.xpath_literal(component_id_value)
        parent_xpath = f"//*[@id={component_id_literal}]"
        descendant = relative_xpath
        if descendant.startswith(".//"):
            descendant = descendant[1:]
        elif not descendant.startswith("/"):
            descendant = f"//{descendant}"

        return ComponentUtils.get_texts_by_xpath(
            scope,
            f"({parent_xpath}){descendant}",
            visible_only=visible_only,
        )

    @staticmethod
    def get_texts_by_xpath(
        scope: Scope,
        xpath: str,
        visible_only: bool = False,
    ) -> list[str]:
        """Return unique normalized text from elements matching XPath.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            xpath: XPath expression without application-specific CSS classes.
            visible_only: When true, read only currently visible matches.

        Returns:
            list[str]: Unique non-empty text values in DOM order.
        """
        expression = str(xpath or "").strip()
        if not expression:
            raise ValueError("XPath cannot be empty or whitespace.")

        raw_scope = ComponentUtils.unwrap_scope(scope)
        matches = raw_scope.locator(f"xpath={expression}")
        if visible_only:
            matches = matches.filter(visible=True)

        values: list[str] = []
        for index in range(matches.count()):
            try:
                raw_text = (
                    matches.nth(index).inner_text()
                    if visible_only
                    else matches.nth(index).text_content()
                )
                text = " ".join((raw_text or "").split())
            except Exception:
                text = ""
            if text and text not in values:
                values.append(text)
        return values

    @staticmethod
    def get_visible_texts_by_xpath(scope: Scope, xpath: str) -> list[str]:
        """Return unique normalized text from visible XPath matches.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            xpath: XPath expression evaluated within the supplied scope.


        Returns:
            list[str]: Visible text values from elements matching the XPath expression.
        """
        return ComponentUtils.get_texts_by_xpath(
            scope,
            xpath,
            visible_only=True,
        )

    @staticmethod
    def get_attribute_values_by_xpath(
        scope: Scope,
        xpath: str,
        attribute: str,
        visible_only: bool = False,
    ) -> list[str]:
        """Return unique non-empty attribute values from XPath matches.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            xpath: XPath expression without application-specific CSS classes.
            attribute: Attribute name to read from each matching element.
            visible_only: When true, inspect only currently visible matches.

        Returns:
            list[str]: Unique non-empty attribute values in DOM order.
        """
        expression = str(xpath or "").strip()
        if not expression:
            raise ValueError("XPath cannot be empty or whitespace.")

        attribute_name = str(attribute or "").strip()
        if not attribute_name:
            raise ValueError("Attribute cannot be empty or whitespace.")

        raw_scope = ComponentUtils.unwrap_scope(scope)
        matches = raw_scope.locator(f"xpath={expression}")
        if visible_only:
            matches = matches.filter(visible=True)

        values: list[str] = []
        for index in range(matches.count()):
            value = str(matches.nth(index).get_attribute(attribute_name) or "").strip()
            if value and value not in values:
                values.append(value)
        return values

    @staticmethod
    def wait_until_visible(scope: Scope, message: str = None) -> None:
        """Wait until a scope or locator is visible.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            message: Optional assertion message used when the wait fails.
        """
        expect(ComponentUtils.unwrap_scope(scope), message).to_be_visible()

    @staticmethod
    def wait_until_hidden(scope: Scope) -> None:
        """Wait until a scope or locator is hidden or detached.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
        """
        expect(ComponentUtils.unwrap_scope(scope)).to_be_hidden()

    @staticmethod
    def tab(scope: Scope, occurrence: Optional[int] = None) -> None:
        """Move keyboard focus forward on the supplied scope.

        Use this to trigger Appian focus-out behavior after editing a control.
        When ``occurrence`` is omitted, Tab is pressed once.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            occurrence: Optional number of Tab key presses. Defaults to 1 when
                omitted.

        Raises:
            ValueError: If occurrence is provided and is not a positive integer.
        """
        if occurrence is None:
            occurrence = 1
        elif (
            isinstance(occurrence, bool)
            or not isinstance(occurrence, int)
            or occurrence < 1
        ):
            raise ValueError("Tab occurrence must be a positive integer.")

        raw_scope = ComponentUtils.unwrap_scope(scope)
        for _ in range(occurrence):
            if hasattr(scope, "press_key"):
                scope.press_key("Tab")
            elif isinstance(raw_scope, Page):
                raw_scope.keyboard.press("Tab")
            else:
                raw_scope.press("Tab")

    @staticmethod
    def upload_document(
        scope: Scope,
        directory_path: str,
        file_name: str,
    ) -> str:
        """Set a local file on the first Appian upload input.

        The path is expanded and resolved from ``directory_path`` plus
        ``file_name``. The standard multiple-file widget is preferred; otherwise
        the first generic file input is used.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            directory_path: Local directory containing the upload file.
            file_name: File name relative to ``directory_path``.

        Returns:
            str: Absolute path of the file supplied to the browser.

        Raises:
            FileNotFoundError: If the resolved local file does not exist.
        """
        resolved_path = Path(directory_path, file_name).expanduser().resolve()
        if not resolved_path.is_file():
            raise FileNotFoundError(f"Upload file not found at: {resolved_path}")

        raw_scope = ComponentUtils.unwrap_scope(scope)
        widget_input = raw_scope.locator(
            "div.MultipleFileUploadWidget---upload_field input[type='file']"
        )
        if widget_input.count() > 0:
            widget_input.first.set_input_files(str(resolved_path))
        else:
            raw_scope.locator("input[type='file']").first.set_input_files(
                str(resolved_path)
            )

        return str(resolved_path)

    @staticmethod
    def find_container(scope: Scope, field_label: str, header_text: str) -> Locator:
        """Build a locator for a region containing a heading and field label.

        Use this to scope duplicate fields to a semantic region. The returned
        locator is not awaited or validated; the caller owns visibility checks.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            field_label: Visible field text required inside the region.
            header_text: Visible text whose ancestor region is selected.

        Returns:
            Locator: A live locator for the nearest matching region.
        """
        xpath = (
            f"//*[normalize-space()='{header_text}']"
            f"/ancestor::*[@role='region']"
            f"[.//*[normalize-space()='{field_label}']][1]"
        )
        raw_scope = ComponentUtils.unwrap_scope(scope)
        return raw_scope.locator(f"xpath={xpath}")

    @staticmethod
    def find_locator_by_xpath(scope: Scope, xpath: str) -> Locator:
        """Build a locator using an XPath expression.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            xpath: XPath expression to locate the element.

        Returns:
            Locator: A live locator for the element matching the XPath.
        """
        raw_scope = ComponentUtils.unwrap_scope(scope)
        locator = raw_scope.locator(f"xpath={xpath}").filter(visible=True).first
        return locator

    @staticmethod
    def wait_and_find_locator_by_xpath(scope: Scope, xpath: str) -> Locator:
        """Build a locator using an XPath expression.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            xpath: XPath expression to locate the element.

        Returns:
            Locator: A live locator for the element matching the XPath.
        """
        locator = ComponentUtils.find_locator_by_xpath(scope, xpath)
        expect(locator).to_be_visible()
        return locator
