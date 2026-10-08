"""Shared behavior for Appian input components."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator

if TYPE_CHECKING:
    from .appian_page import AppianPage


class AppianInputComponent:
    """Base class for Appian components that change input state.

    The base owns only the common post-change lifecycle. Component-specific
    locator resolution and interaction semantics remain in each subclass.
    """

    def __init__(self, *, page: "AppianPage") -> None:
        self._page = page

    @staticmethod
    def _focus_out(locator: Locator) -> None:
        """Move focus away so Appian can commit/validate the changed value."""
        locator.blur()

    def _after_change(self, locator: Locator) -> None:
        """Run shared behavior after a component value/state actually changes."""
        self._focus_out(locator)


__all__ = ["AppianInputComponent"]
