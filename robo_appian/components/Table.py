"""Generic utilities for interacting with Appian table and grid components."""

import logging
from typing import Optional

from playwright.sync_api import Locator, Page, expect
from robo_appian.utils.types import Scope

from robo_appian.components.InputDate import InputDate
from robo_appian.components.Dropdown import Dropdown
from robo_appian.components.InputText import InputText
from robo_appian.components.RadioSelect import RadioSelect
from robo_appian.components.SearchInput import SearchInput
from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)


class Table:
    """Reusable operations for Appian tables and editable grids."""

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
        scope: Scope,
        table_name: str = "",
        excat_match: bool = False,
        column_name: Optional[str] = None,
        region_name: str = "",
        table_column_name: Optional[str] = None,
    ) -> Locator:
        """
        Resolve a visible table using the first available identifier.

        Resolution precedence:
        1. ``table_name`` - explicit accessible/name-based table lookup.
        2. ``region_name`` - first visible table immediately under that region.
        3. ``table_column_name`` - table containing that named column.
        4. ``column_name`` - compatibility fallback; useful when the target
           cell column itself uniquely identifies the table.
        5. First visible table.

        If more than one identifier is supplied, the higher-precedence
        identifier is used.
        """
        normalized_table_name = str(table_name or "").strip()
        normalized_region_name = str(region_name or "").strip()
        normalized_table_column = str(table_column_name or "").strip()
        normalized_column = str(column_name or "").strip()

        if normalized_table_name:
            named_table = (
                scope.get_by_role(
                    "table",
                    name=normalized_table_name,
                    excat_match=excat_match,
                )
                .filter(visible=True)
                .first
            )
            if named_table.count() > 0:
                return named_table

            table_label = (
                scope.get_by_text(
                    normalized_table_name,
                    excat_match=excat_match,
                )
                .filter(visible=True)
                .first
            )
            expect(
                table_label,
                f"Table label '{normalized_table_name}' was not visible.",
            ).to_be_visible()

            field_layout = table_label.locator(
                "xpath=ancestor::*[contains(@class, 'FieldLayout---field_layout')][1]"
            )
            if field_layout.count() > 0:
                table = field_layout.locator("table").filter(visible=True).first
                if table.count() > 0:
                    return table

            region = table_label.locator("xpath=ancestor::*[@role='region'][1]")
            if region.count() > 0:
                table = region.locator("table").filter(visible=True).first
                if table.count() > 0:
                    return table

            table = table_label.locator("xpath=following::table[1]").filter(visible=True).first
            expect(
                table,
                f"Table '{normalized_table_name}' was not visible.",
            ).to_be_visible()
            return table

        if normalized_region_name:
            named_region = (
                scope.get_by_role(
                    "region",
                    name=normalized_region_name,
                    excat_match=excat_match,
                )
                .filter(visible=True)
                .first
            )
            expect(
                named_region,
                f"Region '{normalized_region_name}' was not visible.",
            ).to_be_visible()
            table = named_region.locator("table").filter(visible=True).first
            expect(
                table,
                f"No visible table was found inside region '{normalized_region_name}'.",
            ).to_be_visible()
            return table

        lookup_column = normalized_table_column or normalized_column
        if lookup_column:
            tables = scope.locator("table").filter(visible=True)
            for index in range(tables.count()):
                table = tables.nth(index)
                if Table.__has_column(table, lookup_column):
                    return table
            raise ValueError(
                f"No visible table contains column '{lookup_column}'."
            )

        table = scope.locator("table").filter(visible=True).first
        expect(table, "No visible table was found.").to_be_visible()
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
        scope: Scope,
        table_name: str,
        row_number: int,
        excat_match: bool = False,
        column_name: Optional[str] = None,
        region_name: str = "",
    ) -> Locator:
        """
        Return a one-based data row.

        ``row_number`` refers to rows inside ``tbody`` only. The table
        header is not included in the row number.
        """
        if row_number < 1:
            raise ValueError("Row number must be 1 or greater.")

        table = Table.__get_table(
            scope,
            table_name,
            excat_match,
            column_name,
            region_name,
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
        excat_match: bool = False,
    ) -> Locator:
        """
        Locate a visible table row using its first data-cell text.

        Appian constructs a row's accessible name from all cells in that
        row. Therefore an excat_match role/name lookup such as:

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

            if excat_match:
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
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        excat_match: bool = False,
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> Locator:
        """Resolve a table cell from flexible table/row/column identifiers.

        Table precedence: ``table_name`` > ``region_name`` >
        ``table_column_name`` > target ``column_name`` > first visible table.

        Row precedence: ``row_number`` > ``row_name``.
        Column precedence: ``column_number`` > ``column_name``.

        Row and column numbers are one-based.
        """
        table = Table.__get_table(
            scope,
            table_name=table_name,
            excat_match=excat_match,
            column_name=column_name,
            region_name=region_name,
            table_column_name=table_column_name,
        )

        if row_number is not None:
            if row_number < 1:
                raise ValueError("Row number must be 1 or greater.")
            rows = Table.__get_data_rows(table)
            row = rows.nth(row_number - 1)
            expect(
                row,
                f"Data row {row_number} was not available in the resolved table.",
            ).to_be_visible()
            row_description = str(row_number)
        else:
            normalized_row_name = str(row_name or "").strip()
            if not normalized_row_name:
                raise ValueError("Specify row_number or row_name to locate a table cell.")
            row = Table.__get_row_by_name(table, normalized_row_name, excat_match)
            row_description = f"'{normalized_row_name}'"

        if column_number is not None:
            if column_number < 1:
                raise ValueError("Column number must be 1 or greater.")
            column_index = column_number - 1
            column_description = str(column_number)
        else:
            normalized_column_name = str(column_name or "").strip()
            if not normalized_column_name:
                raise ValueError(
                    "Specify column_number or column_name to locate a table cell."
                )
            column_index = Table.__get_column_index(table, normalized_column_name)
            column_description = f"'{normalized_column_name}'"

        cells = row.locator("td")
        if cells.count() <= column_index:
            raise AssertionError(
                f"Column {column_description} was not available in row {row_description}."
            )

        cell = cells.nth(column_index)
        expect(
            cell,
            f"Cell at row {row_description}, column {column_description} was not visible.",
        ).to_be_visible()
        return cell

    @staticmethod
    def __get_cell_by_named_row(
        scope: Scope,
        table_name: str,
        row_name: str,
        column_name: str,
        excat_match: bool = False,
        region_name: str = "",
        table_column_name: Optional[str] = None,
    ) -> Locator:
        """Compatibility wrapper for named-row/named-column cell lookup."""
        return Table.__get_cell(
            scope=scope,
            table_name=table_name,
            row_name=row_name,
            column_name=column_name,
            excat_match=excat_match,
            region_name=region_name,
            table_column_name=table_column_name,
        )

    @staticmethod
    def get_row_count(
        scope: Scope,
        table_name: str = "",
        column_name: Optional[str] = None,
        region_name: str = "",
        table_column_name: Optional[str] = None,
    ) -> int:
        """Count visible data rows in a resolved Appian table.

        Identify the table by region or heading text when ``table_name`` is
        supplied. Otherwise, optionally use a visible column header and finally
        fall back to the first visible table. Empty-grid placeholder rows are
        excluded.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Optional region or heading text identifying the table.
            column_name: Optional header used when no table name is available.
            region_name: Optional accessible region name identifying the table container.
            table_column_name: Optional visible column header used to resolve the table within a region.

        Returns:
            int: Number of visible body rows containing actual data.
        """
        table = Table.__get_table(
            scope,
            table_name=table_name,
            column_name=column_name,
            region_name=region_name,
            table_column_name=table_column_name,
        )

        return Table.__get_data_rows(table).count()

    @staticmethod
    def get_cell(
        scope: Scope,
        table_name: str = "",
        region_name: str = "",
        table_column_name: Optional[str] = None,
        row_number: Optional[int] = None,
        row_name: str = "",
        column_number: Optional[int] = None,
        column_name: str = "",
        excat_match: bool = False,
    ) -> Locator:
        """Return a visible table cell using flexible semantic selectors.

        Table: table_name > region_name > table_column_name > column_name.
        Row: row_number > row_name.
        Column: column_number > column_name.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            region_name: Optional region name used to narrow the lookup.
            table_column_name: Optional table-column identifier used when resolving a cell.
            row_number: One-based row number of the target table row.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            column_name: Visible column header identifying the target column.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            Locator: The matching table cell locator.
        """
        return Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
            excat_match=excat_match,
        )

    @staticmethod
    def get_cell_text(
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> str:
        """Read text from a resolved table cell.

        Table lookup uses table_name, region_name, or a column name.
        Cell lookup accepts row_number or row_name and column_number or
        column_name. Numeric selectors take precedence when both are supplied.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            region_name: Optional region name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.


        Returns:
            str: The visible text from the matching table cell.
        """
        cell = Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        return cell.inner_text().strip()

    @staticmethod
    def get_cell_text_in_named_row(
        scope: Scope,
        table_name: str,
        row_name: str,
        column_name: str,
    ) -> str:
        """Return text from a named-row/named-column intersection.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.


        Returns:
            str: The visible text from the requested cell in the named row.
        """
        cell = Table.__get_cell_by_named_row(
            scope,
            table_name,
            row_name,
            column_name,
        )

        return cell.inner_text().strip()

    @staticmethod
    def fill_input_in_named_row(
        scope: Scope,
        table_name: str = "",
        row_name: str = "",
        column_name: str = "",
        value: str = "",
        region_name: str = "",
    ) -> None:
        """Fill a text input or textarea at a named-row/column intersection.

        This supports Appian TextInput and ParagraphWidget controls because
        both expose textbox semantics to Playwright.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            region_name: Optional region name used to narrow the lookup.
        """
        cell = Table.__get_cell_by_named_row(
            scope,
            table_name,
            row_name,
            column_name,
            region_name=region_name,
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
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a textbox using flexible table/row/column selectors.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            region_name: Optional region name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        textbox = cell.get_by_role("textbox").filter(visible=True).first
        expect(textbox, "Text input was not found in the resolved table cell.").to_be_visible()
        InputText.fill_by_locator(textbox, value)

    @staticmethod
    def fill_date_in_named_row(
        scope: Scope,
        table_name: str = "",
        row_name: str = "",
        column_name: str = "",
        value: str = "",
        region_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a date input at a named row and resolved column.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            region_name: Optional region name used to narrow the lookup.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        date_input = cell.locator('input[placeholder="mm/dd/yyyy"]').filter(visible=True).first
        expect(date_input, "Date input was not found in the resolved table cell.").to_be_visible()
        InputDate.fill_by_locator(scope, date_input, value)

    @staticmethod
    def select_dropdown_in_cell(
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        option_name: str = "",
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Select a dropdown using flexible table/row/column selectors.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
            region_name: Optional region name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        dropdown = cell.get_by_role("combobox").filter(visible=True).first
        expect(dropdown, "Dropdown was not found in the resolved table cell.").to_be_visible()
        Dropdown.select_by_locator(scope, dropdown, option_name)
        logger.debug("Selected '%s' in resolved table cell.", option_name)

    @staticmethod
    def select_dropdown_in_named_row(
        scope: Scope,
        table_name: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a dropdown at a named-row/named-column intersection.

        Example:
            row_name="Registration Type"
            column_name="ROBO APPIAN"
            option_name="Other"

        Table only locates the dropdown. Dropdown retains
        responsibility for interacting with the Appian component.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
        """
        cell = Table.__get_cell_by_named_row(
            scope,
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
            scope,
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
        scope: Scope,
        table_name: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a value from an Appian SearchInput in a named table row.

        Table resolves the row/column intersection and SearchInput.
        SearchInput performs the actual picker interaction.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
        """
        cell = Table.__get_cell_by_named_row(
            scope,
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
            scope=scope,
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
        scope: Scope,
        table_name: str,
        row_number: int,
        column_name: str,
    ) -> str:
        """Return normalized text from a table cell.

        This public compatibility API delegates to ``get_cell_text``.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.


        Returns:
            str: The value associated with the requested label in the table cell.
        """
        return Table.get_cell_text(scope, table_name, row_number, column_name)

    @staticmethod
    def fill_textbox_in_cell(
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a textbox using flexible table/row/column selectors.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            region_name: Optional region name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        Table.fill_input_in_cell(
            scope=scope,
            table_name=table_name,
            row_number=row_number,
            column_name=column_name,
            value=value,
            region_name=region_name,
            row_name=row_name,
            column_number=column_number,
            table_column_name=table_column_name,
        )

    @staticmethod
    def fill_date_in_cell(
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a date control using flexible table/row/column selectors.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            region_name: Optional region name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        date_input = cell.locator('input[placeholder="mm/dd/yyyy"]').filter(visible=True).first
        expect(date_input, "Date input was not found in the resolved table cell.").to_be_visible()
        InputDate.fill_by_locator(scope, date_input, value)

    @staticmethod
    def select_radio_in_cell(
        scope: Scope,
        table_name: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        region_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Select a radio option using flexible table/row/column selectors.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            region_name: Optional region name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = Table.__get_cell(
            scope=scope,
            table_name=table_name,
            region_name=region_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        RadioSelect.click_locator(cell, value)

    @staticmethod
    def click_action_in_cell(
        scope: Scope,
        table_name: str,
        row_number: int,
        column_name: str,
        action_label: str,
        excat_match: bool = False,
    ) -> None:
        """Click an Appian link or button action contained in a table cell.

        Appian table actions are commonly represented in either of these ways:

        * a clickable link/button containing accessibility-only action text, or
        * a clickable link/button containing an icon whose descendant exposes
          the action through ``aria-label``.

        The table/cell is resolved first, then only clickable descendants of
        that cell are considered. This keeps the utility generic while
        supporting both Appian action representations.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            action_label: Visible label of the action to invoke.
            excat_match: Whether matching must use the complete label or text.
        """
        normalized_action = str(action_label or "").strip()
        if not normalized_action:
            raise ValueError("Action label cannot be empty or whitespace.")

        cell = Table.__get_cell(
            scope,
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
                if excat_match
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
                    if excat_match
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
        scope: Scope,
        table_name: str,
        row_number: int,
        excat_match: bool = False,
    ) -> None:
        """Click a one-based data row in a named Appian table.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            excat_match: Whether matching must use the complete label or text.
        """
        row = Table.__get_row_by_index(
            scope,
            table_name,
            row_number,
            excat_match,
        )
        ComponentUtils.click(row)

    @staticmethod
    def click_checkbox_in_named_row(
        scope: Scope,
        table_name: str,
        row_name: str,
        checked: bool = True,
    ) -> None:
        """Check or uncheck the checkbox contained in a named table row.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            checked: Desired checkbox state.
        """
        table = Table.__get_table(scope, table_name=table_name)
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
        scope: Scope,
        table_name: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a radio option from a named-row/column intersection.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            table_name: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
        """
        cell = Table.__get_cell_by_named_row(
            scope,
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
