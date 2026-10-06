"""Regression checks for pytest fixture namespace boundaries."""

from pathlib import Path


def test_robo_appian_context_uses_unique_wrapped_browser_fixture() -> None:
    source = Path("robo_appian/pytest_plugin.py").read_text(encoding="utf-8")
    assert "def robo_appian_browser(" in source
    assert "robo_automation_browser: Browser" in source
    assert "def robo_appian_context(\n    robo_appian_browser: RoboBrowser" in source


def test_public_browser_alias_is_preserved() -> None:
    source = Path("robo_appian/pytest_plugin.py").read_text(encoding="utf-8")
    assert "def browser(robo_appian_browser: RoboBrowser) -> RoboBrowser" in source


def test_unique_context_and_page_fixtures_are_exposed() -> None:
    source = Path("robo_appian/pytest_plugin.py").read_text(encoding="utf-8")
    assert "def robo_appian_context(" in source
    assert "def robo_appian_page(" in source
    assert "def context(robo_appian_context: RoboContext)" in source
    assert "def page(robo_appian_page: RoboPage)" in source
