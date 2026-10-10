"""Appian table cell component abstraction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator

from .appian_button import AppianButton
from .appian_checkbox import AppianCheckbox
from .appian_component_accessor import AppianComponentAccessor
from .appian_date import AppianDate
from .appian_dropdown import AppianDropdown
from .appian_link import AppianLink
from .appian_locator import AppianLocator
from .appian_radio_select import AppianRadioSelect
from .appian_tab import AppianTab
from .appian_textbox import AppianTextbox

if TYPE_CHECKING:
    from .appian_page import AppianPage
    from robo_appian.appian.appian_table import AppianTable


class AppianCell(AppianLocator):
    """Represent a resolved Appian table cell and its scoped components.

    ``AppianCell`` remains an ``AppianLocator``, so the normal locator surface is
    still available. Appian components can be resolved either semantically or by
    zero-based index when a table cell does not expose a field label/name::

        cell.dropdown(label="CAN").select(value="12345")
        cell.dropdown[0].select(value="12345")
        cell.button[0].click()

    Index access is intentionally zero-based Python indexing. Component-specific
    option indexes, such as ``dropdown.select(index=1)``, keep their documented
    one-based semantics.
    """

    def __init__(self, locator: Locator, *, page: "AppianPage") -> None:
        # AppianLocator/RoboLocator normally builds a locator from attributes.
        # A table cell is already resolved, so retain that live locator directly.
        self.scope = locator
        self.attributes = {}
        self.excat_match = None
        self._locator = locator
        self._page = page

    def _visible_nth(self, locator: Locator, index: int) -> Locator:
        """Return the zero-based visible component match inside this cell."""
        return locator.filter(visible=True).nth(index)

    # ------------------------------------------------------------------
    # Semantic factories used by the public short accessors
    # ------------------------------------------------------------------
    def _button_factory(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianButton:
        """Return an Appian button scoped to this cell."""
        return AppianButton(
            page=self._page,
            name=name,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _textbox_factory(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTextbox:
        """Return an Appian textbox scoped to this cell."""
        return AppianTextbox(
            page=self._page,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _dropdown_factory(
        self,
        *,
        label: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDropdown:
        """Return an Appian dropdown scoped to this cell."""
        return AppianDropdown(
            page=self._page,
            label=label,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _checkbox_factory(
        self,
        *,
        label: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianCheckbox:
        """Return an Appian checkbox scoped to this cell."""
        return AppianCheckbox(
            page=self._page,
            label=label,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _radio_factory(
        self,
        *,
        label: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianRadioSelect:
        """Return an Appian radio group scoped to this cell."""
        return AppianRadioSelect(
            page=self._page,
            label=label,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _link_factory(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianLink:
        """Return an Appian link scoped to this cell."""
        return AppianLink(
            page=self._page,
            name=name,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _tab_factory(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTab:
        """Return an Appian tab scoped to this cell."""
        return AppianTab(
            page=self._page,
            name=name,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _date_factory(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDate:
        """Return an Appian date field scoped to this cell."""
        return AppianDate(
            page=self._page,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    def _table_factory(
        self,
        *,
        label: str | None = None,
        header_name: str | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> "AppianTable":
        """Return a nested Appian table scoped to this cell."""
        from robo_appian.appian.appian_table import AppianTable

        return AppianTable(
            self,
            label=label,
            header_name=header_name,
            row_name=row_name,
            column_name=column_name,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Short callable/indexable accessors
    # ------------------------------------------------------------------
    @property
    def button(self) -> AppianComponentAccessor[AppianButton]:
        def indexed(index: int) -> AppianButton:
            component = AppianButton(
                page=self._page, name=f"button[{index}]", scope=self
            )
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("button[type='button']"), index
            )
            return component

        return AppianComponentAccessor(
            self._button_factory, indexed, component_name="button"
        )

    @property
    def textbox(self) -> AppianComponentAccessor[AppianTextbox]:
        def indexed(index: int) -> AppianTextbox:
            component = AppianTextbox(
                page=self._page, label=f"textbox[{index}]", scope=self
            )
            raw = self.locator.locator(
                "xpath=.//input[(@type='text' or @type='password') and "
                "not(@data-testid='DatePickerWidget-textInput')] | "
                ".//textarea[@role='textbox']"
            )
            component._indexed_locator = self._visible_nth(raw, index)  # type: ignore[attr-defined]
            return component

        return AppianComponentAccessor(
            self._textbox_factory, indexed, component_name="textbox"
        )

    @property
    def dropdown(self) -> AppianComponentAccessor[AppianDropdown]:
        def indexed(index: int) -> AppianDropdown:
            component = AppianDropdown(
                page=self._page,
                label=f"dropdown[{index}]",
                scope=self,
            )
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("[role='combobox']"), index
            )
            return component

        return AppianComponentAccessor(
            self._dropdown_factory, indexed, component_name="dropdown"
        )

    @property
    def checkbox(self) -> AppianComponentAccessor[AppianCheckbox]:
        def indexed(index: int) -> AppianCheckbox:
            component = AppianCheckbox(
                page=self._page,
                label=f"checkbox[{index}]",
                scope=self,
            )
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("input[type='checkbox']"), index
            )
            return component

        return AppianComponentAccessor(
            self._checkbox_factory, indexed, component_name="checkbox"
        )

    @property
    def radio(self) -> AppianComponentAccessor[AppianRadioSelect]:
        def indexed(index: int) -> AppianRadioSelect:
            component = AppianRadioSelect(
                page=self._page,
                label=f"radio[{index}]",
                scope=self,
            )
            groups = self.locator.locator(
                "xpath=.//*[@role='radiogroup' or "
                "(@role='group' and .//input[@type='radio'])]"
            )
            component._indexed_locator = self._visible_nth(groups, index)  # type: ignore[attr-defined]
            return component

        return AppianComponentAccessor(
            self._radio_factory, indexed, component_name="radio"
        )

    @property
    def link(self) -> AppianComponentAccessor[AppianLink]:
        def indexed(index: int) -> AppianLink:
            component = AppianLink(page=self._page, name=f"link[{index}]", scope=self)
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.get_by_role("link"), index
            )
            return component

        return AppianComponentAccessor(
            self._link_factory, indexed, component_name="link"
        )

    @property
    def tab(self) -> AppianComponentAccessor[AppianTab]:
        def indexed(index: int) -> AppianTab:
            component = AppianTab(page=self._page, name=f"tab[{index}]", scope=self)
            state = self.locator.get_by_text(AppianTab._STATE_PATTERN)
            tabs = self.locator.get_by_role("link").filter(has=state)
            component._indexed_locator = self._visible_nth(tabs, index)  # type: ignore[attr-defined]
            return component

        return AppianComponentAccessor(self._tab_factory, indexed, component_name="tab")

    @property
    def date(self) -> AppianComponentAccessor[AppianDate]:
        def indexed(index: int) -> AppianDate:
            component = AppianDate(page=self._page, label=f"date[{index}]", scope=self)
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("input[data-testid='DatePickerWidget-textInput']"),
                index,
            )
            return component

        return AppianComponentAccessor(
            self._date_factory, indexed, component_name="date"
        )

    @property
    def table(self) -> AppianComponentAccessor["AppianTable"]:
        from robo_appian.appian.appian_table import AppianTable

        def indexed(index: int) -> AppianTable:
            component = AppianTable(self, label=f"table[{index}]")
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("table"), index
            )
            return component

        return AppianComponentAccessor(
            self._table_factory, indexed, component_name="table"
        )


__all__ = ["AppianCell"]
