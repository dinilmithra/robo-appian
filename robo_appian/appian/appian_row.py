"""Appian table row component abstraction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator

from robo_appian.appian.appian_cell import AppianCell
from robo_appian.appian.appian_link import AppianLink
from robo_appian.appian.appian_locator import AppianLocator
from robo_appian.appian.appian_page import AppianPage
from robo_appian.utils.ComponentUtils import ComponentUtils

if TYPE_CHECKING:
    from .appian_table import AppianTable


class AppianRow:
    """Represent a semantic row inside an already-resolved Appian table."""

    def __init__(
        self,
        table: "AppianTable",
        *,
        name: str | None = None,
        row_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ) -> None:
        normalized_name = None if name is None else " ".join(str(name).split())
        if name is not None and not normalized_name:
            raise ValueError("AppianRow name cannot be empty or whitespace.")
        if row_number is not None and row_number < 1:
            raise ValueError("AppianRow row_number must be 1 or greater.")
        if normalized_name is None and row_number is None:
            raise ValueError("AppianRow requires name or row_number.")

        self._table = table
        self._name = normalized_name
        self._row_number = row_number
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._exact = exact

    @property
    def visible(self) -> bool | None:
        return self._visible

    @property
    def locator(self) -> Locator:
        rows = self._table.locator.locator("tbody tr")
        if self._name is not None:
            rows = rows.filter(has_text=self._name)
        if self._visible is not None:
            rows = rows.filter(visible=self._visible)
        if self._row_number is not None:
            return rows.nth(self._row_number - 1)
        if self._exact:
            literal = ComponentUtils.xpath_literal(self._name or "")
            return rows.locator(
                "xpath=self::tr[.//*[normalize-space(translate(string(.), '\u00a0', ' '))="
                + literal
                + "]]"
            ).first
        return rows.first

    def click(self) -> "AppianRow":
        """Click this row using its resolved row element.

        The row locator is resolved immediately before the click so Appian
        rerenders do not leave this component holding a stale element.
        """
        row = self.locator
        row.click()
        owner = self._table.appian_page
        page = owner if isinstance(owner, AppianPage) else AppianPage.get(owner)
        page.wait_for_appian_action_completed()
        return self

    def cell(
        self,
        *,
        column_name: str | None = None,
        column_number: int | None = None,
        visible: bool | str | None = True,
        exact: bool = True,
    ) -> AppianCell:
        """Return an Appian cell within this row by semantic column name or number."""
        normalized_column = (
            None if column_name is None else " ".join(str(column_name).split())
        )
        if column_name is not None and not normalized_column:
            raise ValueError(
                "AppianRow cell column_name cannot be empty or whitespace."
            )
        if column_number is not None and column_number < 1:
            raise ValueError("AppianRow cell column_number must be 1 or greater.")
        if normalized_column is None and column_number is None:
            normalized_column = self._table.column_name
        if normalized_column is None and column_number is None:
            raise ValueError(
                "AppianRow.cell requires column_name or column_number, "
                "unless the table was created with column_name."
            )

        if column_number is not None:
            column_index = column_number - 1
        else:
            column_index = self._table._column_index(
                normalized_column or "", exact=exact
            )

        cell = self.locator.locator("td").nth(column_index)
        normalized_visible = ComponentUtils.normalize_visibility(visible)
        if normalized_visible is not None:
            cell = cell.filter(visible=normalized_visible)
        return AppianCell(cell, page=self._table.appian_page)

    def link(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
    ) -> AppianLink:
        """Return an Appian link scoped to this row."""
        return AppianLink(
            page=self._table.appian_page,
            name=name,
            exact=exact,
            scope=self,  # AppianLink only requires a live ``locator`` property.
            visible=visible,
        )


__all__ = ["AppianRow"]
