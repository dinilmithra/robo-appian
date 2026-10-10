"""Appian-facing assertion helpers that hide Playwright assertion types."""

from __future__ import annotations

from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, expect

from .errors import RoboAppianError


def wait_visible(
    locator: Any, *, timeout: float | None = None, message: str = ""
) -> None:
    """Wait for a locator to become visible using the configured Appian timeout."""
    try:
        if timeout is None:
            locator.wait_for(state="visible")
        else:
            locator.wait_for(state="visible", timeout=timeout)
    except PlaywrightTimeoutError as exc:
        raise RoboAppianError(
            message or "Appian element did not become visible in time.",
            code="ROBO_APPIAN_TIMEOUT",
            details={"operation": "wait_visible"},
        ) from exc


def assert_text(
    locator: Any, expected: Any, *, message: str = "", **kwargs: Any
) -> None:
    """Assert locator text through the Appian public error boundary."""
    try:
        expect(locator, message or None).to_have_text(expected, **kwargs)
    except AssertionError as exc:
        raise RoboAppianError(
            message or "Appian element text did not match the expected value.",
            code="ROBO_APPIAN_ASSERTION_ERROR",
            details={"operation": "to_have_text", "expected": str(expected)},
        ) from exc


def assert_not_text(
    locator: Any, expected: Any, *, message: str = "", **kwargs: Any
) -> None:
    """Assert locator text does not match ``expected``."""
    try:
        expect(locator, message or None).not_to_have_text(expected, **kwargs)
    except AssertionError as exc:
        raise RoboAppianError(
            message or "Appian element text still matches a disallowed value.",
            code="ROBO_APPIAN_ASSERTION_ERROR",
            details={"operation": "not_to_have_text", "expected": str(expected)},
        ) from exc


def assert_visible(locator: Any, *, message: str = "") -> None:
    """Assert locator visibility."""
    try:
        expect(locator, message or None).to_be_visible()
    except AssertionError as exc:
        raise RoboAppianError(
            message or "Appian element was not visible.",
            code="ROBO_APPIAN_ASSERTION_ERROR",
            details={"operation": "to_be_visible"},
        ) from exc
