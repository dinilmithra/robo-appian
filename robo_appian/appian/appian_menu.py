"""Business-facing Appian menu component."""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from robo_appian._component_support import ComponentSupport


class AppianMenu:
    """Open an Appian menu and choose visible business options."""

    def __init__(
        self, page, name: str, *, exact: bool = True, visible=True, timeout=None
    ) -> None:
        self.page = page
        self.name = " ".join(str(name).split())
        self.exact = exact
        self.visible = ComponentSupport.normalize_visibility(visible)
        self.timeout = ComponentSupport.normalize_timeout_seconds(timeout)
        self._opened = False

    def _button(self) -> Locator:
        buttons = self.page.get_by_role("button", name=self.name, exact=self.exact)
        buttons = (
            buttons.filter(has=self.page.locator("xpath=.//*[@aria-hidden='true']"))
            if False
            else buttons
        )
        if self.visible is not None:
            buttons = buttons.filter(visible=self.visible)
        button = buttons.first
        expect(button).to_be_visible(timeout=self.timeout)
        return button

    def open(self) -> "AppianMenu":
        button = self._button()
        if (button.get_attribute("aria-expanded") or "").lower() != "true":
            ComponentSupport.click(button)
        self._opened = True
        return self

    def _options(self) -> Locator:
        if not self._opened:
            self.open()
        options = self.page.get_by_role("option")
        if self.visible is not None:
            options = options.filter(visible=True)
        return options

    def _option(self, value: str | None = None, *, index: int | None = None) -> Locator:
        if value is None and index is None:
            raise ValueError("Menu option value or index is required.")
        if value is not None and index is not None:
            raise ValueError("Use either menu option value or index, not both.")
        options = self._options()
        if value is not None:
            option = options.filter(has_text=value).first
        else:
            if isinstance(index, bool) or not isinstance(index, int) or index < 1:
                raise ValueError("Menu option index must be 1 or greater.")
            option = options.nth(index - 1)
        expect(option).to_be_visible(timeout=self.timeout)
        return option

    def select(self, value: str | None = None, *, index: int | None = None) -> Page:
        """Choose a final menu option and return the opened page when it creates one."""
        option = self._option(value, index=index)
        owner = self.page
        try:
            with owner.expect_popup(
                timeout=int((self.timeout or 30) * 1000)
            ) as popup_info:
                ComponentSupport.click(option)
            new_page = popup_info.value
            new_page.wait_for_load_state("domcontentloaded")
            return new_page
        except Exception as exc:
            # A normal in-page menu selection does not create a popup.
            if "Timeout" not in type(exc).__name__ and "Timeout" not in str(exc):
                raise
            return owner

    def menu(
        self, value: str | None = None, *, index: int | None = None
    ) -> "AppianMenu":
        """Open a nested menu option and return it for fluent chaining."""
        option = self._option(value, index=index)
        ComponentSupport.click(option)
        child_name = value if value is not None else f"menu option {index}"
        child = AppianMenu(
            self.page,
            child_name,
            exact=self.exact,
            visible=self.visible,
            timeout=self.timeout,
        )
        child._opened = True
        return child

    def options(self) -> list[str]:
        """Return visible option text in displayed order."""
        options = self._options()
        return [
            " ".join(options.nth(i).inner_text().split())
            for i in range(options.count())
        ]


__all__ = ["AppianMenu"]
