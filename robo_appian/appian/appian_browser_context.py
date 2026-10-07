"""Appian-specific browser context abstraction."""

from __future__ import annotations

from typing import Any, Callable

from robo_automation import RoboBrowserContext

from .appian_page import AppianPage


class AppianBrowserContext(RoboBrowserContext):
    """Browser context specialization that exposes Appian pages."""

    def new_page(self) -> AppianPage:
        """Create and return a new Appian page."""
        return AppianPage.get(self._context.new_page())

    @property
    def pages(self) -> list[AppianPage]:
        """Return the current pages as Appian pages."""
        return [AppianPage.get(page) for page in self._context.pages]

    def on(self, event: str, callback: Callable[..., Any]) -> None:
        """Register a context event callback using Appian page values."""
        if event == "page":
            self._context.on(event, lambda page: callback(AppianPage.get(page)))
            return
        self._context.on(event, callback)


__all__ = ["AppianBrowserContext"]
