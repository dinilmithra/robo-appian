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

    def __normalize_optional_identifier(self, value: str | None, name: str) -> str | None:
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
                "AppianTable.cell row_name cannot be empty or whitespace."
            )
        if row_number is not None and row_number < 1:
            raise ValueError("AppianTable.cell row_number must be 1 or greater.")

        normalized_column = (
            None if column_name is None else " ".join(str(column_name).split())
        )
        if column_name is not None and not normalized_column:
            raise ValueError(
                "AppianTable.cell column_name cannot be empty or whitespace."
            )
        if column_number is not None and column_number < 1:
            raise ValueError(
                "AppianTable.cell column_number must be 1 or greater."
            )

        effective_row_name = normalized_row
        if effective_row_name is None and row_number is None:
            effective_row_name = self._component_row_name
        if effective_row_name is None and row_number is None:
            raise ValueError(
                "AppianTable.cell requires row_name or row_number, "
                "unless the table was created with row_name."
            )

        effective_column_name = normalized_column
        if effective_column_name is None and column_number is None:
            effective_column_name = self._component_column_name
        if effective_column_name is None and column_number is None:
            raise ValueError(
                "AppianTable.cell requires column_name or column_number, "
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


    def column(
        self,
        *,
        name: str | None = None,
        column_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ):
        """Return a semantic column scoped to this table."""
        return self.appian_column(
            name=name,
            column_number=column_number,
            visible=visible,
            exact=exact,
        )

    def row_count(
        self,
        *,
        visible: bool | str | None = None,
        timeout: float | int | None = None,
    ) -> int:
        """Return the number of currently rendered data rows.

        Header rows and Appian paging totals are not counted. ``timeout`` waits
        only for the table to exist; it does not wait for an empty table to gain
        rows.
        """
        table = self.locator
        effective_timeout = ComponentUtils.normalize_timeout_seconds(timeout)
        kwargs = ComponentUtils.timeout_kwargs(effective_timeout)
        expect(table.first, "Appian table was not found.").to_be_attached(**kwargs)
        rows = table.first.locator("tbody tr")
        normalized_visible = ComponentUtils.normalize_visibility(visible)
        if normalized_visible is not None:
            rows = rows.filter(visible=normalized_visible)
        return rows.count()

    def click_row(self, *, row_number: int) -> None:
        """Click a one-based rendered data row."""
        self.row(row_number=row_number).select()

    def click_action_in_cell(
        self,
        *,
        row_number: int,
        column_name: str,
        action_label: str,
        exact: bool = False,
    ) -> None:
        """Click a link or button action in a resolved table cell."""
        normalized = " ".join(str(action_label or "").split())
        if not normalized:
            raise ValueError("Action label cannot be empty or whitespace.")
        cell = self.cell(row_number=row_number, column_name=column_name)
        actions = cell.locator.locator("a, button").filter(visible=True)
        for index in range(actions.count()):
            candidate = actions.nth(index)
            text = " ".join((candidate.text_content() or "").split())
            matched = text == normalized if exact else normalized in text
            if not matched:
                labels = candidate.locator("[aria-label]")
                for label_index in range(labels.count()):
                    aria = " ".join((labels.nth(label_index).get_attribute("aria-label") or "").split())
                    if (aria == normalized if exact else normalized in aria):
                        matched = True
                        break
            if matched:
                expect(candidate, f"Action '{normalized}' was not visible.").to_be_visible()
                ComponentUtils.click(candidate)
                return
        raise AssertionError(f"Action '{normalized}' was not found in the resolved table cell.")

    def select_dropdown_in_cell(
        self,
        *,
        option_name: str,
        row_number: int | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        column_number: int | None = None,
    ) -> None:
        """Select the first dropdown in a resolved table cell."""
        self.cell(
            row_number=row_number,
            row_name=row_name,
            column_name=column_name,
            column_number=column_number,
        ).dropdown[0].select(value=option_name)

    def select_dropdown_in_named_row(
        self, *, row_name: str, column_name: str, option_name: str
    ) -> None:
        """Select the first dropdown at a named row/column intersection."""
        self.select_dropdown_in_cell(
            row_name=row_name, column_name=column_name, option_name=option_name
        )

    def fill_input_in_named_row(
        self, *, row_name: str, column_name: str, value: str
    ) -> None:
        """Fill the first textbox at a named row/column intersection."""
        self.cell(row_name=row_name, column_name=column_name).textbox[0].fill(value)

    def fill_textbox_in_cell(
        self,
        *,
        value: str,
        row_number: int | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        column_number: int | None = None,
    ) -> None:
        """Fill the first textbox in a resolved table cell."""
        self.cell(
            row_number=row_number,
            row_name=row_name,
            column_name=column_name,
            column_number=column_number,
        ).textbox[0].fill(value)

    def fill_date_in_cell(
        self,
        *,
        value: str,
        row_number: int | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        column_number: int | None = None,
    ) -> None:
        """Fill the first date component in a resolved table cell."""
        self.cell(
            row_number=row_number,
            row_name=row_name,
            column_name=column_name,
            column_number=column_number,
        ).date[0].fill(value)

    def fill_date_in_named_row(
        self, *, row_name: str, column_name: str, value: str
    ) -> None:
        """Fill the first date component at a named row/column intersection."""
        self.fill_date_in_cell(row_name=row_name, column_name=column_name, value=value)

    def get_label_value_in_cell(
        self, *, row_number: int, column_name: str
    ) -> str:
        """Return normalized visible text from a resolved table cell."""
        text = self.cell(row_number=row_number, column_name=column_name).locator.inner_text()
        return " ".join(text.split())

    def select_search_input_in_named_row(
        self, *, row_name: str, column_name: str, option_name: str
    ) -> None:
        """Select a value from a searchable picker in a named table cell."""
        cell = self.cell(row_name=row_name, column_name=column_name)
        search_input = cell.locator.get_by_role("combobox").filter(visible=True).first
        expect(search_input, "Search input was not found in the resolved table cell.").to_be_visible()
        SearchInput.select_by_locator(
            scope=self._component_scope,
            lookup=search_input,
            search_text=option_name,
            field_name=row_name,
        )


__all__ = ["AppianTable"]
