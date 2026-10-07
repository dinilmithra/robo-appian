"""Generic button interaction utilities."""

import logging
import re
from typing import Mapping, Optional

from playwright.sync_api import Locator, expect
from robo_automation import Scope

from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)



class Button:
    """Reusable operations for Appian button controls."""

    @staticmethod
    def is_visible(
        scope: Scope,
        label: str,
        excat_match: bool = False,
    ) -> bool:
        """Return whether a matching Appian button control is visible.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible label used to identify the control.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            bool: ``True`` when a matching Appian button control is visible; otherwise ``False``.
        """
        if not label or not label.strip():
            return False

        button = Button._button_wait_locator(
            scope,
            label,
            excat_match=excat_match,
        )

        return button.is_visible()

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """Return an XPath-safe string literal."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def _button_wait_locator(
        scope: Scope,
        label: str,
        excat_match: bool = False,
    ) -> Locator:
        """Build a live XPath locator for a native button label.

        Appian often pads visible labels with non-breaking spaces and may add
        accessibility-only spans. XPath text normalization does not treat NBSP
        as regular whitespace, so NBSP is translated to a normal space before
        comparison. Matching is case-insensitive.
        """
        if not label or not label.strip():
            raise ValueError("Button label cannot be empty or whitespace.")

        normalized = " ".join(label.split()).upper()
        expected = Button._xpath_literal(normalized)

        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"

        # Convert NBSP to a regular space, normalize whitespace, then convert
        # ASCII lowercase characters to uppercase for case-insensitive matching.
        def normalized_xpath(expression: str) -> str:
            """Build an XPath expression that normalizes text for comparison."""

            return (
                "translate("
                "normalize-space(translate(" + expression + ", '\u00a0', ' ')), "
                f"'{lowercase}', '{uppercase}')"
            )

        button_text = normalized_xpath("string(.)")
        aria_label = normalized_xpath("@aria-label")
        title = normalized_xpath("@title")
        data_label = normalized_xpath("@data-owl-test-label")
        if excat_match:
            compare = lambda expr: f"{expr} = {expected}"
        else:
            compare = lambda expr: f"contains({expr}, {expected})"

        # Appian action buttons are native <button type="button"> elements.
        # Match their rendered/accessibility label while requiring that DOM
        # contract. Disabled state is intentionally not part of identity.
        descendant_text = normalized_xpath("string(.)")
        button_predicate = " or ".join(
            [
                compare(button_text),
                compare(aria_label),
                compare(title),
                compare(data_label),
                f".//*[{compare(descendant_text)}]",
            ]
        )

        xpath = (
            "xpath=(.//button[@type='button' and ("
            + button_predicate
            + ")])[1]"
        )

        return scope.locator(xpath)

    @staticmethod
    def wait_until_ready(
        scope: Scope,
        label: str,
        excat_match: bool = False,
    ) -> Locator:
        """Wait using browser automation auto-waiting until a button is actionable.

        The XPath locator is live: if Appian removes and recreates the button
        during a SAIL rerender, browser automation re-evaluates the locator until the
        current element is visible and enabled. No manual polling or sleeps are
        required.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible label used to identify the control.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            Locator: The visible and enabled Appian button locator.
        """
        button = (
            Button._button_wait_locator(
                scope,
                label,
                excat_match=excat_match,
            )
            .filter(visible=True)
            .first
        )

        expect(
            button,
            f"Button '{label}' was not rendered and visible.",
        ).to_be_visible()

        expect(
            button,
            f"Button '{label}' was visible but remained disabled.",
        ).not_to_have_attribute("disabled", re.compile(".*"))

        return button

    @staticmethod
    def click_with_attributes(
        scope: Scope,
        label: str,
        attributes: Mapping[str, Optional[str]],
        excat_match: bool = False,
    ) -> None:
        """Wait for and click an Appian button control matching HTML attributes.

        This method is useful when a scope renders duplicate buttons with the
        same label. An attribute value of ``None`` means that the attribute
        must be present; another value requires an exact attribute match.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Accessible or rendered button label.
            attributes: HTML attribute constraints used to disambiguate the
                button. Values of ``None`` require attribute presence.
            excat_match: Whether the normalized button text must match the label.

        Raises:
            ValueError: If the label or an attribute name is empty or invalid.
            AssertionError: If no matching button becomes visible and enabled.
        """
        if not label or not label.strip():
            raise ValueError("Button label cannot be empty or whitespace.")

        attribute_predicates = []
        for attribute_name, attribute_value in attributes.items():
            if not re.fullmatch(r"[A-Za-z_:][A-Za-z0-9_.:-]*", attribute_name):
                raise ValueError(f"Invalid HTML attribute name: {attribute_name}")
            if attribute_value is None:
                attribute_predicates.append(f"@{attribute_name}")
            else:
                escaped_value = Button._xpath_literal(str(attribute_value))
                attribute_predicates.append(f"@{attribute_name}={escaped_value}")

        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        expected = Button._xpath_literal(" ".join(label.split()).upper())
        normalized_text = (
            "translate(normalize-space(translate(string(.), "
            "'\u00a0', ' ')), "
            f"'{lowercase}', '{uppercase}')"
        )
        label_predicate = (
            f"{normalized_text} = {expected}"
            if excat_match
            else f"contains({normalized_text}, {expected})"
        )
        predicates = attribute_predicates + [label_predicate]
        button = (
            scope.locator("xpath=(.//button[" + " and ".join(predicates) + "])[1]")
            .filter(visible=True)
            .first
        )

        expect(
            button, f"Button '{label}' was not rendered and visible."
        ).to_be_visible()
        expect(button, f"Button '{label}' was visible but not enabled.").to_be_enabled()
        logger.info("Before button click: label='%s'.", label)
        ComponentUtils.click(button)
        logger.info("After button click: label='%s'.", label)

    @staticmethod
    def click(
        scope: Scope,
        label: str,
        excat_match: bool = False,
    ) -> None:
        """Wait for an Appian button control to be actionable, then click it.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible label used to identify the control.
            excat_match: Whether matching must use the complete label or text.
        """
        logger.info("Before button click: label='%s'.", label)

        button = Button.wait_until_ready(
            scope,
            label,
            excat_match=excat_match,
        )

        ComponentUtils.click(button)

        logger.info("After button click: label='%s'.", label)

    @staticmethod
    def wait_until_hidden(
        scope: Scope,
        label: str,
        excat_match: bool = False,
    ) -> None:
        """Wait until a matching Appian button control is hidden or detached.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible label used to identify the control.
            excat_match: Whether matching must use the complete label or text.
        """
        button = Button._button_wait_locator(
            scope,
            label,
            excat_match=excat_match,
        )

        expect(
            button,
            f"Button '{label}' remained visible.",
        ).to_be_hidden()
