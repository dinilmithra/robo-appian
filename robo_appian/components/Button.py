"""Generic button interaction utilities."""

import logging
import re
from typing import Mapping, Optional, Union

from playwright.sync_api import Locator, Page, expect

from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)

Scope = Union[Page, Locator]


class Button:
    """Reusable operations for native HTML button controls."""

    @staticmethod
    def is_visible(
        scope: Scope,
        label: str,
        exact: bool = True,
    ) -> bool:
        """Return whether a matching native HTML button is visible."""
        if not label or not label.strip():
            return False

        button = Button._button_wait_locator(
            scope,
            label,
            exact=exact,
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
        exact: bool = True,
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
        input_value = normalized_xpath("@value")

        if exact:
            compare = lambda expr: f"{expr} = {expected}"
        else:
            compare = lambda expr: f"contains({expr}, {expected})"

        # For <button>, match either the full normalized text/accessibility
        # metadata or any descendant's normalized text. The descendant branch
        # is important for Appian buttons whose visible label is nested inside
        # spans while extra accessibility text is also present.
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

        input_predicate = " or ".join(
            [
                compare(input_value),
                compare(aria_label),
                compare(title),
                compare(data_label),
            ]
        )

        xpath = (
            "xpath=(.//button[" + button_predicate + "]"
            " | .//input["
            "(@type='button' or @type='submit' or @type='reset') and ("
            + input_predicate
            + ")])[1]"
        )

        return scope.locator(xpath)

    @staticmethod
    def wait_until_ready(
        scope: Scope,
        label: str,
        exact: bool = True,
    ) -> Locator:
        """Wait using Playwright auto-waiting until a button is actionable.

        The XPath locator is live: if Appian removes and recreates the button
        during a SAIL rerender, Playwright re-evaluates the locator until the
        current element is visible and enabled. No manual polling or sleeps are
        required.
        """
        button = (
            Button._button_wait_locator(
                scope,
                label,
                exact=exact,
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
            f"Button '{label}' was visible but not enabled.",
        ).to_be_enabled()

        return button

    @staticmethod
    def click_with_attributes(
        scope: Scope,
        label: str,
        attributes: Mapping[str, Optional[str]],
        exact: bool = True,
    ) -> None:
        """Wait for and click a native button matching HTML attributes.

        This method is useful when a page renders duplicate buttons with the
        same label. An attribute value of ``None`` means that the attribute
        must be present; another value requires an exact attribute match.

        Args:
            scope: Page or locator used to resolve the button.
            label: Accessible or rendered button label.
            attributes: HTML attribute constraints used to disambiguate the
                button. Values of ``None`` require attribute presence.
            exact: Whether the normalized button text must match the label.

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
            if exact
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
        exact: bool = True,
    ) -> None:
        """Wait for a native HTML button to be actionable, then click it."""
        logger.info("Before button click: label='%s'.", label)

        button = Button.wait_until_ready(
            scope,
            label,
            exact=exact,
        )

        ComponentUtils.click(button)

        logger.info("After button click: label='%s'.", label)

    @staticmethod
    def wait_until_hidden(
        scope: Scope,
        label: str,
        exact: bool = True,
    ) -> None:
        """Wait until a matching native button is hidden or detached."""
        button = Button._button_wait_locator(
            scope,
            label,
            exact=exact,
        )

        expect(
            button,
            f"Button '{label}' remained visible.",
        ).to_be_hidden()
