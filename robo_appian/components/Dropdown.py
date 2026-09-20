"""Reusable utilities for interacting with Appian dropdown components."""

import logging
from typing import Optional, Union

from playwright.sync_api import Locator, Page, expect
from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)

Scope = Union[Page, Locator]


class Dropdown:
    """Reusable operations for Appian dropdown components."""

    @staticmethod
    def _dropdown_locator(
        scope: Scope,
        accessible_name: str,
        exact: bool = True,
        editable_only: bool = False,
        allow_required_marker: bool = True,
    ) -> Locator:
        """Build a direct semantic XPath locator for an Appian dropdown.

        The dropdown is resolved in one XPath by matching a preceding label
        ``span`` and the ``div[role=combobox]`` whose ``aria-labelledby``
        references that label ID. This is the single component-discovery rule
        used by label-based dropdown operations. No generated Appian IDs or
        CSS class names are used.

        Args:
            scope: Page or Locator used to resolve the component.
            accessible_name: Visible field label.
            exact: Whether the label text must match exactly.
            editable_only: When True, exclude comboboxes with
                ``aria-disabled=true``.
            allow_required_marker: When True, exact label matching also accepts
                Appian's trailing required-marker variants (``Label*`` and
                ``Label *``).

        Returns:
            A live locator for the matching dropdown.

        Raises:
            ValueError: If the accessible name is empty.
        """
        normalized_name = str(accessible_name or "").strip()
        if not normalized_name:
            raise ValueError("Dropdown accessible name cannot be empty or whitespace.")

        label_text = "normalize-space(string(.))"

        if exact and not allow_required_marker:
            # Strict mode matches the rendered Appian label exactly as supplied.
            expected = ComponentUtils.xpath_literal(normalized_name)
            label_condition = f"{label_text} = {expected}"
        else:
            # Appian appends a trailing required marker to some field labels.
            # Normalize only that trailing marker so flexible exact matching
            # accepts Label, Label*, and Label * without stripping asterisks
            # elsewhere in legitimate labels.
            base_name = normalized_name.rstrip()
            if base_name.endswith("*"):
                base_name = base_name[:-1].rstrip()

            expected = ComponentUtils.xpath_literal(base_name)
            if exact:
                expected_required = ComponentUtils.xpath_literal(f"{base_name}*")
                expected_required_spaced = ComponentUtils.xpath_literal(
                    f"{base_name} *"
                )
                label_condition = (
                    "("
                    f"{label_text} = {expected}"
                    f" or {label_text} = {expected_required}"
                    f" or {label_text} = {expected_required_spaced}"
                    ")"
                )
            else:
                label_condition = f"contains({label_text}, {expected})"

        editable_condition = " and not(@aria-disabled='true')" if editable_only else ""

        xpath = (
            ".//div["
            "@role='combobox'"
            + editable_condition
            + " and @aria-labelledby = "
            + f"preceding::span[@id and {label_condition}]/@id"
            + "]"
        )
        return scope.locator(f"xpath={xpath}")

    @staticmethod
    def _get_dropdown(
        scope: Scope,
        accessible_name: str,
        exact: bool = True,
        allow_required_marker: bool = True,
    ) -> Locator:
        """
        Resolve a visible Appian dropdown by accessible label.

        Args:
            scope: Page or Locator used to resolve the component.
            accessible_name: Accessible name of the dropdown.
            exact: Whether the accessible-name match must be exact.
            allow_required_marker: Whether exact matching may accept Appian's
                trailing required-marker variants.

        Returns:
            The resolved visible dropdown locator.

        Raises:
            ValueError: If the accessible name is empty.
            AssertionError: If the dropdown is not visible.
        """
        normalized_name = str(accessible_name or "").strip()
        dropdown = Dropdown._dropdown_locator(
            scope,
            normalized_name,
            exact=exact,
            allow_required_marker=allow_required_marker,
        ).filter(visible=True).first

        expect(
            dropdown,
            f"Dropdown '{normalized_name}' was not visible.",
        ).to_be_visible()

        return dropdown

    @staticmethod
    def _expand(
        dropdown: Locator,
    ) -> None:
        """
        Expand an Appian dropdown when it is currently collapsed.

        Appian dropdowns expose their state through ``aria-expanded``.
        The method does nothing when the dropdown is already expanded.

        Args:
            dropdown: Already-resolved Appian dropdown locator.

        Raises:
            AssertionError: If the dropdown is not visible, enabled,
                or does not expand after being clicked.
        """
        expect(
            dropdown,
            "Dropdown is not visible.",
        ).to_be_visible()

        expect(
            dropdown,
            "Dropdown is not enabled.",
        ).to_be_enabled()
        expect(
            dropdown,
            "Dropdown is marked aria-disabled.",
        ).not_to_have_attribute("aria-disabled", "true")

        if dropdown.get_attribute("aria-expanded") == "true":
            return

        dropdown.click()

        expect(
            dropdown,
            "Dropdown did not expand after click.",
        ).to_have_attribute(
            "aria-expanded",
            "true",
        )

    @staticmethod
    def _get_listbox(
        page: Page,
        dropdown: Locator,
    ) -> Locator:
        """
        Resolve the listbox associated with an expanded Appian dropdown.

        Appian connects the combobox to its option list through the
        ``aria-controls`` attribute.

        Args:
            page: Current Playwright page.
            dropdown: Expanded Appian dropdown locator.

        Returns:
            The visible listbox associated with the dropdown.

        Raises:
            AssertionError: If the dropdown is not expanded, does not
                expose ``aria-controls``, or its listbox is not visible.
        """
        expect(
            dropdown,
            ("Dropdown is not expanded, so its options " "cannot be read."),
        ).to_have_attribute(
            "aria-expanded",
            "true",
        )

        listbox_id = dropdown.get_attribute("aria-controls")

        if not listbox_id:
            raise AssertionError(
                "Dropdown does not expose an aria-controls "
                "attribute for its option list."
            )

        combobox_label_id = dropdown.get_attribute("aria-labelledby")
        if not combobox_label_id:
            raise AssertionError(
                "Dropdown does not expose an aria-labelledby attribute."
            )

        listbox_id_literal = ComponentUtils.xpath_literal(listbox_id)
        label_id_literal = ComponentUtils.xpath_literal(f" {combobox_label_id} ")
        listbox = page.locator(
            "xpath=//*[@role='listbox' and @id="
            + listbox_id_literal
            + " and contains(concat(' ', normalize-space(@aria-labelledby), ' '), "
            + label_id_literal
            + ")][1]"
        )

        expect(
            listbox,
            "Dropdown option list was not visible.",
        ).to_be_visible()

        return listbox

    @staticmethod
    def _get_option(
        listbox: Locator,
        option_text: str,
        exact: bool = True,
    ) -> Locator:
        """
        Resolve a visible option from an Appian dropdown listbox.

        Args:
            listbox: Visible Appian listbox.
            option_text: Option text to locate.
            exact: Whether the option name must match exactly.

        Returns:
            The matching visible option.

        Raises:
            ValueError: If the option name is empty.
            AssertionError: If the option is not visible.
        """
        normalized_option = str(option_text or "").strip()

        if not normalized_option:
            raise ValueError("Dropdown option cannot be empty or whitespace.")

        expected = ComponentUtils.xpath_literal(normalized_option)
        option_text_xpath = "normalize-space(string(.))"
        option_match = (
            f"{option_text_xpath} = {expected}"
            if exact
            else f"contains({option_text_xpath}, {expected})"
        )
        option = listbox.locator(
            "xpath=.//*[@role='option' and " + option_match + "][1]"
        ).filter(visible=True)

        expect(
            option,
            (f"Dropdown option '{normalized_option}' " "was not visible."),
        ).to_be_visible()

        return option

    @staticmethod
    def _stable_dropdown_locator(page: Page, dropdown: Locator) -> Locator:
        """Re-resolve an Appian dropdown through its controlled listbox relation."""
        listbox_id = dropdown.get_attribute("aria-controls")
        if not listbox_id:
            raise AssertionError("Dropdown does not expose an aria-controls attribute.")

        listbox_id_literal = ComponentUtils.xpath_literal(listbox_id)
        return (
            page.locator(
                "xpath=//*[@role='combobox' and @aria-controls="
                + listbox_id_literal
                + "]"
            )
            .filter(visible=True)
            .first
        )

    @staticmethod
    def _verify_selection(
        selected_dropdown: Locator,
        listbox: Locator,
        selected_text: str,
        failure_context: str,
    ) -> None:
        """Verify an Appian selection after the control rerenders."""
        expect(
            listbox,
            f"Dropdown option list remained visible after selecting {failure_context}.",
        ).to_be_hidden()

        expect(
            selected_dropdown,
            f"Dropdown remained expanded after selecting {failure_context}.",
        ).to_have_attribute("aria-expanded", "false")
        expect(
            selected_dropdown,
            f"Dropdown did not retain selected option {failure_context}.",
        ).to_contain_text(selected_text)

    @staticmethod
    def select_by_locator(
        page: Page,
        dropdown: Locator,
        option_text: str,
        exact: bool = True,
    ) -> None:
        """
        Select an option from an already-resolved Appian dropdown.

        Use this method when another reusable component, such as
        Table, has already located the dropdown.

        This method owns all dropdown behavior:
        - validates the component;
        - expands it when necessary;
        - resolves the associated listbox;
        - selects the requested option.

        Args:
            page: Current Playwright page.
            dropdown: Already-resolved Appian dropdown locator.
            option_text: Option text to select.
            exact: Whether the option text must match exactly.
        """
        normalized_option = str(option_text or "").strip()

        if not normalized_option:
            raise ValueError("Dropdown option cannot be empty or whitespace.")

        Dropdown._expand(dropdown)
        listbox = Dropdown._get_listbox(
            page,
            dropdown,
        )
        option = Dropdown._get_option(
            listbox,
            normalized_option,
            exact=exact,
        )
        selected_dropdown = Dropdown._stable_dropdown_locator(page, dropdown)
        option.click()

        Dropdown._verify_selection(
            selected_dropdown,
            listbox,
            normalized_option,
            f"'{normalized_option}'",
        )

        logger.debug(
            "Selected dropdown option '%s'.",
            normalized_option,
        )

    @staticmethod
    def select(
        page: Page,
        accessible_name: str,
        option_text: str,
        exact: bool = True,
        scope: Optional[Locator] = None,
    ) -> None:
        """
        Select an option from an Appian dropdown identified by label.

        Args:
            page: Current Playwright page.
            accessible_name: Accessible name of the dropdown.
            option_text: Option text to select.
            exact: Whether label and option matching must be exact.
            scope: Optional container used to restrict dropdown lookup.
        """
        logger.info(
            "Dropdown selection starting: field='%s'.",
            accessible_name,
        )
        search_scope: Scope = scope if scope is not None else page

        dropdown = Dropdown._get_dropdown(
            search_scope,
            accessible_name,
            exact=exact,
        )

        Dropdown.select_by_locator(
            page,
            dropdown,
            option_text,
            exact=exact,
        )

        logger.info(
            "Dropdown selection completed: field='%s'.",
            accessible_name,
        )

    @staticmethod
    def select_by_index(
        page: Page,
        accessible_name: str,
        option_index: int,
        exact: bool = True,
        scope: Optional[Locator] = None,
    ) -> None:
        """Select an Appian dropdown option by one-based option index.

        This is useful when the option text is dynamic but its position is
        stable. Index 1 selects the first real selectable option, index 2 the second,
        and so on. Placeholder entries such as "Select a Value" are excluded.
        """
        if option_index < 1:
            raise ValueError("Dropdown option index must be 1 or greater.")

        search_scope: Scope = scope if scope is not None else page
        dropdown = Dropdown._get_dropdown(
            search_scope, accessible_name, exact=exact
        )
        Dropdown._expand(dropdown)
        listbox = Dropdown._get_listbox(page, dropdown)

        # Appian can render the listbox before its dynamic choices finish
        # loading. It may also expose the placeholder as an option. A
        # one-based index must therefore apply only to real selectable
        # choices, not to the placeholder.
        options = listbox.locator(
            "xpath=.//*[@role='option' and "
            "translate(normalize-space(string(.)), "
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') "
            "!= 'select a value']"
        ).filter(visible=True)

        selected_option = options.nth(option_index - 1)
        expect(
            selected_option,
            (
                f"Dropdown '{accessible_name}' did not render selectable option "
                f"{option_index}."
            ),
        ).to_be_visible()

        selected_text = selected_option.inner_text().strip()
        selected_dropdown = Dropdown._stable_dropdown_locator(page, dropdown)
        selected_option.click()

        if selected_text:
            Dropdown._verify_selection(
                selected_dropdown,
                listbox,
                selected_text,
                f"one-based index {option_index} from '{accessible_name}'",
            )

        logger.debug(
            "Selected one-based option index %s ('%s') from dropdown '%s'.",
            option_index,
            selected_text,
            accessible_name,
        )

    @staticmethod
    def select_by_placeholder(
        page: Page,
        placeholder_text: str,
        option_text: str,
        exact: bool = True,
    ) -> None:
        """Select an option from a visible Appian dropdown by placeholder text.

        Appian dropdown placeholders are commonly rendered as the visible text
        inside the combobox rather than as an HTML ``placeholder`` attribute.
        The resolved component is delegated to ``select_by_locator`` so all
        dropdown expansion and option-selection behavior remains centralized.
        """
        normalized_placeholder = str(placeholder_text or "").strip()
        normalized_option = str(option_text or "").strip()

        if not normalized_placeholder:
            raise ValueError("Dropdown placeholder cannot be empty or whitespace.")
        if not normalized_option:
            raise ValueError("Dropdown option cannot be empty or whitespace.")

        expected = ComponentUtils.xpath_literal(normalized_placeholder)
        displayed_text = "normalize-space(string(.))"
        placeholder_match = (
            f"{displayed_text} = {expected}"
            if exact
            else f"contains({displayed_text}, {expected})"
        )
        dropdown = page.locator(
            "xpath=(//*[@role='combobox' and " + placeholder_match + "])[1]"
        ).filter(visible=True)

        expect(
            dropdown,
            f"Dropdown placeholder '{normalized_placeholder}' was not visible.",
        ).to_be_visible()

        Dropdown.select_by_locator(
            page,
            dropdown,
            normalized_option,
            exact=exact,
        )

        logger.debug(
            "Selected '%s' from dropdown with placeholder '%s'.",
            normalized_option,
            normalized_placeholder,
        )

    @staticmethod
    def is_visible(
        page: Page,
        accessible_name: str,
        exact: bool = True,
        scope: Optional[Locator] = None,
    ) -> bool:
        """
        Return whether a visible Appian dropdown exists by label.

        Args:
            page: Current Playwright page.
            accessible_name: Accessible name to locate.
            exact: Whether the accessible-name match must be exact.
            scope: Optional container used to restrict lookup.
        """
        normalized_name = str(accessible_name or "").strip()

        if not normalized_name:
            return False

        search_scope: Scope = scope if scope is not None else page

        dropdown = (
            Dropdown._dropdown_locator(
                search_scope,
                normalized_name,
                exact=exact,
            )
            .filter(visible=True)
            .first
        )

        return dropdown.count() > 0

    @staticmethod
    def is_editable(
        scope: Scope,
        accessible_name: str,
        exact: bool = True,
        immediate: bool = False,
        timeout: Optional[float] = None,
    ) -> bool:
        """Return True only when the labeled Appian dropdown is editable.

        A field is editable only when a visible ``div`` with ``role=combobox``
        references a matching label ``span`` through ``aria-labelledby`` and
        does not have ``aria-disabled=true``. Any field that does not satisfy
        all of those criteria is treated as non-editable, including disabled
        dropdowns and read-only display fields.

        Args:
            scope: Playwright Page or Locator used as the search scope.
            accessible_name: Visible label text of the dropdown.
            exact: Whether the label-text match must be exact.
            immediate: Whether to inspect the current DOM without waiting.
            timeout: Optional timeout in seconds. When omitted, Playwright's
                configured default timeout is used.

        Returns:
            ``True`` only when the editable-dropdown criteria match; otherwise
            ``False``.
        """
        normalized_name = str(accessible_name or "").strip()
        if not normalized_name:
            return False

        editable_dropdown = (
            Dropdown._dropdown_locator(
                scope,
                normalized_name,
                exact=exact,
                editable_only=True,
            )
            .filter(visible=True)
            .first
        )

        if immediate:
            return editable_dropdown.count() > 0

        try:
            editable_expectation = expect(
                editable_dropdown,
                f"Dropdown '{normalized_name}' did not become editable.",
            )
            if timeout is None:
                editable_expectation.to_be_visible()
            else:
                editable_expectation.to_be_visible(timeout=timeout * 1000)
            return True
        except AssertionError:
            return False

    @staticmethod
    def get_value(
        page: Page,
        accessible_name: str,
        exact: bool = True,
        scope: Optional[Locator] = None,
    ) -> str:
        """
        Return the currently displayed value of a dropdown.

        Args:
            page: Current Playwright page.
            accessible_name: Accessible name of the dropdown.
            exact: Whether the accessible-name match must be exact.
            scope: Optional container used to restrict lookup.

        Returns:
            Normalized visible text of the dropdown.
        """
        search_scope: Scope = scope if scope is not None else page

        dropdown = Dropdown._get_dropdown(
            search_scope,
            accessible_name,
            exact=exact,
        )

        return dropdown.inner_text().strip()
