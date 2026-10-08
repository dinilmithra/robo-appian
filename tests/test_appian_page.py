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
    forbidden = (
        "RoboPage",
        "RoboBrowserContext",
        "RoboLocator",
        "from robo_automation import Scope",
    )

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


def test_legacy_components_input_text_is_removed() -> None:
    """The legacy static InputText component must not return to robo-appian."""
    package_root = Path(__file__).resolve().parents[1] / "robo_appian"
    assert not (package_root / "components" / "InputText.py").exists()

    components_init = (package_root / "components" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert "components.InputText" not in components_init
    assert '"InputText"' not in components_init


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


def test_appian_page_textbox_by_header_returns_appian_textbox() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    textbox = appian_page.textbox(header="Conference Description")

    assert isinstance(textbox, AppianTextbox)
    assert textbox.header == "Conference Description"
    assert textbox.label is None
    assert textbox.placeholder is None


def test_appian_textbox_requires_exactly_one_identifier() -> None:
    import pytest

    page = _mock_page()
    appian_page = AppianPage.get(page)

    with pytest.raises(ValueError):
        appian_page.textbox()

    with pytest.raises(ValueError):
        appian_page.textbox(label="Title", placeholder="Title")

    with pytest.raises(ValueError):
        appian_page.textbox(label="Title", header="Conference Description")

    with pytest.raises(ValueError):
        appian_page.textbox(
            placeholder="Enter a value", header="Conference Description"
        )


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


def test_appian_textbox_header_uses_semantic_header_and_following_textbox() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    header_locator = MagicMock(spec=Locator)
    following_locator = MagicMock(spec=Locator)
    matched_locator = MagicMock(spec=Locator)
    header_locator.count.return_value = 1
    header_locator.first.locator.return_value.first = matched_locator
    page.locator.return_value = header_locator
    appian_page = AppianPage.get(page)

    result = AppianTextbox(
        page=appian_page,
        header="Conference Description",
    )._locator()

    assert result is matched_locator
    header_xpath = page.locator.call_args.args[0]
    assert "self::strong" in header_xpath
    assert "@role='heading'" in header_xpath
    assert "CONFERENCE DESCRIPTION" in header_xpath
    following_xpath = header_locator.first.locator.call_args.args[0]
    assert "following::*" in following_xpath
    assert "self::textarea" in following_xpath
    assert "@role='textbox'" in following_xpath
    assert "@class" not in header_xpath
    assert "@class" not in following_xpath


def test_appian_textbox_header_missing_returns_nonmatching_locator() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    missing_header = MagicMock(spec=Locator)
    no_match = MagicMock(spec=Locator)
    missing_header.count.return_value = 0
    page.locator.side_effect = [missing_header, no_match]
    appian_page = AppianPage.get(page)

    result = AppianTextbox(
        page=appian_page,
        header="Conference Description",
    )._locator()

    assert result is no_match
    assert "false()" in page.locator.call_args_list[1].args[0]


def test_core_conference_description_uses_header_textbox_lookup() -> None:
    conference_flow = (
        Path(__file__).resolve().parents[2]
        / "core-automation"
        / "src"
        / "flows"
        / "user_hub"
        / "conference.py"
    ).read_text(encoding="utf-8")

    assert "textbox(header=app_text.CONFERENCE_DESCRIPTION_TEXT)" in conference_flow
    assert "textbox(label=app_text.CONFERENCE_DESCRIPTION_TEXT" not in conference_flow


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
    filtered_locator = MagicMock(spec=Locator)
    role_locator.first = first_locator
    first_locator.locator.return_value.first = filtered_locator
    page.locator.return_value = missing_label
    page.get_by_role.return_value = role_locator
    appian_page = AppianPage.get(page)

    result = AppianTextbox(
        page=appian_page, label="Description", exact=False
    )._locator()

    assert result is filtered_locator
    page.get_by_role.assert_called_once_with("textbox", name="Description", exact=False)
    filter_xpath = first_locator.locator.call_args.args[0]
    assert "not(@data-testid='DatePickerWidget-textInput')" in filter_xpath


def test_appian_textbox_accessible_name_fallback_does_not_use_visible_text() -> None:
    source = (
        Path(__file__).resolve().parents[1]
        / "robo_appian"
        / "appian"
        / "appian_textbox.py"
    ).read_text(encoding="utf-8")

    assert "visible_label =" not in source
    assert "following-sibling" not in source


def test_appian_page_date_returns_appian_date() -> None:
    from robo_appian import AppianDate

    page = _mock_page()
    appian_page = AppianPage.get(page)

    date = appian_page.date(label="Required Award Date")

    assert isinstance(date, AppianDate)
    assert date.label == "Required Award Date"


def test_appian_date_inherits_appian_textbox() -> None:
    from robo_appian import AppianDate, AppianTextbox

    assert issubclass(AppianDate, AppianTextbox)


def test_appian_textbox_excludes_date_picker_test_id() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    label_locator = MagicMock(spec=Locator)
    textbox_locator = MagicMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.get_attribute.return_value = "title-id"
    page.locator.side_effect = [label_locator, textbox_locator]
    appian_page = AppianPage.get(page)

    AppianTextbox(page=appian_page, label="Title")._locator()

    xpath = page.locator.call_args_list[1].args[0]
    assert "@type='text'" in xpath
    assert "not(@data-testid='DatePickerWidget-textInput')" in xpath
    assert "@class" not in xpath


def test_appian_date_requires_date_picker_test_id() -> None:
    from robo_appian import AppianDate

    page = _mock_page()
    label_locator = MagicMock(spec=Locator)
    date_locator = MagicMock(spec=Locator)
    label_locator.count.return_value = 1
    label_locator.first.get_attribute.return_value = "award-date-id"
    page.locator.side_effect = [label_locator, date_locator]
    appian_page = AppianPage.get(page)

    AppianDate(page=appian_page, label="Required Award Date")._locator()

    xpath = page.locator.call_args_list[1].args[0]
    assert "@type='text'" in xpath
    assert "@data-testid='DatePickerWidget-textInput'" in xpath
    assert "@id='award-date-id'" in xpath
    assert "@class" not in xpath


def test_appian_date_placeholder_uses_date_picker_test_id() -> None:
    from robo_appian import AppianDate

    page = _mock_page()
    appian_page = AppianPage.get(page)

    AppianDate(page=appian_page, placeholder="mm/dd/yyyy")._locator()

    xpath = page.locator.call_args.args[0]
    assert "@data-testid='DatePickerWidget-textInput'" in xpath
    assert "@placeholder" in xpath
    assert "MM/DD/YYYY" in xpath
    assert "@class" not in xpath


def test_component_utils_unwraps_appian_locator_for_low_level_locator_calls() -> None:
    """Legacy helpers must unwrap AppianLocator before calling locator(...)."""
    from unittest.mock import patch

    from robo_appian import ComponentUtils

    raw_scope = MagicMock(spec=Locator)
    processing = MagicMock(spec=Locator)
    raw_scope.locator.return_value = processing
    wrapped_scope = AppianLocator.get(raw_scope)

    assert ComponentUtils.unwrap_scope(wrapped_scope) is raw_scope

    with patch("robo_appian.utils.ComponentUtils.expect") as expect_mock:
        ComponentUtils.wait_for_appian_action_completed(wrapped_scope)

    raw_scope.locator.assert_called_once_with(
        "#appian-nprogress, #appian-working-indicator-hidden"
    )
    expect_mock.assert_called_once_with(
        processing,
        "The application continued processing longer than expected.",
    )
    expect_mock.return_value.to_have_count.assert_called_once_with(0)


def test_appian_date_fill_blurs_after_entering_value() -> None:
    from robo_appian import AppianDate

    page = _mock_page()
    appian_page = AppianPage.get(page)
    date = AppianDate(page=appian_page, label="Required Award Date")
    date_input = MagicMock(spec=Locator)
    date._wait_until_ready_locator = MagicMock(return_value=date_input)  # type: ignore[method-assign]

    date.fill("10/07/2026")

    date_input.fill.assert_called_once_with("10/07/2026")
    date_input.blur.assert_called_once_with()
    date_input.press.assert_not_called()


def test_appian_textbox_fill_does_not_blur() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)
    textbox = AppianTextbox(page=appian_page, label="Title")
    text_input = MagicMock(spec=Locator)
    textbox._wait_until_ready_locator = MagicMock(return_value=text_input)  # type: ignore[method-assign]

    textbox.fill("Contract Title")

    text_input.fill.assert_called_once_with("Contract Title")
    text_input.press.assert_not_called()


def test_appian_page_does_not_expose_generic_label_or_placeholder_methods() -> None:
    assert not hasattr(AppianPage, "get_by_label")
    assert not hasattr(AppianPage, "get_by_placeholder")


def test_legacy_input_date_module_is_removed() -> None:
    from pathlib import Path

    module_path = (
        Path(__file__).parents[1] / "robo_appian" / "components" / "InputDate.py"
    )
    assert not module_path.exists()


def test_legacy_text_component_is_removed() -> None:
    """The legacy static Text component must not return to robo-appian."""
    from pathlib import Path
    import robo_appian

    package_root = Path(robo_appian.__file__).resolve().parent
    assert not (package_root / "components" / "Text.py").exists()
    components_init = (package_root / "components" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert "components.Text" not in components_init
    assert '"Text"' not in components_init
    assert not hasattr(robo_appian, "Text")
