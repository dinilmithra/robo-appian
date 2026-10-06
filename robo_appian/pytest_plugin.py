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
from playwright.sync_api import Browser

from robo_automation import PytestPerformanceMonitor

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
def robo_appian_browser(
    robo_automation_browser: Browser,
) -> RoboBrowser:
    """Wrap robo-automation's raw browser as the robo-appian browser boundary.

    The unique fixture name prevents collisions with generic plugins that also
    expose a public fixture named ``browser``.
    """
    return RoboBrowser.get(robo_automation_browser)


@pytest.fixture(scope="session")
def browser(robo_appian_browser: RoboBrowser) -> RoboBrowser:
    """Public robo-appian browser fixture.

    Consuming projects may override this fixture normally.  Internal robo-appian
    fixtures depend on ``robo_appian_browser`` so plugin load order cannot replace
    the wrapper with a raw Playwright browser.
    """
    return robo_appian_browser


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
def robo_appian_context(
    robo_appian_browser: RoboBrowser,
    storage_state: Any,
    performance_monitor: Optional[PytestPerformanceMonitor],
    robo_appian_context_lifecycle: ContextLifecycle,
) -> Iterator[RoboContext]:
    """Provide robo-appian's uniquely named test-scoped context fixture."""
    yield from robo_appian_context_lifecycle(
        robo_appian_browser,
        storage_state,
        performance_monitor,
    )


@pytest.fixture
def context(robo_appian_context: RoboContext) -> RoboContext:
    """Public context alias retained for compatibility."""
    return robo_appian_context


@pytest.fixture
def robo_appian_page(
    robo_appian_context: RoboContext,
    performance_monitor: Optional[PytestPerformanceMonitor],
    robo_appian_page_lifecycle: PageLifecycle,
) -> Iterator[RoboPage]:
    """Provide robo-appian's uniquely named test-scoped page fixture."""
    yield from robo_appian_page_lifecycle(robo_appian_context, performance_monitor)


@pytest.fixture
def page(robo_appian_page: RoboPage) -> RoboPage:
    """Public page alias retained for compatibility."""
    return robo_appian_page
