from pathlib import Path
from unittest.mock import MagicMock, Mock

from playwright.sync_api import Locator, Page

from robo_automation import RoboPage
from robo_appian import AppianLocator, AppianPage, AppianScope


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


def test_appian_page_button_returns_appian_button() -> None:
    from robo_appian import AppianButton

    page = _mock_page()
    appian_page = AppianPage.get(page)

    button = appian_page.button(name="Save")

    assert isinstance(button, AppianButton)
    assert button.name == "Save"


def test_appian_button_does_not_import_legacy_components() -> None:
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[1]
        / "robo_appian"
        / "appian"
        / "appian_button.py"
    ).read_text(encoding="utf-8")

    assert "robo_appian.components" not in source


def test_appian_page_button_requires_name_keyword() -> None:
    import pytest

    page = _mock_page()
    appian_page = AppianPage.get(page)

    with pytest.raises(TypeError):
        appian_page.button("Save")  # type: ignore[misc]


def test_button_locator_requires_type_button() -> None:
    from robo_appian import AppianButton

    page = _mock_page()
    appian_page = AppianPage.get(page)
    AppianButton(page=appian_page, name="Submit", exact=True)._locator()

    xpath = page.locator.call_args.args[0]
    assert ".//button[@type='button'" in xpath
    assert ".//input[" not in xpath


def test_button_locator_matches_name_without_using_css_classes() -> None:
    from robo_appian import AppianButton

    page = _mock_page()
    appian_page = AppianPage.get(page)
    AppianButton(page=appian_page, name="Submit", exact=True)._locator()

    xpath = page.locator.call_args.args[0]
    assert "@type='button'" in xpath
    assert "@class" not in xpath
    assert "SUBMIT" in xpath


def test_appian_button_disabled_uses_disabled_attribute() -> None:
    from robo_appian import AppianButton

    page = _mock_page()
    locator = page.locator.return_value
    locator.filter.return_value.first.get_attribute.return_value = ""
    appian_page = AppianPage.get(page)

    assert AppianButton(page=appian_page, name="Submit").is_disabled() is True


def test_appian_button_enabled_when_disabled_attribute_absent() -> None:
    from robo_appian import AppianButton

    page = _mock_page()
    locator = page.locator.return_value
    locator.filter.return_value.first.get_attribute.return_value = None
    appian_page = AppianPage.get(page)

    assert AppianButton(page=appian_page, name="Submit").is_enabled() is True


def test_appian_button_disabled_is_not_enabled() -> None:
    from robo_appian import AppianButton

    page = _mock_page()
    locator = page.locator.return_value
    locator.filter.return_value.first.get_attribute.return_value = ""
    appian_page = AppianPage.get(page)

    assert AppianButton(page=appian_page, name="Submit").is_enabled() is False


def test_appian_page_button_can_preserve_locator_scope() -> None:
    page = _mock_page()
    raw_scope = MagicMock(spec=Locator)
    raw_scope.locator.return_value = MagicMock(spec=Locator)
    scoped_locator = AppianLocator.get(raw_scope)
    appian_page = AppianPage.get(page)

    button = appian_page.button(name="Confirm", scope=scoped_locator)
    button._locator()

    raw_scope.locator.assert_called_once()
    page.locator.assert_not_called()



def test_appian_browser_context_is_not_public_api() -> None:
    import robo_appian

    package_root = Path(__file__).resolve().parents[1] / "robo_appian"
    assert not (package_root / "appian" / "appian_browser_context.py").exists()
    assert not hasattr(robo_appian, "AppianBrowserContext")

def test_appian_scope_contains_only_appian_abstractions() -> None:
    from typing import get_args

    assert set(get_args(AppianScope)) == {AppianPage, AppianLocator}


def test_core_does_not_reference_generic_robo_resource_types() -> None:
    core_root = Path(__file__).resolve().parents[2] / "core-automation"
    forbidden = ("RoboPage", "RoboBrowserContext", "RoboLocator", "from robo_automation import Scope")

    for path in core_root.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{token!r} found in {path}"


def test_legacy_components_button_is_removed() -> None:
    """The legacy static Button component must not return to robo-appian."""
    import robo_appian

    package_root = Path(__file__).resolve().parents[1] / "robo_appian"
    assert not (package_root / "components" / "Button.py").exists()
    assert not hasattr(robo_appian, "Button")

    components_init = (package_root / "components" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert "components.Button" not in components_init
