from unittest.mock import MagicMock

from playwright.sync_api import Locator, Page

from robo_appian import RoboLocator, RoboPage


def _mock_page() -> Page:
    page = MagicMock(spec=Page)
    locator = MagicMock(spec=Locator)
    page.locator.return_value = locator
    return page


def test_get_wraps_playwright_page_without_public_bridge() -> None:
    page = _mock_page()
    robo_page = RoboPage.get(page)
    assert isinstance(robo_page, RoboPage)
    assert not hasattr(type(robo_page), "page")


def test_get_by_attributes_returns_robo_locator() -> None:
    page = _mock_page()
    robo_page = RoboPage.get(page)
    result = robo_page.get_by_attributes(
        attributes={"role": "button", "aria-label": "User options"},
        excat_match=True,
    )
    assert isinstance(result, RoboLocator)
    page.locator.assert_called_once_with(
        "xpath=.//*[@role='button' and @aria-label='User options']"
    )


def test_get_by_id_returns_robo_locator() -> None:
    page = _mock_page()
    robo_page = RoboPage.get(page)
    result = robo_page.get_by_id("jsAcceptButton", excat_match=True)
    assert isinstance(result, RoboLocator)
    page.locator.assert_called_once_with("xpath=.//*[@id='jsAcceptButton']")
