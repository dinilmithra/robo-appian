from unittest.mock import MagicMock

from playwright.sync_api import Browser, BrowserContext

from robo_appian import RoboBrowser, RoboContext


def _mock_browser() -> Browser:
    browser = MagicMock(spec=Browser)
    browser.new_context.return_value = MagicMock(spec=BrowserContext)
    return browser


def test_get_wraps_playwright_browser_without_public_bridge() -> None:
    browser = _mock_browser()
    robo_browser = RoboBrowser.get(browser)
    assert isinstance(robo_browser, RoboBrowser)
    assert not hasattr(type(robo_browser), "browser")


def test_new_context_returns_robo_context() -> None:
    browser = _mock_browser()
    robo_browser = RoboBrowser.get(browser)
    context = robo_browser.new_context(ignore_https_errors=True)
    assert isinstance(context, RoboContext)
    browser.new_context.assert_called_once_with(ignore_https_errors=True)
