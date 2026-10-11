"""Appian textbox component abstraction."""

from __future__ import annotations

from robo_appian.utils.ComponentUtils import ComponentUtils

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
        visible: bool | str | None = True,
        timeout: float | int | None = None,
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

        super().__init__(page=page, timeout=timeout)
        self._label = normalized_label
        self._placeholder = normalized_placeholder
        self._header = normalized_header
        self._exact = exact
        self._scope = scope
        self._visible = ComponentUtils.normalize_visibility(visible)

    @property
    def visible(self) -> bool | None:
        """Return the visibility constraint used to resolve this component."""
        return self._visible

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
            "((self::input and (((@type='text' or @type='password') and "
            f"not(@data-testid='{self.DATE_TEST_ID}')) or "
            "(@role='combobox' and @aria-autocomplete='list' and @aria-controls))) or "
            "(self::textarea and @role='textbox'))"
        )

    def _accessible_name_locator(self) -> Locator:
        """Resolve this textbox by its accessible name."""
        assert self._label is not None
        root = self._scope.locator if self._scope is not None else self._page
        textbox = root.get_by_role(
            "textbox", name=self._label, exact=self._exact
        ).locator("xpath=self::*[" + self._control_predicate() + "]")
        if textbox.count() > 0:
            return textbox.first

        # Appian searchable text inputs expose role=combobox while remaining
        # text-entry controls. Restrict this fallback to actual input elements
        # with list autocomplete so dropdown/listbox widgets are not captured.
        return (
            root.get_by_role("combobox", name=self._label, exact=self._exact)
            .locator("xpath=self::input[@aria-autocomplete='list' and @aria-controls]")
            .first
        )

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
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed
        if self._label is not None:
            return self._locator_by_label()
        if self._placeholder is not None:
            return self._locator_by_placeholder()
        return self._locator_by_header()

    def _visible_locator(self) -> Locator:
        locator = self._locator()
        if self._visible is not None:
            locator = locator.filter(visible=self._visible)
        return locator.first

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

    @staticmethod
    def _is_searchable(textbox: Locator) -> bool:
        """Return whether a textbox exposes semantic search suggestions."""
        return (
            textbox.get_attribute("role") == "combobox"
            and textbox.get_attribute("aria-autocomplete") == "list"
            and bool(textbox.get_attribute("aria-controls"))
        )

    def fill(self, value: object) -> "AppianTextbox":
        """Replace the textbox value and return this component for chaining.

        Searchable Appian textboxes are entered with keyboard events and retain
        focus so a following ``select(...)`` can choose from their suggestions.
        Ordinary textboxes preserve the normal blur-and-wait Appian lifecycle.
        """
        textbox = self._wait_until_ready_locator()
        text = "" if value is None else str(value)
        if self._is_searchable(textbox):
            textbox.click(**self._timeout_kwargs())
            textbox.press("Control+A")
            textbox.press("Backspace")
            if text:
                textbox.press_sequentially(text, delay=50)
        else:
            textbox.fill(text, **self._timeout_kwargs())
            self._after_fill(textbox)
        logger.info("Filled Appian textbox: %s.", self._description())
        return self

    def _after_fill(self, textbox: Locator) -> None:
        """Commit the changed ordinary textbox value by moving focus away."""
        self._after_change(textbox)

    def select(
        self,
        value: str | None = None,
        *,
        search_text: str | None = None,
        index: int | None = None,
        exact: bool = True,
        timeout: float | int | None = None,
    ) -> "AppianTextbox":
        """Select a suggestion from a searchable Appian textbox.

        ``value`` selects a suggestion by displayed text. ``index`` selects a
        suggestion by 1-based position. They are mutually exclusive. When
        ``search_text`` is supplied, it is entered before the selection; omit it
        after chaining from ``fill(...)``.
        """
        if (value is None) == (index is None):
            raise ValueError("Specify exactly one of 'value' or 'index'.")
        if index is not None and (
            isinstance(index, bool) or not isinstance(index, int) or index < 1
        ):
            raise ValueError(
                "Textbox suggestion index must be an integer of 1 or greater."
            )
        if value is not None and not str(value).strip():
            raise ValueError("Textbox suggestion value cannot be empty or whitespace.")
        if search_text is not None and not str(search_text).strip():
            raise ValueError("search_text cannot be empty or whitespace.")

        if search_text is not None:
            self.fill(search_text)

        textbox = self._wait_until_ready_locator()
        if not self._is_searchable(textbox):
            raise ValueError(
                f"Textbox {self._description()} does not expose searchable suggestions."
            )

        listbox_id = textbox.get_attribute("aria-controls")
        assert listbox_id is not None
        listbox_literal = self._xpath_literal(listbox_id)
        listbox = (
            self._page.locator(
                "xpath=//*[@role='listbox' and @id=" + listbox_literal + "]"
            )
            .filter(visible=True)
            .first
        )
        timeout_kwargs = self._timeout_kwargs(timeout)
        expect(
            listbox,
            f"Suggestion list for textbox {self._description()} was not visible.",
        ).to_be_visible(**timeout_kwargs)

        options = listbox.get_by_role("option").filter(visible=True)
        expect(
            options.first, f"Textbox {self._description()} did not render suggestions."
        ).to_be_visible(**timeout_kwargs)

        no_results = listbox.get_by_role(
            "option", name="No results found", exact=True
        ).filter(visible=True)
        if no_results.count() > 0:
            raise LookupError(
                f"No suggestions were found for textbox {self._description()}."
            )

        if index is not None:
            count = options.count()
            if index > count:
                raise IndexError(
                    f"Textbox {self._description()} suggestion index {index} is out of range; "
                    f"{count} visible suggestion(s) were available."
                )
            option = options.nth(index - 1)
        else:
            option = (
                listbox.get_by_role("option", name=str(value).strip(), exact=exact)
                .filter(visible=True)
                .first
            )

        expect(
            option, f"Textbox {self._description()} suggestion was not visible."
        ).to_be_visible(**timeout_kwargs)
        option.click(**timeout_kwargs)
        self._page.wait_for_appian_action_completed(timeout=timeout or self._timeout)
        logger.info("Selected Appian textbox suggestion: %s.", self._description())
        return self

    def clear(self) -> None:
        """Wait until the textbox is ready, then clear its value."""
        self.fill("")

    def click(self) -> None:
        """Wait until the textbox is ready, then click it."""
        self._wait_until_ready_locator().click(**self._timeout_kwargs())

    def is_visible(self) -> bool:
        """Return whether the textbox is currently visible."""
        return self._locator().is_visible()

    def is_disabled(self) -> bool:
        """Return whether the textbox is currently disabled."""
        return self._visible_locator().get_attribute("disabled") is not None

    def is_enabled(self, timeout: float | int | None = None) -> bool:
        """Return whether the textbox is enabled, optionally waiting.

        Omitting ``timeout`` performs an immediate state query. Supplying a
        positive timeout in seconds waits up to that duration and returns
        ``False`` if the textbox never becomes enabled.
        """
        textbox = self._visible_locator()
        if timeout is None:
            if textbox.count() == 0:
                return False
            return textbox.get_attribute("disabled", timeout=0) is None

        try:
            expect(
                textbox,
                f"Textbox {self._description()} did not become enabled.",
            ).to_be_enabled(**ComponentUtils.timeout_kwargs(timeout))
            return True
        except AssertionError:
            return False

    def value(self) -> str:
        """Return the textbox's current value."""
        return self._visible_locator().input_value()

    def _wait_until_ready_locator(self) -> Locator:
        textbox = self._visible_locator()
        expect(
            textbox,
            f"Textbox {self._description()} was not visible.",
        ).to_be_visible(**self._timeout_kwargs())
        expect(
            textbox,
            f"Textbox {self._description()} was not enabled.",
        ).to_be_enabled(**self._timeout_kwargs())
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
