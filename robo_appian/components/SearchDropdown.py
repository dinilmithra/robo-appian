"""Generic helpers for interacting with searchable Appian dropdown controls.

Keep application-specific labels, values, and workflow decisions outside this module.
"""

from typing import Optional

from playwright.sync_api import Page, expect

from robo_appian.components.Dropdown import Dropdown
from robo_appian.components.InputText import InputText
from robo_appian.utils.ComponentUtils import ComponentUtils


class SearchDropdown:
    """Select and inspect values in searchable Appian dropdown widgets."""

    @staticmethod
    def select(
        page: Page,
        accessible_name: str,
        option_text: str,
        exact_label: bool = True,
        timeout: Optional[float] = None,
    ) -> None:
        """Search for and click an option in a labeled Appian combobox.

        The exact accessible-name match is opened. Its ``aria-controls``
        relation identifies the listbox, and the listbox container's native
        ``Search`` label identifies the filter input.

        Args:
            page: Appian page containing the searchable dropdown.
            accessible_name: Accessible combobox name to match.
            option_text: Option name to search for and select.
            exact_label: When True, require the rendered Appian label to match
                exactly. When False, also accept Appian's trailing required
                marker variants (``Label*`` and ``Label *``).
            timeout: Optional timeout in seconds for dropdown/listbox/search/option
                visibility and final selection assertions. When omitted,
                Playwright's configured expectation timeout is used.

        Raises:
            AssertionError: If required ARIA linkage is missing or the combobox,
                listbox, or option does not become available.
        """
        normalized_name = str(accessible_name or "").strip()
        normalized_option = str(option_text or "").strip()
        timeout_ms = None if timeout is None else max(0.0, float(timeout)) * 1000

        def _expect_visible(locator, message: str | None = None) -> None:
            assertion = expect(locator, message) if message else expect(locator)
            if timeout_ms is None:
                assertion.to_be_visible()
            else:
                assertion.to_be_visible(timeout=timeout_ms)

        def _expect_hidden(locator) -> None:
            assertion = expect(locator)
            if timeout_ms is None:
                assertion.to_be_hidden()
            else:
                assertion.to_be_hidden(timeout=timeout_ms)

        def _expect_attribute(locator, name: str, value: str) -> None:
            assertion = expect(locator)
            if timeout_ms is None:
                assertion.to_have_attribute(name, value)
            else:
                assertion.to_have_attribute(name, value, timeout=timeout_ms)

        def _expect_contains_text(locator, value: str) -> None:
            assertion = expect(locator)
            if timeout_ms is None:
                assertion.to_contain_text(value)
            else:
                assertion.to_contain_text(value, timeout=timeout_ms)
        if not normalized_name:
            raise ValueError(
                "Search dropdown accessible name cannot be empty or whitespace."
            )
        if not normalized_option:
            raise ValueError("Search dropdown option cannot be empty or whitespace.")

        # Reuse Dropdown's XPath label-to-aria-labelledby relationship.
        # Dropdown centrally handles Appian's optional trailing required
        # marker, so SearchDropdown does not maintain a second label rule.
        dropdown = (
            Dropdown._dropdown_locator(
                page,
                normalized_name,
                exact=True,
                allow_required_marker=not exact_label,
            )
            .filter(visible=True)
            .first
        )
        _expect_visible(
            dropdown,
            f"Search dropdown '{normalized_name}' was not visible.",
        )

        if dropdown.get_attribute("aria-expanded") != "true":
            if timeout_ms is None:
                dropdown.click()
            else:
                dropdown.click(timeout=timeout_ms)

        _expect_attribute(dropdown, "aria-expanded", "true")

        aria_labelledby = dropdown.get_attribute("aria-labelledby")
        if not aria_labelledby:
            raise AssertionError(
                f"Search dropdown '{normalized_name}' does not have an "
                "aria-labelledby attribute."
            )

        listbox_id = dropdown.get_attribute("aria-controls")
        if not listbox_id:
            raise AssertionError(
                f"Search dropdown '{normalized_name}' does not have an "
                "aria-controls attribute."
            )

        label_id_literal = ComponentUtils.xpath_literal(f" {aria_labelledby} ")
        listbox_id_literal = ComponentUtils.xpath_literal(listbox_id)
        listbox = (
            page.locator(
                "xpath=//*[@role='listbox' and @id="
                + listbox_id_literal
                + " and contains(concat(' ', normalize-space(@aria-labelledby), ' '), "
                + label_id_literal
                + ")]"
            )
            .filter(visible=True)
            .first
        )
        _expect_visible(listbox)

        dropdown_panel = listbox.locator("xpath=parent::*")
        search_input = (
            dropdown_panel.get_by_label("Search", exact=True).filter(visible=True).first
        )
        _expect_visible(search_input)
        InputText.fill_by_locator(search_input, normalized_option)

        visible_options = listbox.get_by_role("option").filter(visible=True)
        _expect_visible(visible_options.first)
        option = (
            listbox.get_by_role("option", name=normalized_option, exact=True)
            .filter(visible=True)
            .first
        )
        _expect_visible(option)
        if timeout_ms is None:
            option.click()
        else:
            option.click(timeout=timeout_ms)
        _expect_hidden(listbox)
        _expect_attribute(dropdown, "aria-expanded", "false")
        _expect_contains_text(dropdown, normalized_option)

    @staticmethod
    def verify_selected_value(
        page: Page,
        accessible_name: str,
        expected_value: str,
        exact: bool = True,
    ) -> None:
        """Wait until a visible dropdown displays the expected rendered text.

        Args:
            page: Appian page containing the dropdown.
            accessible_name: Accessible combobox name.
            expected_value: Text expected inside the selected dropdown.
            exact: Whether ``accessible_name`` must exactly match; this does
                not change the rendered-value assertion.
        """
        normalized_name = str(accessible_name or "").strip()
        if not normalized_name:
            raise ValueError(
                "Search dropdown accessible name cannot be empty or whitespace."
            )

        dropdown = Dropdown._get_dropdown(
            page,
            normalized_name,
            exact=exact,
        )

        expect(
            dropdown,
            f"Validation Failed: Dropdown '{accessible_name}' does not display "
            f"'{expected_value}'",
        ).to_have_text(expected_value)

    @staticmethod
    def check_dropdown_state(page: Page, label_text: str) -> str:
        """Immediately classify a label-linked field's editability.

        Use this inside caller-owned retry logic when Appian may still be
        rerendering. All missing-label, missing-linkage, and lookup errors are
        represented as ``Label or ID Not Found`` rather than raised.

        Args:
            page: Appian page containing the field label.
            label_text: Exact visible label text to inspect.

        Returns:
            ``EDITABLE``, ``READ_ONLY``, or ``Label or ID Not Found``.
        """
        if not label_text or not label_text.strip():
            return "Label or ID Not Found"

        try:
            safe_label_text = ComponentUtils.xpath_literal(label_text.strip())
            label_locator = (
                page.locator(f"xpath=//*[@id and normalize-space(.)={safe_label_text}]")
                .filter(visible=True)
                .first
            )

            if label_locator.count() == 0 or not label_locator.is_visible():
                return "Label or ID Not Found"

            label_id = label_locator.get_attribute("id")
            if not label_id:
                return "Label or ID Not Found"

            label_id_literal = ComponentUtils.xpath_literal(f" {label_id} ")
            linked_containers = page.locator(
                "xpath=//*[@role='combobox' and contains("
                "concat(' ', normalize-space(@aria-labelledby), ' '), "
                + label_id_literal
                + ")]"
            ).filter(visible=True)

            if linked_containers.count() == 0:
                return "READ_ONLY"

            linked_container = linked_containers.first
            aria_disabled = linked_container.get_attribute("aria-disabled")

            if aria_disabled != "true":
                return "EDITABLE"

            return "READ_ONLY"

        except Exception:
            return "Label or ID Not Found"
