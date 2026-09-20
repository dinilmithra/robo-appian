"""Generic utilities for interacting with Appian table and grid components."""

import logging
from typing import Optional

from playwright.sync_api import Locator, Page, expect

from robo_appian.components.InputDate import InputDate
from robo_appian.components.Dropdown import Dropdown
from robo_appian.components.InputText import InputText
from robo_appian.components.RadioSelect import RadioSelect
from robo_appian.components.SearchInput import SearchInput
from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)


class Table:
    """Provide reusable operations for Appian tables and editable grids."""

    @staticmethod
    def __xpath_literal(value: str) -> str:
        """Return a safe XPath string literal."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    """Reusable operations for Appian tables and editable grids."""

    @staticmethod
    def __get_table(
        page: Page,
        table_name: str = "",
        exact: bool = True,
        column_name: Optional[str] = None,
    ) -> Locator:
        """
        Resolve a visible table.

        Resolution order:
        1. Locate by table or surrounding section name when supplied.
        2. Locate by column name when supplied.
        3. Otherwise return the first visible table.

        Named-row operations should be preferred when multiple tables
        contain the same column name.
        """
        normalized_table_name = str(table_name or "").strip()
        normalized_column = str(column_name or "").strip()

        if normalized_table_name:
            table_label = (
                page.get_by_text(
                    normalized_table_name,
                    exact=exact,
                )
                .filter(visible=True)
                .first
            )

            expect(
                table_label,
                f"Table label '{normalized_table_name}' was not visible.",
            ).to_be_visible()

            region = table_label.locator("xpath=ancestor::*[@role='region'][1]")

            if region.count() > 0:
                table = region.locator("table").filter(visible=True).first

                if table.count() > 0:
                    return table

            table = (
                table_label.locator("xpath=following::table[1]")
                .filter(visible=True)
                .first
            )

            expect(
                table,
                f"Table '{normalized_table_name}' was not visible.",
            ).to_be_visible()

            return table

        if normalized_column:
            tables = page.locator("table").filter(visible=True)

            for index in range(tables.count()):
                table = tables.nth(index)

                if Table.__has_column(
                    table,
                    normalized_column,
                ):
                    return table

            raise ValueError(
                f"No visible table contains column " f"'{normalized_column}'."
            )

        table = page.locator("table").filter(visible=True).first

        expect(
            table,
            "No visible table was found.",
        ).to_be_visible()

        return table

    @staticmethod
    def __has_column(
        table: Locator,
        column_name: str,
    ) -> bool:
        """
        Return whether the table contains the requested column.

        Appian editable grids expose the column name both as visible
        header text and, commonly, through the ``abbr`` attribute.
        """
        normalized = str(column_name or "").strip()

        if not normalized:
            return False

        headers = table.locator("thead th")

        for index in range(headers.count()):
            header = headers.nth(index)

            header_text = header.inner_text().strip()
            header_abbr = (header.get_attribute("abbr") or "").strip()

            if header_text == normalized or header_abbr == normalized:
                return True

        return False

    @staticmethod
    def __get_column_index(
        table: Locator,
        column_name: str,
    ) -> int:
        """
        Return the zero-based index of a named table column.

        Both visible header text and Appian's ``abbr`` attribute are
        supported.
        """
        normalized = str(column_name or "").strip()

        if not normalized:
            raise ValueError("Column name cannot be empty or whitespace.")

        headers = table.locator("thead th")

        for index in range(headers.count()):
            header = headers.nth(index)

            header_text = header.inner_text().strip()
            header_abbr = (header.get_attribute("abbr") or "").strip()

            if header_text == normalized or header_abbr == normalized:
                return index

        raise AssertionError(f"Column '{normalized}' was not found in table.")

    @staticmethod
    def __get_data_rows(table: Locator) -> Locator:
        """Return visible Appian data rows, excluding empty-grid placeholders."""
        return table.locator(
            "tbody > tr"
            ":not(:has([data-empty-grid-message='true']))"
            ":not(.EditableGridLayout---empty_msg)"
            ":not(:has(td[role='alert'][colspan]))"
        ).filter(visible=True)

    @staticmethod
    def __get_row_by_index(
        page: Page,
        table_name: str,
        row_number: int,
        exact: bool = True,
        column_name: Optional[str] = None,
    ) -> Locator:
        """
        Return a one-based data row.

        ``row_number`` refers to rows inside ``tbody`` only. The table
        header is not included in the row number.
        """
        if row_number < 1:
            raise ValueError("Row number must be 1 or greater.")

        table = Table.__get_table(
            page,
            table_name,
            exact,
            column_name,
        )

        rows = Table.__get_data_rows(table)

        row_count = rows.count()

        if row_count < row_number:
            raise AssertionError(
                f"Requested data row {row_number}, "
                f"but only {row_count} visible rows were found."
            )

        row = rows.nth(row_number - 1)

        expect(
            row,
            f"Data row {row_number} was not visible.",
        ).to_be_visible()

        return row

    @staticmethod
    def __get_row_by_name(
        table: Locator,
        row_name: str,
        exact: bool = True,
    ) -> Locator:
        """
        Locate a visible table row using its first data-cell text.

        Appian constructs a row's accessible name from all cells in that
        row. Therefore an exact role/name lookup such as:

            get_by_role("row", name="Registration Type", exact=True)

        is unreliable because the dropdown value is also part of the
        accessible row name.

        Matrix-style Appian tables use the first cell as the semantic
        row label, so this method matches against that cell instead.
        """
        normalized = str(row_name or "").strip()

        if not normalized:
            raise ValueError("Row name cannot be empty or whitespace.")

        rows = Table.__get_data_rows(table)

        for index in range(rows.count()):
            row = rows.nth(index)

            cells = row.locator("td")

            if cells.count() == 0:
                continue

            first_cell_text = cells.first.inner_text().strip()

            if exact:
                matches = first_cell_text == normalized
            else:
                matches = normalized in first_cell_text

            if matches:
                return row

        raise AssertionError(
            f"Visible table row containing " f"'{normalized}' was not found."
        )

    @staticmethod
    def __get_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        exact: bool = True,
    ) -> Locator:
        """
        Return a cell using one-based data-row number and column name.
        """
        if row_number < 1:
            raise ValueError("Row number must be 1 or greater.")

        table = Table.__get_table(
            page,
            table_name,
            exact,
            column_name,
        )

        rows = Table.__get_data_rows(table)

        # Appian editable grids can briefly render an empty placeholder row
        # while an action is adding the real row.  Do not inspect the row/cell
        # counts immediately; let Playwright wait for the requested data row
        # to materialize before resolving its cell.
        row = rows.nth(row_number - 1)
        expect(
            row,
            (
                f"Row {row_number} was not available in table "
                f"containing column '{column_name}'."
            ),
        ).to_be_visible()

        column_index = Table.__get_column_index(
            table,
            column_name,
        )

        cell = row.locator("td").nth(column_index)

        expect(
            cell,
            (f"Cell at row {row_number}, " f"column '{column_name}' was not visible."),
        ).to_be_visible()

        return cell

    @staticmethod
    def __get_cell_by_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
        exact: bool = True,
    ) -> Locator:
        """
        Return the cell at a named-row/named-column intersection.

        The row is located first and its ancestor table determines the
        table to use. This avoids ambiguity when several tables contain
        the same attendee column name.
        """
        if not column_name or not column_name.strip():
            raise ValueError("Column name cannot be empty or whitespace.")

        table = Table.__get_table(
            page,
            table_name=table_name,
            exact=True,
        )

        row = Table.__get_row_by_name(
            table,
            row_name,
            exact,
        )

        column_index = Table.__get_column_index(
            table,
            column_name,
        )

        cells = row.locator("td")

        if cells.count() <= column_index:
            raise AssertionError(
                f"Column '{column_name}' was not available " f"in row '{row_name}'."
            )

        cell = cells.nth(column_index)

        expect(
            cell,
            (f"Cell at row '{row_name}', " f"column '{column_name}' was not visible."),
        ).to_be_visible()

        return cell

    @staticmethod
    def get_row_count(
        page: Page,
        table_name: str = "",
        column_name: Optional[str] = None,
    ) -> int:
        """Count visible data rows in a resolved Appian table.

        Identify the table by region or heading text when ``table_name`` is
        supplied. Otherwise, optionally use a visible column header and finally
        fall back to the first visible table. Empty-grid placeholder rows are
        excluded.

        Args:
            page: Appian page containing the table.
            table_name: Optional region or heading text identifying the table.
            column_name: Optional header used when no table name is available.

        Returns:
            Number of visible body rows containing actual data.
        """
        table = Table.__get_table(
            page,
            table_name,
            column_name=column_name,
        )

        return Table.__get_data_rows(table).count()

    @staticmethod
    def get_cell_text(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
    ) -> str:
        """Read text from a one-based data row and named column.

        Column lookup uses visible header text or its ``abbr`` value. Row one is
        the first visible data row in ``tbody``; header and empty-grid rows are
        not included.

        Args:
            page: Appian page containing the table.
            table_name: Region or heading text identifying the table.
            row_number: One-based visible data-row position.
            column_name: Visible header or ``abbr`` text identifying the column.

        Returns:
            Cell text with surrounding whitespace removed.

        Raises:
            ValueError: If ``row_number`` is less than one or a required name is
                empty.
            AssertionError: If the table, row, column, or cell is unavailable.
        """
        cell = Table.__get_cell(
            page,
            table_name,
            row_number,
            column_name,
        )

        return cell.inner_text().strip()

    @staticmethod
    def get_cell_text_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
    ) -> str:
        """Return text from a named-row/named-column intersection."""
        cell = Table.__get_cell_by_named_row(
            page,
            table_name,
            row_name,
            column_name,
        )

        return cell.inner_text().strip()

    @staticmethod
    def fill_input_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
        value: str,
    ) -> None:
        """
        Fill a text input or textarea at a named-row/column intersection.

        This supports Appian TextInput and ParagraphWidget controls because
        both expose textbox semantics to Playwright.
        """
        cell = Table.__get_cell_by_named_row(
            page,
            table_name,
            row_name,
            column_name,
        )

        textbox = cell.get_by_role("textbox").filter(visible=True).first

        expect(
            textbox,
            (
                f"Text input was not found in row "
                f"'{row_name}', column '{column_name}'."
            ),
        ).to_be_visible()

        InputText.fill_by_locator(
            textbox,
            value,
        )

        logger.debug(
            "Filled '%s' in row '%s', column '%s'.",
            value,
            row_name,
            column_name,
        )

    @staticmethod
    def fill_input_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        value: str,
    ) -> None:
        """Fill a textbox using data-row number and column name."""
        cell = Table.__get_cell(
            page,
            table_name,
            row_number,
            column_name,
        )

        textbox = cell.get_by_role("textbox").filter(visible=True).first

        expect(
            textbox,
            (
                f"Text input was not found at row "
                f"{row_number}, column '{column_name}'."
            ),
        ).to_be_visible()

        InputText.fill_by_locator(
            textbox,
            value,
        )

    @staticmethod
    def fill_date_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
        value: str,
    ) -> None:
        """Fill a date input at a table section/row/column intersection."""
        cell = Table.__get_cell_by_named_row(
            page, table_name, row_name, column_name
        )
        date_input = (
            cell.locator('input[placeholder="mm/dd/yyyy"]').filter(visible=True).first
        )
        expect(
            date_input,
            f"Date input was not found in table '{table_name}', row '{row_name}', column '{column_name}'.",
        ).to_be_visible()
        InputDate.fill_by_locator(
            page,
            date_input,
            value,
        )

    @staticmethod
    def select_dropdown_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        option_name: str,
    ) -> None:
        """
        Select a dropdown using data-row number and column name.

        Table resolves the component. Dropdown performs the
        actual Appian dropdown interaction.
        """
        cell = Table.__get_cell(
            page,
            table_name,
            row_number,
            column_name,
        )

        dropdown = cell.get_by_role("combobox").filter(visible=True).first

        expect(
            dropdown,
            (
                f"Dropdown was not found at row "
                f"{row_number}, column '{column_name}'."
            ),
        ).to_be_visible()

        Dropdown.select_by_locator(
            page,
            dropdown,
            option_name,
        )

        logger.debug(
            "Selected '%s' at row %s, column '%s'.",
            option_name,
            row_number,
            column_name,
        )

    @staticmethod
    def select_dropdown_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """
        Select a dropdown at a named-row/named-column intersection.

        Example:
            row_name="Registration Type"
            column_name="ROBO APPIAN"
            option_name="Other"

        Table only locates the dropdown. Dropdown retains
        responsibility for interacting with the Appian component.
        """
        cell = Table.__get_cell_by_named_row(
            page,
            table_name,
            row_name,
            column_name,
        )

        dropdown = cell.get_by_role("combobox").filter(visible=True).first

        expect(
            dropdown,
            (
                f"Dropdown was not found in row "
                f"'{row_name}', column '{column_name}'."
            ),
        ).to_be_visible()

        Dropdown.select_by_locator(
            page,
            dropdown,
            option_name,
        )

        logger.debug(
            ("Selected '%s' from dropdown " "in row '%s', column '%s'."),
            option_name,
            row_name,
            column_name,
        )

    @staticmethod
    def select_search_input_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """
        Select a value from an Appian SearchInput in a named table row.

        Table resolves the row/column intersection and SearchInput.
        SearchInput performs the actual picker interaction.
        """
        cell = Table.__get_cell_by_named_row(
            page,
            table_name,
            row_name,
            column_name,
        )

        search_input = cell.get_by_role("combobox").filter(visible=True).first

        expect(
            search_input,
            (
                f"SearchInput was not found in row "
                f"'{row_name}', column '{column_name}'."
            ),
        ).to_be_visible()

        # Delegate picker behavior to the generic SearchInput component API.
        SearchInput.select_by_locator(
            page=page,
            lookup=search_input,
            search_text=option_name,
            field_name=row_name,
        )

        logger.debug(
            ("Selected '%s' from SearchInput " "in row '%s', column '%s'."),
            option_name,
            row_name,
            column_name,
        )

    @staticmethod
    def get_label_value_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
    ) -> str:
        """Return normalized text from a table cell.

        This public compatibility API delegates to ``get_cell_text``.
        """
        return Table.get_cell_text(page, table_name, row_number, column_name)

    @staticmethod
    def fill_textbox_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        value: str,
    ) -> None:
        """Fill a textbox in a table cell using the generic input API."""
        Table.fill_input_in_cell(page, table_name, row_number, column_name, value)

    @staticmethod
    def fill_date_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        value: str,
    ) -> None:
        """Fill a date control in a table cell using ``InputDate``."""
        cell = Table.__get_cell(page, table_name, row_number, column_name)
        date_input = (
            cell.locator('input[placeholder="mm/dd/yyyy"]').filter(visible=True).first
        )
        expect(
            date_input,
            f"Date input was not found at row {row_number}, column '{column_name}'.",
        ).to_be_visible()
        InputDate.fill_by_locator(page, date_input, value)

    @staticmethod
    def select_radio_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        value: str,
    ) -> None:
        """Select a radio option in a table cell using ``RadioSelect``."""
        cell = Table.__get_cell(page, table_name, row_number, column_name)
        RadioSelect.click_locator(cell, value)

    @staticmethod
    def click_action_in_cell(
        page: Page,
        table_name: str,
        row_number: int,
        column_name: str,
        action_label: str,
        exact: bool = True,
    ) -> None:
        """Click an Appian link or button action contained in a table cell.

        Appian table actions are commonly represented in either of these ways:

        * a clickable link/button containing accessibility-only action text, or
        * a clickable link/button containing an icon whose descendant exposes
          the action through ``aria-label``.

        The table/cell is resolved first, then only clickable descendants of
        that cell are considered. This keeps the utility generic while
        supporting both Appian action representations.
        """
        normalized_action = str(action_label or "").strip()
        if not normalized_action:
            raise ValueError("Action label cannot be empty or whitespace.")

        cell = Table.__get_cell(
            page,
            table_name,
            row_number,
            column_name,
        )

        clickable_actions = cell.locator("a, button").filter(visible=True)
        action = None

        for index in range(clickable_actions.count()):
            candidate = clickable_actions.nth(index)

            # Appian may put the action description in hidden text inside
            # the clickable element, e.g. "Link to this record".
            candidate_text = str(candidate.text_content() or "").strip()
            text_matches = (
                candidate_text == normalized_action
                if exact
                else normalized_action in candidate_text
            )

            if text_matches:
                action = candidate
                break

            # Icon actions often expose the action on a descendant SVG/image,
            # e.g. <svg role="img" aria-label="Select">.
            labeled_descendants = candidate.locator("[aria-label]")
            for label_index in range(labeled_descendants.count()):
                descendant = labeled_descendants.nth(label_index)
                aria_label = str(descendant.get_attribute("aria-label") or "").strip()
                label_matches = (
                    aria_label == normalized_action
                    if exact
                    else normalized_action in aria_label
                )
                if label_matches:
                    action = candidate
                    break

            if action is not None:
                break

        if action is None:
            raise AssertionError(
                f"Action '{normalized_action}' was not found in table "
                f"'{table_name}', row {row_number}, column '{column_name}'."
            )

        expect(
            action,
            (
                f"Action '{normalized_action}' was not visible in table "
                f"'{table_name}', row {row_number}, column '{column_name}'."
            ),
        ).to_be_visible()

        ComponentUtils.click(action)

        logger.debug(
            "Clicked action '%s' in table '%s', row %s, column '%s'.",
            normalized_action,
            table_name,
            row_number,
            column_name,
        )

    @staticmethod
    def click_row(
        page: Page,
        table_name: str,
        row_number: int,
        exact: bool = True,
    ) -> None:
        """Click a one-based data row in a named Appian table."""
        row = Table.__get_row_by_index(
            page,
            table_name,
            row_number,
            exact,
        )
        ComponentUtils.click(row)

    @staticmethod
    def click_checkbox_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        checked: bool = True,
    ) -> None:
        """Check or uncheck the checkbox contained in a named table row."""
        table = Table.__get_table(page, table_name=table_name)
        row = Table.__get_row_by_name(
            table,
            row_name,
            exact=False,
        )

        checkbox = row.get_by_role("checkbox").filter(visible=True).first

        expect(
            checkbox,
            f"Checkbox was not found in row '{row_name}'.",
        ).to_be_visible()

        if checked:
            checkbox.check()
        else:
            checkbox.uncheck()

    @staticmethod
    def select_radio_in_named_row(
        page: Page,
        table_name: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a radio option from a named-row/column intersection."""
        cell = Table.__get_cell_by_named_row(
            page,
            table_name,
            row_name,
            column_name,
            exact=False,
        )

        RadioSelect.click_locator(
            cell,
            option_name,
        )

        logger.debug(
            ("Selected radio option '%s' " "in row '%s', column '%s'."),
            option_name,
            row_name,
            column_name,
        )
