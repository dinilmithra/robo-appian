"""Type contracts for Appian page and locator scopes."""

from __future__ import annotations

from typing import TypeAlias

from .locator.appian_locator import AppianLocator
from .page.appian_page import AppianPage

AppianScope: TypeAlias = AppianPage | AppianLocator

__all__ = ["AppianScope"]
