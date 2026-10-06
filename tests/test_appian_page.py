from unittest.mock import MagicMock, Mock

from playwright.sync_api import Locator, Page

from robo_automation import RoboPage
from robo_appian import AppianLocator, AppianPage


def _mock_page() -> Page:
    page = MagicMock(spec=Page)
    page.locator.return_value = MagicMock(spec=Locator)
    return page


def test_appian_page_is_robo_page_specialization() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    assert isinstance(appian_page, AppianPage)


def test_appian_page_attribute_lookup_returns_appian_locator() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    locator = appian_page.get_by_id("jsAcceptButton")
    assert isinstance(locator, AppianLocator)


def test_appian_page_fixture_specializes_robo_page() -> None:
    from robo_appian.pytest_plugin import appian_page as appian_page_fixture

    raw_page = Mock(spec=Page)
    robo_page = RoboPage.get(raw_page)
    result = appian_page_fixture.__wrapped__(robo_page)

    assert isinstance(result, AppianPage)
    assert result.same_page(robo_page)


def test_pytest11_entry_point_declared() -> None:
    """Package metadata must auto-register the Appian pytest plugin."""
    import tomllib
    from pathlib import Path

    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    metadata = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    assert metadata["project"]["entry-points"]["pytest11"]["robo_appian"] == (
        "robo_appian.pytest_plugin"
    )
