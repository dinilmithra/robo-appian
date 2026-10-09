"""Pytest fixtures that specialize robo-automation for Appian consumers.

``robo-automation`` owns the underlying browser/context/page lifecycle. This
plugin only specializes the generic ``RoboPage`` as ``AppianPage`` and exposes
it as the public ``page`` fixture for Appian consumers.
"""

from __future__ import annotations

import pytest

from typing import Any, Optional

from robo_automation import RoboPage
from robo_appian.appian import AppianPage
from robo_appian.runtime import AppianRuntime


@pytest.fixture(scope="session")
def appian_runtime(
    browser: Any,
    performance_monitor: Optional[Any],
    wait_time: int,
) -> AppianRuntime:
    """Expose Appian-level runtime services to consumer projects.

    Consumers should depend on this fixture instead of robo-automation browser
    or performance classes directly.
    """
    return AppianRuntime(
        browser,
        performance_monitor,
        wait_time_seconds=wait_time,
    )


@pytest.fixture
def appian_page(robo_page: RoboPage) -> AppianPage:
    """Specialize the lower-layer ``RoboPage`` as an ``AppianPage``."""
    page = robo_page.specialize(AppianPage)
    assert isinstance(page, AppianPage)
    return page


@pytest.fixture
def page(appian_page: AppianPage) -> AppianPage:
    """Expose ``AppianPage`` as the public page fixture for Appian consumers."""
    return appian_page
