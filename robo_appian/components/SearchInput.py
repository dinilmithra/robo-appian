"""Generic helpers for search-input interaction and result synchronization."""

import logging
from typing import Optional

from playwright.sync_api import Page, expect, Locator
from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)


class SearchInput:
    """Choose exact values from dynamic Appian search-input suggestions.

    Use these helpers for Appian picker fields that render a suggestion list
    after keyboard input. Callers may identify a picker by accessible name or
    placeholder, or provide a locator resolved inside another component.
    """

    @staticmethod
    def get_section_container(
        page: Page, header_text: str, field_label: str
    ) -> Locator:
        """Find the nearest visible section containing a heading and field.

        Args:
            page: Appian page containing the picker field.
            header_text: Unique heading for the section to search.
            field_label: Exact label of the field within that section.

        Returns:
            A visible locator that scopes both the heading and field.

        Raises:
            AssertionError: If the shared section container does not become
                visible within the configured Playwright timeout.
        """
        # Single XPath: find the nearest common ancestor of the section header text
        # and the target field label text, without using CSS classes.
        header_text_xpath = ComponentUtils.xpath_literal(header_text)
        field_label_xpath = ComponentUtils.xpath_literal(field_label)

        common_root_xpath = (
            "(//*[normalize-space(text())="
            + header_text_xpath
            + "])[1]/ancestor::*[.//*[normalize-space(text())="
            + field_label_xpath
            + "]][1]"
        )

        section_container = page.locator(f"xpath={common_root_xpath}")
        expect(section_container).to_be_visible()
        return section_container

    @staticmethod
    def __find_lookup(
        page: Page,
        accessible_name: Optional[str] = None,
        placeholder_text: Optional[str] = None,
        section_name: Optional[str] = None,
    ) -> Locator:
        """
        Finds the visible Appian picker input by accessible name or placeholder.
        """
        if bool(accessible_name) == bool(placeholder_text):
            raise ValueError("Provide exactly one accessible name or placeholder text.")

        field_identifier = placeholder_text or accessible_name

        search_scope = (
            SearchInput.get_section_container(
                page=page,
                header_text=section_name,
                field_label=field_identifier,
            )
            if section_name
            else page
        )

        if placeholder_text:
            placeholder_literal = ComponentUtils.xpath_literal(placeholder_text)
            lookup_candidates = search_scope.locator(
                "xpath=.//input[@role='combobox' and @placeholder="
                + placeholder_literal
                + "]"
            ).filter(visible=True)
        else:
            lookup_candidates = search_scope.get_by_role(
                "combobox", name=accessible_name, exact=True
            ).filter(visible=True)

        lookup = lookup_candidates.first
        expect(lookup).to_be_visible()
        # Wait until re-rendering settles and the field is interactable.
        expect(lookup).to_be_enabled()

        if not lookup.get_attribute("aria-labelledby"):
            raise AssertionError(
                f"SearchInput '{field_identifier}' does not expose aria-labelledby."
            )
        if not lookup.get_attribute("aria-controls"):
            raise AssertionError(
                f"SearchInput '{field_identifier}' does not expose aria-controls."
            )

        return lookup

    @staticmethod
    def select(
        page: Page,
        accessible_name: Optional[str] = None,
        placeholder_text: Optional[str] = None,
        search_text: str = "",
        section_name: Optional[str] = None,
        use_typing_delay: bool = True,
        typing_delay: int = 50,
    ) -> None:
        """Replace a picker value and choose its exact matching suggestion.

        Use this for a visible Appian picker identified by accessible name or
        placeholder. Supply ``section_name`` when duplicate field labels exist.
        Keyboard events are used to trigger suggestions; the optional delay can
        be disabled or adjusted for a particular picker.

        Args:
            page: Appian page containing the picker.
            accessible_name: Accessible field name used by Playwright's
                role-based locator.
            placeholder_text: Exact placeholder used to identify the picker
                when it does not have a suitable accessible name.
            search_text: Text that must exactly match the option to select.
            section_name: Optional heading used to scope a duplicate field.
            use_typing_delay: Whether to pause between keyboard events.
            typing_delay: Delay in milliseconds between characters when enabled.

        Raises:
            ValueError: If ``search_text`` is empty or exactly one of
                ``accessible_name`` and ``placeholder_text`` is not supplied.
            Exception: If the picker has no suggestion list or no exact match.
            AssertionError: If the picker, list, or matching option does not
                become available within the configured Playwright timeout.
        """
        field_name = placeholder_text or accessible_name or "SearchInput"
        logger.info("Search input selection starting: field='%s'.", field_name)

        # Resolve the component, then delegate to the shared locator-based selection logic.
        lookup = SearchInput.__find_lookup(
            page=page,
            accessible_name=accessible_name,
            section_name=section_name,
            placeholder_text=placeholder_text,
        )
        SearchInput.select_by_locator(
            page=page,
            lookup=lookup,
            search_text=search_text,
            field_name=field_name,
            use_typing_delay=use_typing_delay,
            typing_delay=typing_delay,
        )
        logger.info("Search input selection completed: field='%s'.", field_name)

    @staticmethod
    def select_by_locator(
        page: Page,
        lookup: Locator,
        search_text: str,
        field_name: str = "SearchInput",
        use_typing_delay: bool = True,
        typing_delay: int = 50,
    ) -> None:
        """Replace and select a value in an already-resolved Appian picker.

        Use this when a container helper has already located a picker in a table,
        dialog, or section. Existing text is cleared, keyboard input triggers
        suggestions, and the option must exactly equal ``search_text``.

        Args:
            page: Appian page that owns the picker's suggestion list.
            lookup: Visible picker input locator.
            search_text: Text that must exactly match the option to select.
            field_name: Human-readable field name used in failure messages.
            use_typing_delay: Whether to pause between keyboard events.
            typing_delay: Delay in milliseconds between characters when enabled.

        Raises:
            ValueError: If ``search_text`` is empty.
            Exception: If the picker has no suggestion list or no exact match.
            AssertionError: If the picker, list, or matching option does not
                become available within the configured Playwright timeout.
        """
        if not str(search_text or "").strip():
            raise ValueError("Search text cannot be empty or whitespace.")

        expect(lookup, f"SearchInput '{field_name}' was not visible.").to_be_visible()
        expect(lookup, f"SearchInput '{field_name}' was not enabled.").to_be_enabled()
        expect(
            lookup,
            f"SearchInput '{field_name}' was not a combobox.",
        ).to_have_attribute("role", "combobox")

        label_id = lookup.get_attribute("aria-labelledby")
        if not label_id:
            raise AssertionError(
                f"SearchInput '{field_name}' does not expose aria-labelledby."
            )

        listbox_id = lookup.get_attribute("aria-controls")
        if not listbox_id:
            raise AssertionError(
                f"SearchInput '{field_name}' does not expose aria-controls."
            )

        lookup.click()

        # Replace any existing picker value before entering the new search criteria.
        lookup.press("Control+A")
        lookup.press("Backspace")

        # Appian picker searches are triggered reliably by keyboard input events.
        delay = max(0, typing_delay) if use_typing_delay else 0
        lookup.press_sequentially(str(search_text).strip(), delay=delay)

        # Each Appian picker identifies its own dynamically rendered suggestion list.
        listbox_id_literal = ComponentUtils.xpath_literal(listbox_id)
        listbox = (
            page.locator(
                "xpath=//*[@role='listbox' and @id=" + listbox_id_literal + "]"
            )
            .filter(visible=True)
            .first
        )
        expect(listbox).to_be_visible()

        visible_options = listbox.get_by_role("option").filter(visible=True)
        expect(
            visible_options.first,
            f"SearchInput '{field_name}' did not render any suggestions.",
        ).to_be_visible()

        no_results_locator = listbox.get_by_role(
            "option",
            name="No results found",
            exact=True,
        )
        if no_results_locator.filter(visible=True).count() > 0:
            raise Exception(
                f"No lookup matches found for '{search_text}' in '{field_name}'. "
                "Verify the entered value and the current form selections."
            )

        option_locator = (
            listbox.get_by_role("option", name=str(search_text).strip(), exact=True)
            .filter(visible=True)
            .first
        )
        expect(option_locator).to_be_visible()
        option_locator.click()
        expect(
            listbox,
            f"SearchInput '{field_name}' suggestion list remained visible.",
        ).to_be_hidden()
