"""Appian table column component abstraction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator

from robo_appian.appian.appian_cell import AppianCell
from robo_appian.utils.ComponentUtils import ComponentUtils

if TYPE_CHECKING:
    from .appian_table import AppianTable


class AppianColumn:
    """Represent a semantic column inside an already-resolved Appian table."""

    def __init__(
        self,
        table: "AppianTable",
        *,
        name: str | None = None,
        column_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ) -> None:
        normalized_name = None if name is None else " ".join(str(name).split())
        if name is not None and not normalized_name:
            raise ValueError("AppianColumn name cannot be empty or whitespace.")
        if column_number is not None and column_number < 1:
            raise ValueError("AppianColumn column_number must be 1 or greater.")
        if normalized_name is None and column_number is None:
            raise ValueError("AppianColumn requires name or column_number.")

        self._table = table
        self._name = normalized_name
        self._column_number = column_number
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._exact = exact

    @property
    def visible(self) -> bool | None:
        return self._visible

    @property
    def column_index(self) -> int:
        """Return the zero-based column index within the resolved table."""
        if self._column_number is not None:
            return self._column_number - 1
        return self._table._column_index(self._name or "", exact=self._exact)

    @property
    def locator(self) -> Locator:
        """Return the live locator for the column header."""
        headers = self._table.locator.locator("thead th")
        header = headers.nth(self.column_index)
        if self._visible is not None:
            header = header.filter(visible=self._visible)
        return header

    def cell(
        self,
        *,
        row_name: str | None = None,
        row_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ) -> AppianCell:
        """Return the Appian cell at this column and the requested table row."""
        row = self._table.row(
            name=row_name,
            row_number=row_number,
            visible=None,
            exact=exact,
        )
        cell = row.locator.locator("td").nth(self.column_index)
        normalized_visible = ComponentUtils.normalize_visibility(visible)
        if normalized_visible is not None:
            cell = cell.filter(visible=normalized_visible)
        return AppianCell(cell, page=self._table.appian_page)


__all__ = ["AppianColumn"]
