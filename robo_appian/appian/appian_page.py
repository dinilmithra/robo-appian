"""Appian-specific page wrapper."""

from __future__ import annotations

from typing import Any, Mapping

from playwright.sync_api import Page

from robo_automation import RoboAutomationError, RoboPage

from robo_appian.errors import RoboAppianNavigationError

from .appian_button import AppianButton
from .appian_checkbox import AppianCheckbox
from .appian_component_accessor import AppianComponentAccessor
from .appian_date import AppianDate
from .appian_dropdown import AppianDropdown
from .appian_radio_select import AppianRadioSelect
from .appian_textbox import AppianTextbox
from .appian_tab import AppianTab
from .appian_link import AppianLink
from .appian_locator import AppianLocator
from robo_appian.appian.appian_table import AppianTable


class AppianPage:
    """Transparent Appian wrapper around ``RoboPage``.

    Appian-specific helpers are additive. Unknown attributes and methods are
    delegated to ``RoboPage``, which in turn delegates to underlying page.
    This preserves the complete underlying page API on an AppianPage object.
    """

    locator_class = AppianLocator

    def __init__(self, robo_page: RoboPage) -> None:
        if not isinstance(robo_page, RoboPage):
            raise TypeError("AppianPage requires a RoboPage.")
        self._robo_page = robo_page

    @classmethod
    def get(cls, page: Page | RoboPage | "AppianPage") -> "AppianPage":
        """Return an Appian wrapper around a RoboPage or underlying page."""
        if isinstance(page, cls):
            return page
        return cls(RoboPage.get(page))

    @property
    def robo_page(self) -> RoboPage:
        """Return the wrapped RoboPage."""
        return self._robo_page

    def __getattr__(self, name: str) -> Any:
        """Delegate unknown attributes through RoboPage to underlying page."""
        return getattr(self._robo_page, name)

    def __dir__(self) -> list[str]:
        """Include RoboPage and underlying page members in introspection."""
        return sorted(set(super().__dir__()) | set(dir(self._robo_page)))

    def same_page(self, other: object) -> bool:
        """Return whether another wrapper owns the same underlying page."""
        if isinstance(other, AppianPage):
            other = other.robo_page
        return isinstance(other, RoboPage) and self._robo_page.same_page(other)

    def same_context(self, other: object) -> bool:
        """Return whether another wrapper belongs to the same browser context."""
        if isinstance(other, AppianPage):
            other = other.robo_page
        return isinstance(other, RoboPage) and self._robo_page.same_context(other)

    def open_pages(self) -> list["AppianPage"]:
        """Return Appian wrappers for open pages in the current context."""
        return [type(self).get(page) for page in self._robo_page.open_pages()]

    def get_by_attributes(
        self,
        attributes: Mapping[str, Any],
        excat_match: bool | None = None,
    ) -> AppianLocator:
        """Return an AppianLocator found by arbitrary HTML attributes."""
        return self.locator_class.get_by_attributes(
            self._robo_page._page,
            attributes=attributes,
            excat_match=excat_match,
        )

    def get_by_id(
        self,
        element_id: str,
        excat_match: bool | None = None,
    ) -> AppianLocator:
        """Return an AppianLocator found by HTML id."""
        return self.locator_class.get_by_id(
            self._robo_page._page,
            element_id=element_id,
            excat_match=excat_match,
        )

    def goto(self, url: str, **kwargs):
        """Navigate to an Appian URL using the public Appian error boundary."""
        try:
            return self._robo_page.goto(url, **kwargs)
        except RoboAutomationError as exc:
            code = (
                "ROBO_APPIAN_NAVIGATION_ABORTED"
                if getattr(exc, "code", "") == "ROBO_NAVIGATION_ABORTED"
                else "ROBO_APPIAN_NAVIGATION_ERROR"
            )
            raise RoboAppianNavigationError(
                str(exc),
                code=code,
                details=getattr(exc, "details", None),
            ) from exc

    def reload(self, **kwargs):
        """Reload an Appian page using the public Appian error boundary."""
        try:
            return self._robo_page.reload(**kwargs)
        except RoboAutomationError as exc:
            raise RoboAppianNavigationError(
                str(exc),
                code="ROBO_APPIAN_RELOAD_ERROR",
                details=getattr(exc, "details", None),
            ) from exc

    def _button_factory(
        self,
        *,
        name: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianButton:
        """Return an Appian button component identified by ``name``.

        Args:
            name: Visible or accessible button name.
            exact: Whether the complete normalized button name must match.
            scope: Optional locator scope used to restrict the button search.

        Returns:
            The Appian button component bound to this page.
        """
        return AppianButton(
            page=self,
            name=name,
            exact=exact,
            scope=scope,
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
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTextbox:
        """Return an Appian textbox identified by label, placeholder, or header.

        Specify exactly one identifier. Header lookup binds the matching header
        text to the first supported textbox that follows it.
        """
        return AppianTextbox(
            page=self,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            scope=scope,
            visible=visible,
            timeout=timeout,
        )

    def _dropdown_factory(
        self,
        *,
        label: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDropdown:
        """Return an Appian dropdown identified by its field label.

        Resolution follows Appian's accessibility relationships: the field
        label id is referenced by the combobox ``aria-labelledby`` attribute,
        and the combobox links to its option list through ``aria-controls``.
        """
        return AppianDropdown(
            page=self,
            label=label,
            exact=exact,
            scope=scope,
            visible=visible,
            timeout=timeout,
        )

    def _checkbox_factory(
        self,
        *,
        label: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianCheckbox:
        """Return an Appian checkbox identified by visible label text."""
        return AppianCheckbox(
            page=self,
            label=label,
            exact=exact,
            scope=scope,
            visible=visible,
            timeout=timeout,
        )

    def _radio_factory(
        self,
        *,
        label: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianRadioSelect:
        """Return an Appian radio group identified by its field label."""
        return AppianRadioSelect(
            page=self,
            label=label,
            exact=exact,
            scope=scope,
            visible=visible,
            timeout=timeout,
        )

    def _link_factory(
        self,
        *,
        name: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianLink:
        """Return an Appian link identified by its accessible/visible name."""
        return AppianLink(
            page=self,
            name=name,
            exact=exact,
            scope=scope,
            visible=visible,
            timeout=timeout,
        )

    def _tab_factory(
        self,
        *,
        name: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTab:
        """Return an Appian tab identified by its visible tab name."""
        return AppianTab(
            page=self,
            name=name,
            exact=exact,
            scope=scope,
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
    ) -> AppianTable:
        """Return an Appian table identified by one or more semantic hints.

        At least one of ``label``, ``header_name``, ``row_name``, or
        ``column_name`` is required. ``visible=True`` selects visible tables,
        ``visible=False`` selects hidden tables, and ``visible=None`` applies
        no visibility filter so both visible and hidden matches are retained.
        """
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

    def _date_factory(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        scope: AppianLocator | None = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDate:
        """Return an Appian date field identified by label, placeholder, or header."""
        return AppianDate(
            page=self,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            scope=scope,
            visible=visible,
            timeout=timeout,
        )

    # Public Appian component accessors. Names intentionally omit the redundant
    # ``appian_`` prefix because the containing object is already AppianPage.
    def _page_nth(self, selector: str, index: int):
        return self.locator(selector).filter(visible=True).nth(index)

    @property
    def button(self) -> AppianComponentAccessor[AppianButton]:
        def indexed(index: int) -> AppianButton:
            component = AppianButton(page=self, name=f"button[{index}]")
            component._indexed_locator = (
                self.get_by_role("button").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentAccessor(
            self._button_factory, indexed, component_name="button"
        )

    @property
    def textbox(self) -> AppianComponentAccessor[AppianTextbox]:
        def indexed(index: int) -> AppianTextbox:
            component = AppianTextbox(page=self, label=f"textbox[{index}]")
            raw = self.locator(
                "xpath=.//input[(@type='text' or @type='password') and not(@data-testid='DatePickerWidget-textInput')] | .//textarea[@role='textbox']"
            )
            component._indexed_locator = raw.filter(visible=True).nth(index)
            return component

        return AppianComponentAccessor(
            self._textbox_factory, indexed, component_name="textbox"
        )

    @property
    def dropdown(self) -> AppianComponentAccessor[AppianDropdown]:
        def indexed(index: int) -> AppianDropdown:
            component = AppianDropdown(page=self, label=f"dropdown[{index}]")
            component._indexed_locator = (
                self.locator("[role='combobox']").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentAccessor(
            self._dropdown_factory, indexed, component_name="dropdown"
        )

    @property
    def checkbox(self) -> AppianComponentAccessor[AppianCheckbox]:
        def indexed(index: int) -> AppianCheckbox:
            component = AppianCheckbox(page=self, label=f"checkbox[{index}]")
            component._indexed_locator = (
                self.locator("input[type='checkbox']").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentAccessor(
            self._checkbox_factory, indexed, component_name="checkbox"
        )

    @property
    def radio(self) -> AppianComponentAccessor[AppianRadioSelect]:
        def indexed(index: int) -> AppianRadioSelect:
            component = AppianRadioSelect(page=self, label=f"radio[{index}]")
            groups = self.locator(
                "xpath=.//*[@role='radiogroup' or (@role='group' and .//input[@type='radio'])]"
            )
            component._indexed_locator = groups.filter(visible=True).nth(index)
            return component

        return AppianComponentAccessor(
            self._radio_factory, indexed, component_name="radio"
        )

    @property
    def link(self) -> AppianComponentAccessor[AppianLink]:
        def indexed(index: int) -> AppianLink:
            component = AppianLink(page=self, name=f"link[{index}]")
            component._indexed_locator = (
                self.get_by_role("link").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentAccessor(
            self._link_factory, indexed, component_name="link"
        )

    @property
    def tab(self) -> AppianComponentAccessor[AppianTab]:
        def indexed(index: int) -> AppianTab:
            component = AppianTab(page=self, name=f"tab[{index}]")
            state = self.get_by_text(AppianTab._STATE_PATTERN)
            component._indexed_locator = (
                self.get_by_role("link")
                .filter(has=state)
                .filter(visible=True)
                .nth(index)
            )
            return component

        return AppianComponentAccessor(self._tab_factory, indexed, component_name="tab")

    @property
    def date(self) -> AppianComponentAccessor[AppianDate]:
        def indexed(index: int) -> AppianDate:
            component = AppianDate(page=self, label=f"date[{index}]")
            component._indexed_locator = (
                self.locator("input[data-testid='DatePickerWidget-textInput']")
                .filter(visible=True)
                .nth(index)
            )
            return component

        return AppianComponentAccessor(
            self._date_factory, indexed, component_name="date"
        )

    @property
    def table(self) -> AppianComponentAccessor[AppianTable]:
        def indexed(index: int) -> AppianTable:
            component = AppianTable(self, label=f"table[{index}]")
            component._indexed_locator = (
                self.locator("table").filter(visible=True).nth(index)
            )
            return component

        return AppianComponentAccessor(
            self._table_factory, indexed, component_name="table"
        )


__all__ = ["AppianPage"]
