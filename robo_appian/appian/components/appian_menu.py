"""Appian menu paths resolved and clicked through public business names."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.internal.component_support import ComponentSupport

if TYPE_CHECKING:
    from robo_appian.appian.page.appian_page import AppianPage


class AppianMenu:
    """Describe a menu path; execute it with click, open, or options."""

    def __init__(
        self, page: AppianPage, name: str, *, exact: bool = True,
        visible=True, timeout=None,
    ) -> None:
        self._validate_choice(name, None)
        self.page = page
        self.name = " ".join(str(name).split())
        self.exact = exact
        self.visible = ComponentSupport.normalize_visibility(visible)
        self.timeout = ComponentSupport.normalize_timeout_seconds(timeout)
        self._parent: AppianMenu | None = None
        self._index: int | None = None
        self._opened = False

    @staticmethod
    def _validate_choice(name: str | None, index: int | None) -> None:
        if (name is None) == (index is None):
            raise ValueError("Specify either a menu name or a 1-based index.")
        if name is not None and (not isinstance(name, str) or not name.strip()):
            raise ValueError("Menu name must be a non-empty string.")
        if index is not None and (
            isinstance(index, bool) or not isinstance(index, int) or index < 1
        ):
            raise ValueError("Menu index must be 1 or greater.")

    def _visible(self, locator: Locator) -> Locator:
        return locator if self.visible is None else locator.filter(visible=self.visible)

    def _locator(self, *, open_ancestors: bool = True) -> Locator:
        if self._parent is not None:
            return self._parent._option(
                None if self._index is not None else self.name,
                index=self._index, open_menu=open_ancestors,
            )
        return self._visible(
            self.page.get_by_role("button", name=self.name, exact=self.exact)
        ).first

    def is_visible(self) -> bool:
        """Check current visibility without opening any part of the path."""
        return self._locator(open_ancestors=False).is_visible()

    def open(self) -> AppianMenu:
        """Open this menu and its ancestors, preserving an expanded trigger."""
        trigger = self._locator()
        kwargs = ComponentSupport.timeout_kwargs(self.timeout)
        expect(trigger).to_be_visible(**kwargs)
        expanded = trigger.get_attribute("aria-expanded")
        if (expanded or "").lower() != "true" and (
            expanded is not None or not self._opened
        ):
            ComponentSupport.click(trigger)
        if expanded is not None:
            expect(trigger).to_have_attribute("aria-expanded", "true", **kwargs)
        self._opened = True
        return self

    def _options(self, *, open_menu: bool = True) -> Locator:
        if open_menu:
            self.open()
        options = self.page.get_by_role("option")
        dialog = self.page.get_by_role("dialog", name=self.name, exact=self.exact)
        for role in ("button", "link", "menuitem"):
            options = options.or_(dialog.get_by_role(role))
        return self._visible(options)

    def _option(
        self, name: str | None = None, *, index: int | None = None,
        open_menu: bool = True,
    ) -> Locator:
        if index is not None:
            return self._options(open_menu=open_menu).nth(index - 1)
        if open_menu:
            self.open()
        # Role/name lookup handles nested button text and input[value] equally.
        # Profile actions remain scoped to their named User options dialog.
        option = self.page.get_by_role("option", name=name, exact=self.exact)
        dialog = self.page.get_by_role("dialog", name=self.name, exact=self.exact)
        for role in ("button", "link", "menuitem"):
            option = option.or_(dialog.get_by_role(role, name=name, exact=self.exact))
        return self._visible(option).first

    def menu(self, name: str | None = None, *, index: int | None = None) -> AppianMenu:
        """Append a named or indexed item without clicking the page."""
        self._validate_choice(name, index)
        child = AppianMenu(
            self.page, name if name is not None else f"menu item {index}",
            exact=self.exact, visible=self.visible, timeout=self.timeout,
        )
        child._parent = self
        child._index = index
        return child

    def click(self, *, opens_new_page: bool = False) -> AppianPage:
        """Open ancestors, click the leaf once, and return the resulting page.

        False skips popup waiting; it does not change the application's link
        target. True requires a popup and returns a public AppianPage wrapper.
        Missing popups, failed clicks, and load failures propagate to the caller.
        """
        target = self._locator()
        kwargs = ComponentSupport.timeout_kwargs(self.timeout)
        expect(target).to_be_visible(**kwargs)
        if not opens_new_page:
            ComponentSupport.click(target)
            self.page.wait_for_appian_action_completed(timeout=self.timeout)
            return self.page
        with self.page.expect_popup(**kwargs) as popup_info:
            ComponentSupport.click(target)
        popup = popup_info.value
        popup.wait_for_load_state("domcontentloaded", **kwargs)
        return type(self.page).get(popup)

    def options(self) -> list[str]:
        """Open this menu and return its visible choices in document order."""
        options = self._options()
        return [
            " ".join((options.nth(i).inner_text()
                      or options.nth(i).get_attribute("aria-label")
                      or options.nth(i).get_attribute("value") or "").split())
            for i in range(options.count())
        ]


__all__ = ["AppianMenu"]
