"""Generic utilities for interacting with Appian table and grid components."""

import logging
from typing import Optional

from playwright.sync_api import Locator, expect
from robo_automation import Scope

from robo_appian.appian.appian_date import AppianDate
from robo_appian.appian.appian_cell import AppianCell
from robo_appian.components.SearchInput import SearchInput
from robo_appian.utils.ComponentUtils import ComponentUtils

logger = logging.getLogger(__name__)


class AppianTable:
    """Reusable operations for Appian tables and editable grids.

    ``AppianTable`` provides semantic table/grid operations and can
    be instantiated through ``AppianPage.table(...)`` as a semantic
    Appian table component. At least one of ``label``, ``header_name``,
    ``row_name``, or ``column_name`` is required for the component form.

    ``visible`` is tri-state: ``True`` selects visible tables, ``False``
    selects hidden tables, and ``None`` applies no visibility filter so the
    live locator can contain both visible and hidden matches.
    """

    def __init__(
        self,
        scope: Scope,
        *,
        label: str | None = None,
        header_name: str | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
        timeout: float | int | None = None,
    ) -> None:
        identifiers = {
            "label": self.__normalize_optional_identifier(label, "label"),
            "header_name": self.__normalize_optional_identifier(
                header_name, "header_name"
            ),
            "row_name": self.__normalize_optional_identifier(row_name, "row_name"),
            "column_name": self.__normalize_optional_identifier(
                column_name, "column_name"
            ),
        }
        if not any(identifiers.values()):
            raise ValueError(
                "AppianTable requires at least one of: "
                "label, header_name, row_name, column_name."
            )

        self._component_scope = scope
        self._component_label = identifiers["label"]
        self._component_header_name = identifiers["header_name"]
        self._component_row_name = identifiers["row_name"]
        self._component_column_name = identifiers["column_name"]
        self._component_visible = ComponentUtils.normalize_visibility(visible)
        self._component_exact = exact
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

    @staticmethod
    def __normalize_optional_identifier(value: str | None, name: str) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"AppianTable {name} cannot be empty or whitespace.")
        return " ".join(value.split())

    @property
    def visible(self) -> bool | None:
        """Return the table visibility constraint.

        ``None`` means no visibility filtering is applied.
        """
        return self._component_visible

    @property
    def timeout(self) -> float | None:
        """Return this table's timeout override in seconds, if any."""
        return self._timeout

    def _timeout_kwargs(self) -> dict[str, float]:
        return ComponentUtils.timeout_kwargs(self._timeout)

    @property
    def locator(self) -> Locator:
        """Return the live locator for this semantic table component.

        When ``visible=None``, the returned locator is intentionally not
        filtered by visibility and can therefore contain both visible and
        hidden matching tables.
        """
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed

        raw_scope = ComponentUtils.unwrap_scope(self._component_scope)

        if self._component_label is not None:
            tables = raw_scope.get_by_role(
                "table",
                name=self._component_label,
                exact=self._component_exact,
            )
        elif self._component_header_name is not None:
            region = raw_scope.get_by_role(
                "region",
                name=self._component_header_name,
                exact=self._component_exact,
            )
            tables = region.locator("table")
        else:
            tables = raw_scope.locator("table")

        if self._component_row_name is not None:
            row_text = self.__xpath_literal(self._component_row_name)
            row_match = raw_scope.locator(
                "xpath=.//tbody/tr[td and contains("
                "normalize-space(translate(string(.), '\u00a0', ' ')), "
                + row_text
                + ")]"
            )
            tables = tables.filter(has=row_match)

        if self._component_column_name is not None:
            column_text = self.__xpath_literal(self._component_column_name)
            column_match = raw_scope.locator(
                "xpath=.//thead//th[normalize-space(translate(string(.), '\u00a0', ' '))="
                + column_text
                + " or normalize-space(@abbr)="
                + column_text
                + "]"
            )
            tables = tables.filter(has=column_match)

        if self._component_visible is not None:
            tables = tables.filter(visible=self._component_visible)

        return tables

    @property
    def appian_page(self):
        """Return the AppianPage used to create this table when available."""
        return self._component_scope

    @property
    def row_name(self) -> str | None:
        """Return the optional row-name hint used to identify this table."""
        return self._component_row_name

    @property
    def column_name(self) -> str | None:
        """Return the optional column-name hint used to identify this table."""
        return self._component_column_name

    def cell(
        self,
        *,
        row_name: str | None = None,
        row_number: int | None = None,
        column_name: str | None = None,
        column_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ):
        """Return a cell directly from this table.

        The explicit row/column arguments take precedence. When omitted,
        ``row_name`` and ``column_name`` supplied when this AppianTable was
        created are reused. Row and column numbers are one-based.
        """
        normalized_row = None if row_name is None else " ".join(str(row_name).split())
        if row_name is not None and not normalized_row:
            raise ValueError(
                "AppianAppianTable.cell row_name cannot be empty or whitespace."
            )
        if row_number is not None and row_number < 1:
            raise ValueError("AppianAppianTable.cell row_number must be 1 or greater.")

        normalized_column = (
            None if column_name is None else " ".join(str(column_name).split())
        )
        if column_name is not None and not normalized_column:
            raise ValueError(
                "AppianAppianTable.cell column_name cannot be empty or whitespace."
            )
        if column_number is not None and column_number < 1:
            raise ValueError(
                "AppianAppianTable.cell column_number must be 1 or greater."
            )

        effective_row_name = normalized_row
        if effective_row_name is None and row_number is None:
            effective_row_name = self._component_row_name
        if effective_row_name is None and row_number is None:
            raise ValueError(
                "AppianAppianTable.cell requires row_name or row_number, "
                "unless the table was created with row_name."
            )

        effective_column_name = normalized_column
        if effective_column_name is None and column_number is None:
            effective_column_name = self._component_column_name
        if effective_column_name is None and column_number is None:
            raise ValueError(
                "AppianAppianTable.cell requires column_name or column_number, "
                "unless the table was created with column_name."
            )

        row = self.row(
            name=effective_row_name,
            row_number=row_number,
            visible=None,
            exact=exact,
        )
        return row.cell(
            column_name=effective_column_name,
            column_number=column_number,
            visible=visible,
            exact=exact,
        )

    def _column_index(self, column_name: str, *, exact: bool = True) -> int:
        """Return the zero-based index for a semantic column name."""
        normalized = " ".join(str(column_name or "").split())
        if not normalized:
            raise ValueError("Column name cannot be empty or whitespace.")

        headers = self.locator.locator("thead th")
        for index in range(headers.count()):
            header = headers.nth(index)
            text = " ".join((header.inner_text() or "").split())
            abbr = " ".join((header.get_attribute("abbr") or "").split())
            if exact:
                matches = text == normalized or abbr == normalized
            else:
                matches = normalized in text or normalized in abbr
            if matches:
                return index
        raise AssertionError(f"Column '{normalized}' was not found in table.")

    def appian_column(
        self,
        *,
        name: str | None = None,
        column_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ):
        """Return a semantic column scoped to this Appian table."""
        from robo_appian.appian.appian_column import AppianColumn

        return AppianColumn(
            self,
            name=name,
            column_number=column_number,
            visible=visible,
            exact=exact,
        )

    def row(
        self,
        *,
        name: str | None = None,
        row_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ):
        """Return a semantic row scoped to this Appian table."""
        from robo_appian.appian.appian_row import AppianRow

        return AppianRow(
            self,
            name=name,
            row_number=row_number,
            visible=visible,
            exact=exact,
        )

    @staticmethod
    def __xpath_literal(value: str) -> str:
        """Return a safe XPath string literal."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def __select_radio_option(scope: Scope, option_text: str) -> None:
        """Select one native radio option inside an already-resolved table scope."""
        text = str(option_text or "").strip()
        if not text:
            raise ValueError("Radio option text cannot be empty.")

        literal = AppianTable.__xpath_literal(text)
        raw_scope = ComponentUtils.unwrap_scope(scope)
        label = raw_scope.locator(
            "xpath=(.//label[@for and normalize-space(string(.))=" + literal + "])[1]"
        )
        expect(label, f"Visible radio option '{text}' was not found.").to_be_visible()
        radio = label.locator("xpath=preceding-sibling::input[@type='radio'][1]")
        expect(radio, f"Radio input linked to '{text}' was not found.").to_be_attached()
        if radio.is_checked():
            return

        label.click()
        label = raw_scope.locator(
            "xpath=(.//label[@for and normalize-space(string(.))=" + literal + "])[1]"
        )
        radio = label.locator("xpath=preceding-sibling::input[@type='radio'][1]")
        expect(radio, f"Radio option '{text}' was not selected.").to_be_checked()

    """Reusable operations for Appian tables and editable grids."""

    @staticmethod
    def __get_table(
        scope: Scope,
        label: str = "",
        excat_match: bool = False,
        column_name: Optional[str] = None,
        header_name: str = "",
        table_column_name: Optional[str] = None,
    ) -> Locator:
        """
        Resolve a visible table using the first available identifier.

        Resolution precedence:
        1. ``label`` - explicit accessible/name-based table lookup.
        2. ``header_name`` - table scoped by an accessible region or visible heading/label.
        3. ``table_column_name`` - table containing that named column.
        4. ``column_name`` - compatibility fallback; useful when the target
           cell column itself uniquely identifies the table.
        5. First visible table.

        If more than one identifier is supplied, the higher-precedence
        identifier is used.
        """
        normalized_label = str(label or "").strip()
        normalized_header_name = str(header_name or "").strip()
        normalized_table_column = str(table_column_name or "").strip()
        normalized_column = str(column_name or "").strip()

        if normalized_label:
            named_table = (
                scope.get_by_role(
                    "table",
                    name=normalized_label,
                    exact=excat_match,
                )
                .filter(visible=True)
                .first
            )
            if named_table.count() > 0:
                return named_table

            table_label = (
                scope.get_by_text(
                    normalized_label,
                    exact=excat_match,
                )
                .filter(visible=True)
                .first
            )
            expect(
                table_label,
                f"Table label '{normalized_label}' was not visible.",
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

            table = (
                table_label.locator("xpath=following::table[1]")
                .filter(visible=True)
                .first
            )
            expect(
                table,
                f"Table '{normalized_label}' was not visible.",
            ).to_be_visible()
            return table

        if normalized_header_name:
            # Appian exposes table section headers in more than one semantic form.
            # Prefer an accessible region name when present, then fall back to a
            # visible heading/label and the table associated with that header.
            named_region = (
                scope.get_by_role(
                    "region",
                    name=normalized_header_name,
                    exact=excat_match,
                )
                .filter(visible=True)
                .first
            )
            if named_region.count() > 0:
                table = named_region.locator("table").filter(visible=True).first
                if table.count() > 0:
                    return table

            header = (
                scope.get_by_role(
                    "heading",
                    name=normalized_header_name,
                    exact=excat_match,
                )
                .filter(visible=True)
                .first
            )
            if header.count() == 0:
                header = (
                    scope.get_by_text(
                        normalized_header_name,
                        exact=excat_match,
                    )
                    .filter(visible=True)
                    .first
                )

            expect(
                header,
                f"Table header '{normalized_header_name}' was not visible.",
            ).to_be_visible()

            header_region = header.locator("xpath=ancestor::*[@role='region'][1]")
            if header_region.count() > 0:
                table = header_region.locator("table").filter(visible=True).first
                if table.count() > 0:
                    return table

            table = (
                header.locator("xpath=following::table[1]").filter(visible=True).first
            )
            expect(
                table,
                f"No visible table was found for header '{normalized_header_name}'.",
            ).to_be_visible()
            return table

        lookup_column = normalized_table_column or normalized_column
        if lookup_column:
            tables = (
                ComponentUtils.unwrap_scope(scope).locator("table").filter(visible=True)
            )
            for index in range(tables.count()):
                table = tables.nth(index)
                if AppianTable.__has_column(table, lookup_column):
                    return table
            raise ValueError(f"No visible table contains column '{lookup_column}'.")

        table = (
            ComponentUtils.unwrap_scope(scope)
            .locator("table")
            .filter(visible=True)
            .first
        )
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
        label: str,
        row_number: int,
        excat_match: bool = False,
        column_name: Optional[str] = None,
        header_name: str = "",
    ) -> Locator:
        """
        Return a one-based data row.

        ``row_number`` refers to rows inside ``tbody`` only. The table
        header is not included in the row number.
        """
        if row_number < 1:
            raise ValueError("Row number must be 1 or greater.")

        table = AppianTable.__get_table(
            scope,
            label,
            excat_match,
            column_name,
            header_name,
        )

        rows = AppianTable.__get_data_rows(table)

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

        rows = AppianTable.__get_data_rows(table)

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
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        excat_match: bool = False,
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> Locator:
        """Resolve a table cell from flexible table/row/column identifiers.

        Table precedence: ``label`` > ``header_name`` >
        ``table_column_name`` > target ``column_name`` > first visible table.

        Row precedence: ``row_number`` > ``row_name``.
        Column precedence: ``column_number`` > ``column_name``.

        Row and column numbers are one-based.
        """
        table = AppianTable.__get_table(
            scope,
            label=label,
            excat_match=excat_match,
            column_name=column_name,
            header_name=header_name,
            table_column_name=table_column_name,
        )

        if row_number is not None:
            if row_number < 1:
                raise ValueError("Row number must be 1 or greater.")
            rows = AppianTable.__get_data_rows(table)
            row = rows.nth(row_number - 1)
            expect(
                row,
                f"Data row {row_number} was not available in the resolved table.",
            ).to_be_visible()
            row_description = str(row_number)
        else:
            normalized_row_name = str(row_name or "").strip()
            if not normalized_row_name:
                raise ValueError(
                    "Specify row_number or row_name to locate a table cell."
                )
            row = AppianTable.__get_row_by_name(table, normalized_row_name, excat_match)
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
            column_index = AppianTable.__get_column_index(table, normalized_column_name)
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
        label: str,
        row_name: str,
        column_name: str,
        excat_match: bool = False,
        header_name: str = "",
        table_column_name: Optional[str] = None,
    ) -> Locator:
        """Compatibility wrapper for named-row/named-column cell lookup."""
        return AppianTable.__get_cell(
            scope=scope,
            label=label,
            row_name=row_name,
            column_name=column_name,
            excat_match=excat_match,
            header_name=header_name,
            table_column_name=table_column_name,
        )

    @staticmethod
    def get_row_count(
        scope: Scope,
        label: str = "",
        column_name: Optional[str] = None,
        header_name: str = "",
        table_column_name: Optional[str] = None,
    ) -> int:
        """Count visible data rows in a resolved Appian table.

        Identify the table by region or heading text when ``label`` is
        supplied. Otherwise, optionally use a visible column header and finally
        fall back to the first visible table. Empty-grid placeholder rows are
        excluded.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Optional region or heading text identifying the table.
            column_name: Optional header used when no table name is available.
            header_name: Optional accessible header name identifying the table container.
            table_column_name: Optional visible column header used to resolve the table within a region.

        Returns:
            int: Number of visible body rows containing actual data.
        """
        table = AppianTable.__get_table(
            scope,
            label=label,
            column_name=column_name,
            header_name=header_name,
            table_column_name=table_column_name,
        )

        return AppianTable.__get_data_rows(table).count()

    @staticmethod
    def get_cell(
        scope: Scope,
        label: str = "",
        header_name: str = "",
        table_column_name: Optional[str] = None,
        row_number: Optional[int] = None,
        row_name: str = "",
        column_number: Optional[int] = None,
        column_name: str = "",
        excat_match: bool = False,
    ) -> Locator:
        """Return a visible table cell using flexible semantic selectors.

        Table: label > header_name > table_column_name > column_name.
        Row: row_number > row_name.
        Column: column_number > column_name.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            header_name: Optional header name used to narrow the lookup.
            table_column_name: Optional table-column identifier used when resolving a cell.
            row_number: One-based row number of the target table row.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            column_name: Visible column header identifying the target column.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            Locator: The matching table cell locator.
        """
        return AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
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
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> str:
        """Read text from a resolved table cell.

        Table lookup uses label, header_name, or a column name.
        Cell lookup accepts row_number or row_name and column_number or
        column_name. Numeric selectors take precedence when both are supplied.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            header_name: Optional header name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.


        Returns:
            str: The visible text from the matching table cell.
        """
        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
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
        label: str,
        row_name: str,
        column_name: str,
    ) -> str:
        """Return text from a named-row/named-column intersection.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.


        Returns:
            str: The visible text from the requested cell in the named row.
        """
        cell = AppianTable.__get_cell_by_named_row(
            scope,
            label,
            row_name,
            column_name,
        )

        return cell.inner_text().strip()

    @staticmethod
    def fill_input_in_named_row(
        scope: Scope,
        label: str = "",
        row_name: str = "",
        column_name: str = "",
        value: str = "",
        header_name: str = "",
    ) -> None:
        """Fill a text input or textarea at a named-row/column intersection.

        This supports Appian TextInput and ParagraphWidget controls because
        both expose textbox semantics to browser automation.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            header_name: Optional header name used to narrow the lookup.
        """
        cell = AppianTable.__get_cell_by_named_row(
            scope,
            label,
            row_name,
            column_name,
            header_name=header_name,
        )

        textbox = cell.get_by_role("textbox").filter(visible=True).first

        expect(
            textbox,
            (
                f"Text input was not found in row "
                f"'{row_name}', column '{column_name}'."
            ),
        ).to_be_visible()

        expect(textbox, "Text input was not enabled.").to_be_enabled()
        textbox.fill(str(value or ""))

        logger.debug(
            "Filled '%s' in row '%s', column '%s'.",
            value,
            row_name,
            column_name,
        )

    @staticmethod
    def fill_input_in_cell(
        scope: Scope,
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a textbox using flexible table/row/column selectors.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            header_name: Optional header name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        textbox = cell.get_by_role("textbox").filter(visible=True).first
        expect(
            textbox, "Text input was not found in the resolved table cell."
        ).to_be_visible()
        expect(textbox, "Text input was not enabled.").to_be_enabled()
        textbox.fill(str(value or ""))

    @staticmethod
    def fill_date_in_named_row(
        scope: Scope,
        label: str = "",
        row_name: str = "",
        column_name: str = "",
        value: str = "",
        header_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a date input at a named row and resolved column.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            header_name: Optional header name used to narrow the lookup.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
            table_column_name=table_column_name,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        date_input = (
            cell.locator('input[placeholder="mm/dd/yyyy"]').filter(visible=True).first
        )
        expect(
            date_input, "Date input was not found in the resolved table cell."
        ).to_be_visible()
        AppianDate.fill_locator(date_input, value)

    @staticmethod
    def select_dropdown_in_cell(
        scope: Scope,
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        option_name: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Select a dropdown using flexible table/row/column selectors.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
            header_name: Optional header name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        from .appian_page import AppianPage

        appian_cell = AppianCell(cell, page=AppianPage.get(cell.page))
        appian_cell.dropdown[0].select(value=option_name)
        logger.debug("Selected '%s' in resolved table cell.", option_name)

    @staticmethod
    def select_dropdown_in_named_row(
        scope: Scope,
        label: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a dropdown at a named-row/named-column intersection.

        Example:
            row_name="Registration Type"
            column_name="ROBO APPIAN"
            option_name="Other"

        AppianTable locates the cell and delegates dropdown interaction to AppianDropdown.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
        """
        cell = AppianTable.__get_cell_by_named_row(
            scope,
            label,
            row_name,
            column_name,
        )

        from .appian_page import AppianPage

        appian_cell = AppianCell(cell, page=AppianPage.get(cell.page))
        appian_cell.dropdown[0].select(value=option_name)

        logger.debug(
            ("Selected '%s' from dropdown " "in row '%s', column '%s'."),
            option_name,
            row_name,
            column_name,
        )

    @staticmethod
    def select_search_input_in_named_row(
        scope: Scope,
        label: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a value from an Appian SearchInput in a named table row.

        AppianTable resolves the row/column intersection and SearchInput.
        SearchInput performs the actual picker interaction.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
        """
        cell = AppianTable.__get_cell_by_named_row(
            scope,
            label,
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
        label: str,
        row_number: int,
        column_name: str,
    ) -> str:
        """Return normalized text from a table cell.

        This public compatibility API delegates to ``get_cell_text``.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.


        Returns:
            str: The value associated with the requested label in the table cell.
        """
        return AppianTable.get_cell_text(scope, label, row_number, column_name)

    @staticmethod
    def fill_textbox_in_cell(
        scope: Scope,
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a textbox using flexible table/row/column selectors.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            header_name: Optional header name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        AppianTable.fill_input_in_cell(
            scope=scope,
            label=label,
            row_number=row_number,
            column_name=column_name,
            value=value,
            header_name=header_name,
            row_name=row_name,
            column_number=column_number,
            table_column_name=table_column_name,
        )

    @staticmethod
    def fill_date_in_cell(
        scope: Scope,
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Fill a date control using flexible table/row/column selectors.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            header_name: Optional header name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        date_input = (
            cell.locator('input[placeholder="mm/dd/yyyy"]').filter(visible=True).first
        )
        expect(
            date_input, "Date input was not found in the resolved table cell."
        ).to_be_visible()
        AppianDate.fill_locator(date_input, value)

    @staticmethod
    def select_radio_in_cell(
        scope: Scope,
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        value: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
    ) -> None:
        """Select a radio option using flexible table/row/column selectors.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            value: Value to enter or select.
            header_name: Optional header name used to narrow the lookup.
            row_name: Visible text identifying the target row.
            column_number: One-based column number used when a column name is unavailable.
            table_column_name: Optional table-column identifier used when resolving a cell.
        """
        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
        )
        AppianTable.__select_radio_option(cell, value)

    @staticmethod
    def click_link_in_cell(
        scope: Scope,
        label: str = "",
        row_number: Optional[int] = None,
        column_name: str = "",
        link_name: str = "",
        header_name: str = "",
        row_name: str = "",
        column_number: Optional[int] = None,
        table_column_name: Optional[str] = None,
        exact: bool = True,
    ) -> None:
        """Click a semantic link contained in a resolved Appian table cell.

        AppianTable owns table/row/cell resolution. The link itself is resolved by
        Playwright's semantic ``link`` role inside that cell, so native
        ``<a>`` links and other elements exposed with ``role="link"`` are
        supported without relying on Appian CSS classes.

        Row and column numbers are one-based. Numeric selectors take
        precedence when both numeric and named selectors are supplied.
        """
        normalized_link = str(link_name or "").strip()
        if not normalized_link:
            raise ValueError("Link name cannot be empty or whitespace.")

        cell = AppianTable.__get_cell(
            scope=scope,
            label=label,
            header_name=header_name,
            table_column_name=table_column_name,
            row_number=row_number,
            row_name=row_name,
            column_number=column_number,
            column_name=column_name,
            excat_match=exact,
        )

        from .appian_page import AppianPage

        appian_cell = AppianCell(cell, page=AppianPage.get(cell.page))
        appian_cell.link(name=normalized_link, exact=exact).click()
        logger.debug(
            "Clicked link '%s' in resolved Appian table cell.",
            normalized_link,
        )

    @staticmethod
    def click_action_in_cell(
        scope: Scope,
        label: str,
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
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            column_name: Visible column header identifying the target column.
            action_label: Visible label of the action to invoke.
            excat_match: Whether matching must use the complete label or text.
        """
        normalized_action = str(action_label or "").strip()
        if not normalized_action:
            raise ValueError("Action label cannot be empty or whitespace.")

        cell = AppianTable.__get_cell(
            scope,
            label,
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
                f"'{label}', row {row_number}, column '{column_name}'."
            )

        expect(
            action,
            (
                f"Action '{normalized_action}' was not visible in table "
                f"'{label}', row {row_number}, column '{column_name}'."
            ),
        ).to_be_visible()

        ComponentUtils.click(action)

        logger.debug(
            "Clicked action '%s' in table '%s', row %s, column '%s'.",
            normalized_action,
            label,
            row_number,
            column_name,
        )

    @staticmethod
    def click_row(
        scope: Scope,
        label: str,
        row_number: int,
        excat_match: bool = False,
    ) -> None:
        """Click a one-based data row in a named Appian table.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_number: One-based row number of the target table row.
            excat_match: Whether matching must use the complete label or text.
        """
        row = AppianTable.__get_row_by_index(
            scope,
            label,
            row_number,
            excat_match,
        )
        ComponentUtils.click(row)

    @staticmethod
    def click_checkbox_in_named_row(
        scope: Scope,
        label: str,
        row_name: str,
        checked: bool = True,
    ) -> None:
        """Check or uncheck the checkbox contained in a named table row.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            checked: Desired checkbox state.
        """
        table = AppianTable.__get_table(scope, label=label)
        row = AppianTable.__get_row_by_name(
            table,
            row_name,
            excat_match=False,
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
        label: str,
        row_name: str,
        column_name: str,
        option_name: str,
    ) -> None:
        """Select a radio option from a named-row/column intersection.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible name of the target table.
            row_name: Visible text identifying the target row.
            column_name: Visible column header identifying the target column.
            option_name: Visible option text to select.
        """
        cell = AppianTable.__get_cell_by_named_row(
            scope,
            label,
            row_name,
            column_name,
            excat_match=False,
        )

        AppianTable.__select_radio_option(
            cell,
            option_name,
        )

        logger.debug(
            ("Selected radio option '%s' " "in row '%s', column '%s'."),
            option_name,
            row_name,
            column_name,
        )


__all__ = ["AppianTable"]
