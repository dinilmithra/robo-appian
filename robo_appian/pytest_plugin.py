"""Pytest fixtures that specialize robo-automation for Appian consumers.

``robo-automation`` owns the underlying browser/context/page lifecycle. This
plugin only specializes the generic ``RoboPage`` as ``AppianPage`` and exposes
it as the public ``page`` fixture for Appian consumers.
"""

from __future__ import annotations

import pytest

from robo_automation import RoboPage
from robo_appian.appian import AppianPage


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
