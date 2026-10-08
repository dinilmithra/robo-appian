"""Appian textbox component abstraction."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from .appian_input_component import AppianInputComponent

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage

logger = logging.getLogger(__name__)


class AppianTextbox(AppianInputComponent):
    """Represent an Appian text field bound to a page."""

    DATE_TEST_ID = "DatePickerWidget-textInput"

    def __init__(
        self,
        *,
        page: "AppianPage",
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        scope: "AppianLocator | None" = None,
    ) -> None:
        normalized_label = self._normalize_optional(label)
        normalized_placeholder = self._normalize_optional(placeholder)
        normalized_header = self._normalize_optional(header)

        identifiers = (normalized_label, normalized_placeholder, normalized_header)
        if sum(value is not None for value in identifiers) != 1:
            raise ValueError(
                "Specify exactly one of 'label', 'placeholder', or 'header' "
                "for a textbox."
            )

        super().__init__(page=page)
        self._label = normalized_label
        self._placeholder = normalized_placeholder
        self._header = normalized_header
        self._exact = exact
        self._scope = scope

    @staticmethod
    def _normalize_optional(value: str | None) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Textbox identifier cannot be empty or whitespace.")
        return " ".join(value.split())

    @staticmethod
    def _xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        literals: list[str] = []
        for index, part in enumerate(parts):
            if part:
                literals.append(f"'{part}'")
            if index < len(parts) - 1:
                literals.append('"\'"')
        return f"concat({', '.join(literals)})"

    @staticmethod
    def _normalized_xpath(expression: str) -> str:
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return (
            "translate("
            "normalize-space(translate(" + expression + ", '\u00a0', ' ')), "
            f"'{lowercase}', '{uppercase}')"
        )

    def _root_locator(self, selector: str) -> Locator:
        if self._scope is not None:
            return self._scope.locator.locator(selector)
        return self._page.locator(selector)

    def _comparison(self, expression: str, value: str) -> str:
        normalized = self._normalized_xpath(expression)
        expected = self._xpath_literal(value.upper())
        if self._exact:
            return f"{normalized} = {expected}"
        return f"contains({normalized}, {expected})"

    def _control_predicate(self) -> str:
        """Return the XPath predicate that identifies this component type."""
        return (
            "((self::input and (@type='text' or @type='password') and "
            f"not(@data-testid='{self.DATE_TEST_ID}')) or "
            "(self::textarea and @role='textbox'))"
        )

    def _accessible_name_locator(self) -> Locator:
        """Resolve this textbox by its accessible name."""
        assert self._label is not None
        if self._scope is not None:
            locator = self._scope.locator.get_by_role(
                "textbox",
                name=self._label,
                exact=self._exact,
            ).first
        else:
            locator = self._page.get_by_role(
                "textbox",
                name=self._label,
                exact=self._exact,
            ).first
        return locator.locator("xpath=self::*[" + self._control_predicate() + "]").first

    def _locator_by_label(self) -> Locator:
        assert self._label is not None
        label_xpath = (
            "xpath=(.//label[@for and "
            f"({self._comparison('string(.)', self._label)})])[1]"
        )
        label = self._root_locator(label_xpath)

        if label.count() > 0:
            input_id = label.first.get_attribute("for")
            if input_id:
                input_id_literal = self._xpath_literal(input_id)
                linked = self._root_locator(
                    "xpath=(.//*[("
                    f"{self._control_predicate()}"
                    ") and "
                    f"@id={input_id_literal}])[1]"
                )
                return linked

        # Some Appian layouts expose the field name through accessibility
        # semantics even when there is no usable label[for] relationship.
        # Resolve the textbox by its accessible name instead of matching
        # arbitrary visible text, which may also occur in tables or headings.
        return self._accessible_name_locator()

    def _locator_by_placeholder(self) -> Locator:
        assert self._placeholder is not None
        predicate = self._comparison("@placeholder", self._placeholder)
        return self._root_locator(
            "xpath=(.//*[("
            f"{self._control_predicate()}"
            ") and @placeholder and "
            f"({predicate})])[1]"
        )

    def _locator_by_header(self) -> Locator:
        """Resolve the first supported textbox following semantic header text."""
        assert self._header is not None
        header_comparison = self._comparison("string(.)", self._header)
        header_xpath = (
            "xpath=(.//*[(self::strong or self::h1 or self::h2 or self::h3 "
            "or self::h4 or self::h5 or self::h6 or @role='heading') and "
            f"({header_comparison})])[1]"
        )
        header = self._root_locator(header_xpath)
        if header.count() == 0:
            return self._root_locator("xpath=(.//*[false()])[1]")

        return header.first.locator(
            "xpath=(following::*[" + self._control_predicate() + "])[1]"
        ).first

    def _locator(self) -> Locator:
        if self._label is not None:
            return self._locator_by_label()
        if self._placeholder is not None:
            return self._locator_by_placeholder()
        return self._locator_by_header()

    def _visible_locator(self) -> Locator:
        return self._locator().filter(visible=True).first

    @property
    def label(self) -> str | None:
        """Return the label used to identify this textbox, when applicable."""
        return self._label

    @property
    def placeholder(self) -> str | None:
        """Return the placeholder used to identify this textbox, when applicable."""
        return self._placeholder

    @property
    def header(self) -> str | None:
        """Return the header text used to identify this textbox, when applicable."""
        return self._header

    def fill(self, value: object) -> None:
        """Wait until the textbox is ready, then replace its value."""
        textbox = self._wait_until_ready_locator()
        textbox.fill("" if value is None else str(value))
        self._after_fill(textbox)
        logger.info("Filled Appian textbox: %s.", self._description())

    def _after_fill(self, textbox: Locator) -> None:
        """Commit the changed textbox value by moving focus away."""
        self._after_change(textbox)

    def clear(self) -> None:
        """Wait until the textbox is ready, then clear its value."""
        self.fill("")

    def click(self) -> None:
        """Wait until the textbox is ready, then click it."""
        self._wait_until_ready_locator().click()

    def is_visible(self) -> bool:
        """Return whether the textbox is currently visible."""
        return self._locator().is_visible()

    def is_disabled(self) -> bool:
        """Return whether the textbox is currently disabled."""
        return self._visible_locator().get_attribute("disabled") is not None

    def is_enabled(self) -> bool:
        """Return whether the textbox is currently enabled."""
        return not self.is_disabled()

    def value(self) -> str:
        """Return the textbox's current value."""
        return self._visible_locator().input_value()

    def _wait_until_ready_locator(self) -> Locator:
        textbox = self._visible_locator()
        expect(
            textbox,
            f"Textbox {self._description()} was not visible.",
        ).to_be_visible()
        expect(
            textbox,
            f"Textbox {self._description()} was not enabled.",
        ).to_be_enabled()
        return textbox

    def wait_until_ready(self) -> "AppianTextbox":
        """Wait until the textbox is visible and enabled, then return it."""
        self._wait_until_ready_locator()
        return self

    def _description(self) -> str:
        if self._label is not None:
            return f"with label '{self._label}'"
        if self._placeholder is not None:
            return f"with placeholder '{self._placeholder}'"
        return f"after header '{self._header}'"


__all__ = ["AppianTextbox"]
