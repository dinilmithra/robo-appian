"""Shared behavior for Appian input components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator

from robo_appian.utils.ComponentUtils import ComponentUtils

if TYPE_CHECKING:
    from .appian_page import AppianPage


class AppianInputComponent:
    """Base class for Appian components that change input state.

    The base owns only the common post-change lifecycle. Component-specific
    locator resolution and interaction semantics remain in each subclass.
    """

    def __init__(
        self,
        *,
        page: "AppianPage",
        timeout: float | int | None = None,
    ) -> None:
        self._page = page
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

    @property
    def timeout(self) -> float | None:
        """Return this component's timeout override in seconds, if any."""
        return self._timeout

    def _timeout_kwargs(self, timeout: float | int | None = None) -> dict[str, float]:
        """Return Playwright timeout kwargs using an optional method override."""
        effective = self._timeout if timeout is None else timeout
        return ComponentUtils.timeout_kwargs(effective)

    @staticmethod
    def _focus_out(locator: Locator) -> None:
        """Move focus away so Appian can commit/validate the changed value."""
        locator.blur()

    def _after_change(self, locator: Locator) -> None:
        """Run shared behavior after a component value/state actually changes."""
        self._focus_out(locator)


__all__ = ["AppianInputComponent"]
