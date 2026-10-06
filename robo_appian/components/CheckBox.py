"""Generic helpers for checkbox interaction and state validation."""

from typing import Optional

from playwright.sync_api import Locator, expect
from robo_automation import Scope

from robo_appian.utils.ComponentUtils import ComponentUtils


class CheckBox:
    """Reusable operations for Appian checkbox controls."""

    @staticmethod
    def __checkbox_locator(scope: Scope, text: str) -> Locator:
        """Return one locator that supports labeled and Appian boolean checkboxes.

        Appian checkbox markup is observed in two common forms:
        1. A visible option ``label`` whose ``for`` attribute points directly to
           the native ``input[type='checkbox']``.
        2. A boolean field label (for example ``IT``) whose ``id`` is referenced
           by a ``role='group'`` element through ``aria-labelledby``; the group
           contains the native checkbox input.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Visible checkbox option label or boolean field label.

        Returns:
            Locator resolving the matching native checkbox input.

        Raises:
            ValueError: If ``text`` is blank.
        """
        field_text = str(text or "").strip()
        if not field_text:
            raise ValueError("Checkbox field text cannot be empty.")

        safe_text = ComponentUtils.xpath_literal(field_text)
        xpath = (
            "xpath=("
            "//input[@type='checkbox' and "
            f"@id = //label[@for and normalize-space(.)={safe_text}]/@for]"
            " | "
            "//*[@role='group' and "
            f"@aria-labelledby = //*[self::span or self::label][@id and normalize-space(.)={safe_text}]/@id]"
            "//input[@type='checkbox']"
            ")[1]"
        )
        return scope.locator(xpath)

    @staticmethod
    def __label_for_checkbox(scope: Scope, checkbox: Locator, text: str) -> Locator:
        """Return the visible Appian label associated with a checkbox input."""
        checkbox_id = checkbox.get_attribute("id")
        if not checkbox_id:
            raise ValueError(f"Checkbox '{text}' has no id attribute.")

        safe_checkbox_id = ComponentUtils.xpath_literal(checkbox_id)
        return (
            scope.locator(f"xpath=//label[@for={safe_checkbox_id}]")
            .filter(visible=True)
            .first
        )

    @staticmethod
    def is_visible(scope: Scope, text: str) -> bool:
        """Return whether the requested Appian checkbox is present.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Visible text used to identify the target element.


        Returns:
            bool: ``True`` when a matching Appian checkbox is visible; otherwise ``False``.
        """
        return CheckBox.__checkbox_locator(scope, text).count() > 0

    @staticmethod
    def is_checked(
        scope: Scope,
        text: str,
        timeout: Optional[float] = None,
    ) -> bool:
        """Return whether an Appian checkbox reaches the checked state.

        A single checkbox XPath supports both conventional labeled options and
        Appian boolean fields whose visible field label is linked to a checkbox
        group through ``aria-labelledby``.

        When ``timeout`` is supplied, wait up to that many seconds for the
        checkbox to become checked before returning ``False``. When omitted,
        inspect the current state immediately.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Visible option label or boolean field label.
            timeout: Optional timeout in seconds to wait for a checked state.

        Returns:
            bool: ``True`` when the checkbox is checked within the requested window;
            otherwise ``False``.
        """
        field_text = str(text or "").strip()
        checkbox = CheckBox.__checkbox_locator(scope, field_text)
        timeout_ms = None if timeout is None else max(0.0, float(timeout)) * 1000

        assertion = expect(
            checkbox,
            f"Checkbox '{field_text}' was not found.",
        )
        if timeout_ms is None:
            assertion.to_be_attached()
            return checkbox.is_checked()

        assertion.to_be_attached(timeout=timeout_ms)
        try:
            expect(
                checkbox,
                f"Checkbox '{field_text}' did not become checked.",
            ).to_be_checked(timeout=timeout_ms)
            return True
        except AssertionError:
            return False

    @staticmethod
    def select(scope: Scope, text: str, selected: bool = True) -> None:
        """Select or deselect an Appian checkbox using its visible label.

        The checkbox is re-resolved after clicking because Appian may replace
        the control during a SAIL re-render.

        Args:
            scope: Playwright scope containing the checkbox.
            text: Visible checkbox option label or boolean field label.
            selected: ``True`` to check, ``False`` to uncheck.
        """
        label_text = str(text or "").strip()
        checkbox = CheckBox.__checkbox_locator(scope, label_text)
        expect(
            checkbox,
            f"Checkbox '{label_text}' was not found.",
        ).to_be_attached()

        if checkbox.is_checked() == selected:
            return

        label = CheckBox.__label_for_checkbox(scope, checkbox, label_text)
        expect(
            label,
            f"Visible checkbox label for '{label_text}' was not found.",
        ).to_be_visible()
        label.scroll_into_view_if_needed()
        label.click()

        checkbox = CheckBox.__checkbox_locator(scope, label_text)
        expect(
            checkbox,
            f"Checkbox '{label_text}' did not reach selected={selected}.",
        ).to_be_checked(checked=selected)

        ComponentUtils.wait_for_appian_action_completed(scope)
