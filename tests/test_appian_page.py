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


def test_appian_page_textbox_by_label_returns_appian_textbox() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    textbox = appian_page.textbox(label="Title")

    assert isinstance(textbox, AppianTextbox)
    assert textbox.label == "Title"
    assert textbox.placeholder is None


def test_appian_page_textbox_by_placeholder_returns_appian_textbox() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    textbox = appian_page.textbox(placeholder="example@example.com")

    assert isinstance(textbox, AppianTextbox)
    assert textbox.placeholder == "example@example.com"
    assert textbox.label is None


def test_appian_textbox_requires_exactly_one_identifier() -> None:
    import pytest

    page = _mock_page()
    appian_page = AppianPage.get(page)

    with pytest.raises(ValueError):
        appian_page.textbox()

    with pytest.raises(ValueError):
        appian_page.textbox(label="Title", placeholder="Title")


def test_appian_textbox_label_uses_label_for_and_text_input_id() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    label_locator = MagicMock(spec=Locator)
    input_locator = MagicMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.get_attribute.return_value = "field-123"
    page.locator.side_effect = [label_locator, input_locator]
    appian_page = AppianPage.get(page)

    result = AppianTextbox(page=appian_page, label="Title")._locator()

    assert result is input_locator
    label_xpath = page.locator.call_args_list[0].args[0]
    input_xpath = page.locator.call_args_list[1].args[0]
    assert ".//label[@for" in label_xpath
    assert "TITLE" in label_xpath
    assert "self::input" in input_xpath
    assert "@type='text'" in input_xpath
    assert "self::textarea" in input_xpath
    assert "@role='textbox'" in input_xpath
    assert "@id='field-123'" in input_xpath


def test_appian_textbox_placeholder_requires_text_input() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    AppianTextbox(
        page=appian_page,
        placeholder="example@example.com",
    )._locator()

    xpath = page.locator.call_args.args[0]
    assert "self::input" in xpath
    assert "@type='text'" in xpath
    assert "self::textarea" in xpath
    assert "@role='textbox'" in xpath
    assert "@placeholder" in xpath
    assert "EXAMPLE@EXAMPLE.COM" in xpath



def test_appian_textbox_label_supports_multiline_textarea() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    label_locator = MagicMock(spec=Locator)
    textbox_locator = MagicMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.get_attribute.return_value = "description-123"
    page.locator.side_effect = [label_locator, textbox_locator]
    appian_page = AppianPage.get(page)

    result = AppianTextbox(page=appian_page, label="Description")._locator()

    assert result is textbox_locator
    xpath = page.locator.call_args_list[1].args[0]
    assert "self::textarea" in xpath
    assert "@role='textbox'" in xpath
    assert "@id='description-123'" in xpath


def test_appian_textbox_placeholder_supports_multiline_textarea() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    AppianTextbox(page=appian_page, placeholder="Comment")._locator()

    xpath = page.locator.call_args.args[0]
    assert "self::textarea" in xpath
    assert "@role='textbox'" in xpath
    assert "@placeholder" in xpath
    assert "COMMENT" in xpath

def test_appian_textbox_label_supports_password_input() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    label_locator = MagicMock(spec=Locator)
    textbox_locator = MagicMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.get_attribute.return_value = "pw"
    page.locator.side_effect = [label_locator, textbox_locator]
    appian_page = AppianPage.get(page)

    result = AppianTextbox(page=appian_page, label="Password")._locator()

    assert result is textbox_locator
    xpath = page.locator.call_args_list[1].args[0]
    assert "@type='text'" in xpath
    assert "@type='password'" in xpath
    assert "@id='pw'" in xpath


def test_appian_textbox_placeholder_supports_password_input() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    AppianTextbox(page=appian_page, placeholder="Password")._locator()

    xpath = page.locator.call_args.args[0]
    assert "@type='text'" in xpath
    assert "@type='password'" in xpath
    assert "@placeholder" in xpath
    assert "PASSWORD" in xpath

def test_appian_textbox_does_not_import_legacy_components() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "robo_appian"
        / "appian"
        / "appian_textbox.py"
    ).read_text(encoding="utf-8")

    assert "robo_appian.components" not in source


def test_appian_textbox_label_falls_back_to_accessible_textbox_name() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    missing_label = MagicMock(spec=Locator)
    role_locator = MagicMock(spec=Locator)
    first_locator = MagicMock(spec=Locator)
    missing_label.count.return_value = 0
    role_locator.first = first_locator
    page.locator.return_value = missing_label
    page.get_by_role.return_value = role_locator
    appian_page = AppianPage.get(page)

    result = AppianTextbox(
        page=appian_page, label="Description", exact=False
    )._locator()

    assert result is first_locator
    page.get_by_role.assert_called_once_with(
        "textbox", name="Description", exact=False
    )


def test_appian_textbox_accessible_name_fallback_does_not_use_visible_text() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "robo_appian"
        / "appian"
        / "appian_textbox.py"
    ).read_text(encoding="utf-8")

    assert "visible_label =" not in source
    assert "following-sibling" not in source
