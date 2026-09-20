"""Shared type definitions for reusable Appian UI scopes."""

from typing import Union

from playwright.sync_api import Locator, Page

Scope = Union[Page, Locator]

__all__ = ["Scope"]
