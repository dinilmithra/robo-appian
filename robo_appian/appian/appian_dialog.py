"""Appian modal dialog component abstraction."""

from __future__ import annotations

from playwright.sync_api import expect

from .appian_button import AppianButton
from .appian_component_accessor import AppianComponentAccessor
from .appian_locator import AppianLocator
from robo_appian.utils.ComponentUtils import ComponentUtils


class AppianDialog(AppianLocator):
    """Represent a semantic Appian ``role=dialog`` modal and its components."""

    def __init__(
        self,
        page,
        *,
        name: str | None = None,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
        index: int | None = None,
    ) -> None:
        self._page = page
        self._name = name
        self._exact = exact
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

        locator = page.get_by_role("dialog", name=name, exact=exact) if name else page.get_by_role("dialog")
        if self._visible is True:
            locator = locator.filter(visible=True)
        elif self._visible is False:
            locator = locator.filter(visible=False)
        if index is not None:
            locator = locator.nth(index)
        elif name is not None:
            locator = locator.first

        wrapped = AppianLocator.get(locator)
        self.scope = wrapped.scope
        self.attributes = wrapped.attributes
        self.excat_match = wrapped.excat_match
        self._locator = wrapped.locator

        if self._visible is True:
            expect(self._locator).to_be_visible(**ComponentUtils.timeout_kwargs(self._timeout))
        elif self._visible is False:
            expect(self._locator).to_be_hidden(**ComponentUtils.timeout_kwargs(self._timeout))

    def _button_factory(
        self,
        name: str,
        *,
        exact: bool = True,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> AppianButton:
        return AppianButton(
            page=self._page,
            name=name,
            exact=exact,
            scope=self,
            visible=visible,
            timeout=timeout,
        )

    @property
    def button(self) -> AppianComponentAccessor[AppianButton]:
        def indexed(index: int) -> AppianButton:
            component = AppianButton(page=self._page, name=f"button[{index}]", scope=self)
            component._indexed_locator = self.locator.get_by_role("button").filter(visible=True).nth(index)
            return component

        return AppianComponentAccessor(self._button_factory, indexed, component_name="button")


__all__ = ["AppianDialog"]
