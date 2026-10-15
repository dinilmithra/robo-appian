"""Appian grid cell component abstraction."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

from playwright.sync_api import Locator

from ..components.appian_button import AppianButton
from ..components.appian_checkbox import AppianCheckbox
from ..components.appian_component_collection import AppianComponentCollection
from ..components.appian_date import AppianDate
from ..components.appian_dropdown import AppianDropdown
from ..components.appian_link import AppianLink
from ..locator.appian_locator import AppianLocator
from ..components.appian_radio_select import AppianRadioSelect
from ..components.appian_tab import AppianTab
from ..components.appian_textbox import AppianTextbox

if TYPE_CHECKING:
    from robo_appian.appian.page.appian_page import AppianPage
    from robo_appian.appian.data.appian_grid import AppianGrid


ComponentType = TypeVar("ComponentType")


class _AppianNamedAccessor(AppianComponentCollection[ComponentType]):
    def __init__(
        self,
        factory: Callable[..., ComponentType],
        collection: AppianComponentCollection[ComponentType],
        *,
        name: str,
    ) -> None:
        super().__init__(collection.__getitem__, name=name)
        self._factory = factory

    def __call__(
        self,
        *,
        name: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> ComponentType:
        return self._factory(name=name, exact=exact, visible=visible, timeout=timeout)


class _AppianLabeledAccessor(AppianComponentCollection[ComponentType]):
    def __init__(
        self,
        factory: Callable[..., ComponentType],
        collection: AppianComponentCollection[ComponentType],
        *,
        name: str,
    ) -> None:
        super().__init__(collection.__getitem__, name=name)
        self._factory = factory

    def __call__(
        self,
        *,
        label: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> ComponentType:
        return self._factory(label=label, exact=exact, visible=visible, timeout=timeout)


class _AppianDateAccessor(AppianComponentCollection[AppianDate]):
    def __init__(self, cell: AppianCell) -> None:
        super().__init__(cell.dates.__getitem__, name="date")
        self._cell = cell

    def __call__(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDate:
        return self._cell._date_factory(
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )


class _AppianGridAccessor(AppianComponentCollection["AppianGrid"]):
    def __init__(self, cell: AppianCell) -> None:
        super().__init__(cell.grids.__getitem__, name="grid")
        self._cell = cell

    def __call__(
        self,
        *,
        label: str | None = None,
        header: str | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> "AppianGrid":
        return self._cell._grid_factory(
            label=label,
            header=header,
            row_name=row_name,
            column_name=column_name,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )


class _AppianTextboxAccessor(AppianComponentCollection[AppianTextbox]):
    def __init__(self, cell: AppianCell) -> None:
        super().__init__(cell.textboxes.__getitem__, name="textbox")
        self._cell = cell

    def __call__(
        self,
        label: str | None = None,
        *,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianTextbox:
        return self._cell._textbox_factory(
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )


class _AppianDropdownAccessor(AppianComponentCollection[AppianDropdown]):
    def __init__(self, cell: AppianCell) -> None:
        super().__init__(cell.dropdowns.__getitem__, name="dropdown")
        self._cell = cell

    def __call__(
        self,
        *,
        label: str,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianDropdown:
        return self._cell._dropdown_factory(
            label=label,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )


class AppianCell(AppianLocator):
    """Represent a resolved Appian grid cell and its scoped components.

    ``AppianCell`` remains an ``AppianLocator``, so the normal locator surface is
    still available. Component accessors accept semantic identifiers or resolve
    unlabeled components by zero-based position::

        cell.dropdown(label="CAN").select(value="12345")
        cell.dropdown[0].select(value="12345")
        cell.textbox[0].fill("Example")
        cell.date[0].fill("10/14/2026")
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

    def text(self) -> str:
        """Return normalized user-visible text from this resolved table cell."""
        return " ".join((self.locator.inner_text() or "").split())

    # ------------------------------------------------------------------
    # Semantic factories used by the public short accessors
    # ------------------------------------------------------------------
    @property
    def button(self) -> _AppianNamedAccessor[AppianButton]:
        """Return a callable, zero-based button accessor scoped to this cell."""
        return _AppianNamedAccessor(self._button_factory, self.buttons, name="button")

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

    @property
    def textbox(self) -> _AppianTextboxAccessor:
        """Return a callable, zero-based textbox accessor scoped to this cell."""
        return _AppianTextboxAccessor(self)

    def _textbox_factory(
        self,
        label: str | None = None,
        *,
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

    @property
    def dropdown(self) -> _AppianDropdownAccessor:
        """Return a callable, zero-based dropdown accessor scoped to this cell."""
        return _AppianDropdownAccessor(self)

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

    @property
    def checkbox(self) -> _AppianLabeledAccessor[AppianCheckbox]:
        """Return a callable, zero-based checkbox accessor scoped to this cell."""
        return _AppianLabeledAccessor(
            self._checkbox_factory, self.checkboxes, name="checkbox"
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

    @property
    def radio(self) -> _AppianLabeledAccessor[AppianRadioSelect]:
        """Return a callable, zero-based radio accessor scoped to this cell."""
        return _AppianLabeledAccessor(self._radio_factory, self.radios, name="radio")

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

    @property
    def link(self) -> _AppianNamedAccessor[AppianLink]:
        """Return a callable, zero-based link accessor scoped to this cell."""
        return _AppianNamedAccessor(self._link_factory, self.links, name="link")

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

    @property
    def tab(self) -> _AppianNamedAccessor[AppianTab]:
        """Return a callable, zero-based tab accessor scoped to this cell."""
        return _AppianNamedAccessor(self._tab_factory, self.tabs, name="tab")

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

    @property
    def date(self) -> _AppianDateAccessor:
        """Return a callable, zero-based date accessor scoped to this cell."""
        return _AppianDateAccessor(self)

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

    @property
    def grid(self) -> _AppianGridAccessor:
        """Return a callable, zero-based nested grid accessor scoped to this cell."""
        return _AppianGridAccessor(self)

    def _grid_factory(
        self,
        *,
        label: str | None = None,
        header: str | None = None,
        row_name: str | None = None,
        column_name: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> "AppianGrid":
        """Return a nested Appian grid scoped to this cell."""
        from robo_appian.appian.data.appian_grid import AppianGrid

        return AppianGrid(
            self,
            label=label,
            header=header,
            row_name=row_name,
            column_name=column_name,
            exact=exact,
            visible=visible,
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Indexed component collections
    # ------------------------------------------------------------------
    @property
    def buttons(self) -> AppianComponentCollection[AppianButton]:
        def indexed(index: int) -> AppianButton:
            component = AppianButton(
                page=self._page, name=f"button[{index}]", scope=self
            )
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("button[type='button']"), index
            )
            return component

        return AppianComponentCollection(indexed, name="button")

    @property
    def textboxes(self) -> AppianComponentCollection[AppianTextbox]:
        def indexed(index: int) -> AppianTextbox:
            component = AppianTextbox(
                page=self._page, label=f"textbox[{index}]", scope=self
            )
            raw = self.locator.locator(f"xpath=.//*[{component._control_predicate()}]")
            component._indexed_locator = self._visible_nth(raw, index)  # type: ignore[attr-defined]
            return component

        return AppianComponentCollection(indexed, name="textbox")

    @property
    def dropdowns(self) -> AppianComponentCollection[AppianDropdown]:
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

        return AppianComponentCollection(indexed, name="dropdown")

    @property
    def checkboxes(self) -> AppianComponentCollection[AppianCheckbox]:
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

        return AppianComponentCollection(indexed, name="checkbox")

    @property
    def radios(self) -> AppianComponentCollection[AppianRadioSelect]:
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

        return AppianComponentCollection(indexed, name="radio")

    @property
    def links(self) -> AppianComponentCollection[AppianLink]:
        def indexed(index: int) -> AppianLink:
            component = AppianLink(page=self._page, name=f"link[{index}]", scope=self)
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.get_by_role("link"), index
            )
            return component

        return AppianComponentCollection(indexed, name="link")

    @property
    def tabs(self) -> AppianComponentCollection[AppianTab]:
        def indexed(index: int) -> AppianTab:
            component = AppianTab(page=self._page, name=f"tab[{index}]", scope=self)
            state = self.locator.get_by_text(AppianTab._STATE_PATTERN)
            tabs = self.locator.get_by_role("link").filter(has=state)
            component._indexed_locator = self._visible_nth(tabs, index)  # type: ignore[attr-defined]
            return component

        return AppianComponentCollection(indexed, name="tab")

    @property
    def dates(self) -> AppianComponentCollection[AppianDate]:
        def indexed(index: int) -> AppianDate:
            component = AppianDate(page=self._page, label=f"date[{index}]", scope=self)
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator(f"xpath=.//*[{component._control_predicate()}]"),
                index,
            )
            return component

        return AppianComponentCollection(indexed, name="date")

    @property
    def grids(self) -> AppianComponentCollection["AppianGrid"]:
        from robo_appian.appian.data.appian_grid import AppianGrid

        def indexed(index: int) -> AppianGrid:
            component = AppianGrid(self, label=f"grid[{index}]")
            component._indexed_locator = self._visible_nth(  # type: ignore[attr-defined]
                self.locator.locator("table"), index
            )
            return component

        return AppianComponentCollection(indexed, name="grid")


__all__ = ["AppianCell"]
