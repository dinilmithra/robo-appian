"""Pytest fixtures that expose robo-appian wrapper objects to consuming projects.

The plugin owns the public ``browser``, ``context``, and ``page`` fixtures.  A
consuming project can override the two lifecycle-provider fixtures below when it
needs application-specific authentication/navigation behavior without taking
ownership of the public resource fixtures themselves.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Optional

import pytest
from playwright.sync_api import Playwright, sync_playwright

from robo_automation import PytestPerformanceMonitor
from robo_automation.browser import browser_lifecycle as generic_browser_lifecycle

from .framework import RoboBrowser, RoboContext, RoboPage

ContextLifecycle = Callable[
    [RoboBrowser, Any, Optional[PytestPerformanceMonitor]], Iterator[RoboContext]
]
PageLifecycle = Callable[
    [RoboContext, Optional[PytestPerformanceMonitor]], Iterator[RoboPage]
]


def _default_context_lifecycle(
    browser: RoboBrowser,
    storage_state: Any,
    performance_monitor: Optional[PytestPerformanceMonitor],
) -> Iterator[RoboContext]:
    """Create a generic test context when the consumer provides no override."""
    del performance_monitor
    options: dict[str, Any] = {}
    if storage_state:
        options["storage_state"] = storage_state
    context = browser.new_context(**options)
    try:
        yield context
    finally:
        context.close()


def _default_page_lifecycle(
    context: RoboContext,
    performance_monitor: Optional[PytestPerformanceMonitor],
) -> Iterator[RoboPage]:
    """Create a generic test page when the consumer provides no override."""
    del performance_monitor
    page = context.new_page()
    try:
        yield page
    finally:
        page.close()


@pytest.fixture(scope="session")
def playwright() -> Iterator[Playwright]:
    """Own the Playwright runtime inside robo-appian.

    Consuming projects do not need pytest-playwright merely to obtain the runtime.
    """
    with sync_playwright() as runtime:
        yield runtime


@pytest.fixture(scope="session")
def browser(
    playwright: Playwright,
    performance_monitor: Optional[PytestPerformanceMonitor],
    request: pytest.FixtureRequest,
) -> Iterator[RoboBrowser]:
    """Provide one worker/session-scoped :class:`RoboBrowser`."""
    lifecycle = generic_browser_lifecycle(playwright, performance_monitor, request)
    raw_browser = next(lifecycle)
    try:
        yield RoboBrowser.get(raw_browser)
    finally:
        lifecycle.close()


@pytest.fixture(scope="session")
def storage_state() -> None:
    """Default unauthenticated storage state.

    Application projects can override this fixture with a worker-aware authenticated
    state provider.  CORE does so to preserve per-xdist-worker session isolation.
    """
    return None


@pytest.fixture
def robo_appian_context_lifecycle() -> ContextLifecycle:
    """Return the context lifecycle used by the public ``context`` fixture."""
    return _default_context_lifecycle


@pytest.fixture
def robo_appian_page_lifecycle() -> PageLifecycle:
    """Return the page lifecycle used by the public ``page`` fixture."""
    return _default_page_lifecycle


@pytest.fixture
def context(
    browser: RoboBrowser,
    storage_state: Any,
    performance_monitor: Optional[PytestPerformanceMonitor],
    robo_appian_context_lifecycle: ContextLifecycle,
) -> Iterator[RoboContext]:
    """Provide one test-scoped :class:`RoboContext`."""
    yield from robo_appian_context_lifecycle(
        browser,
        storage_state,
        performance_monitor,
    )


@pytest.fixture
def page(
    context: RoboContext,
    performance_monitor: Optional[PytestPerformanceMonitor],
    robo_appian_page_lifecycle: PageLifecycle,
) -> Iterator[RoboPage]:
    """Provide one test-scoped :class:`RoboPage`."""
    yield from robo_appian_page_lifecycle(context, performance_monitor)
