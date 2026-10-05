"""Playwright Browser wrapper for robo-appian browser lifecycle control."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import Browser

from robo_appian.framework.robo_context import RoboContext


class RoboBrowser:
    """Own a Playwright browser behind the robo-appian framework boundary."""

    def __init__(self, browser: Browser) -> None:
        if not isinstance(browser, Browser):
            raise TypeError("RoboBrowser requires a Playwright Browser.")
        self._browser = browser

    @classmethod
    def get(cls, browser: Browser) -> "RoboBrowser":
        """Wrap a Playwright ``Browser`` in a new ``RoboBrowser``."""
        return cls(browser)

    def new_context(self, **kwargs: Any) -> RoboContext:
        """Create a browser context and return it as ``RoboContext``."""
        return RoboContext.get(self._browser.new_context(**kwargs))

    def close(self, **kwargs: Any) -> None:
        """Close the owned browser."""
        self._browser.close(**kwargs)

    def is_connected(self) -> bool:
        """Return whether the owned browser is connected."""
        return self._browser.is_connected()
