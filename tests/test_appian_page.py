from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

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

    button = appian_page.appian_button(name="Save")

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
        appian_page.appian_button("Save")  # type: ignore[misc]


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

    button = appian_page.appian_button(name="Confirm", scope=scoped_locator)
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

    textbox = appian_page.appian_textbox(label="Title")

    assert isinstance(textbox, AppianTextbox)
    assert textbox.label == "Title"
    assert textbox.placeholder is None


def test_appian_page_textbox_by_placeholder_returns_appian_textbox() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    textbox = appian_page.appian_textbox(placeholder="example@example.com")

    assert isinstance(textbox, AppianTextbox)
    assert textbox.placeholder == "example@example.com"
    assert textbox.label is None


def test_appian_page_textbox_by_header_returns_appian_textbox() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    textbox = appian_page.appian_textbox(header="Conference Description")

    assert isinstance(textbox, AppianTextbox)
    assert textbox.header == "Conference Description"
    assert textbox.label is None
    assert textbox.placeholder is None


def test_appian_textbox_requires_exactly_one_identifier() -> None:
    import pytest

    page = _mock_page()
    appian_page = AppianPage.get(page)

    with pytest.raises(ValueError):
        appian_page.appian_textbox()

    with pytest.raises(ValueError):
        appian_page.appian_textbox(label="Title", placeholder="Title")

    with pytest.raises(ValueError):
        appian_page.appian_textbox(label="Title", header="Conference Description")

    with pytest.raises(ValueError):
        appian_page.appian_textbox(
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

    date = appian_page.appian_date(label="Required Award Date")

    assert isinstance(date, AppianDate)
    assert date.label == "Required Award Date"


def test_appian_date_inherits_appian_textbox() -> None:
    from robo_appian import AppianDate, AppianTextbox

    assert issubclass(AppianDate, AppianTextbox)


def test_appian_input_components_share_focus_out_base() -> None:
    from robo_appian import (
        AppianDate,
        AppianInputComponent,
        AppianRadioSelect,
        AppianTextbox,
    )

    assert issubclass(AppianTextbox, AppianInputComponent)
    assert issubclass(AppianDate, AppianInputComponent)
    assert issubclass(AppianRadioSelect, AppianInputComponent)


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


def test_appian_textbox_fill_blurs_after_entering_value() -> None:
    from robo_appian import AppianTextbox

    page = _mock_page()
    appian_page = AppianPage.get(page)
    textbox = AppianTextbox(page=appian_page, label="Title")
    text_input = MagicMock(spec=Locator)
    textbox._wait_until_ready_locator = MagicMock(return_value=text_input)  # type: ignore[method-assign]

    textbox.fill("Contract Title")

    text_input.fill.assert_called_once_with("Contract Title")
    text_input.blur.assert_called_once_with()
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


def test_appian_page_checkbox_returns_appian_checkbox() -> None:
    from robo_appian import AppianCheckbox

    page = _mock_page()
    appian_page = AppianPage.get(page)

    checkbox = appian_page.appian_checkbox(label="Vendor is missing in approved list")

    assert isinstance(checkbox, AppianCheckbox)


def test_appian_page_radio_returns_appian_radio_select() -> None:
    from robo_appian import AppianRadioSelect

    page = _mock_page()
    appian_page = AppianPage.get(page)

    radio = appian_page.appian_radio(label="Is this request for a conference?")

    assert isinstance(radio, AppianRadioSelect)


def _radio_group_mocks(page: Page, label_id: str):
    label = MagicMock(spec=Locator)
    label.count.return_value = 1
    label.get_attribute.return_value = label_id
    group = MagicMock(spec=Locator)
    group.count.return_value = 1
    target = MagicMock(spec=Locator)
    group.locator.return_value.first = target
    page.locator.side_effect = [label, group]
    return label, group, target


def test_appian_radio_select_radio_locator_scopes_value_to_aria_labelled_group() -> None:
    page = _mock_page()
    label, group, target = _radio_group_mocks(page, "conference-question-id")
    target.is_checked.return_value = True
    appian_page = AppianPage.get(page)

    selected = appian_page.appian_radio(
        label="Is this request for a conference?"
    ).is_selected("Yes")

    assert selected is True
    label_xpath = page.locator.call_args_list[0].args[0]
    group_xpath = page.locator.call_args_list[1].args[0]
    option_xpath = group.locator.call_args.args[0]
    assert "IS THIS REQUEST FOR A CONFERENCE?" in label_xpath
    assert "@class" not in label_xpath
    assert "@role='radiogroup'" in group_xpath
    assert "@aria-labelledby='conference-question-id'" in group_xpath
    assert "input[@type='radio' and @value='Yes']" in option_xpath
    label.get_attribute.assert_called_once_with("id")


def test_appian_radio_select_is_idempotent_when_already_checked() -> None:
    page = _mock_page()
    _, _, target = _radio_group_mocks(page, "traveler-count-id")
    target.is_checked.return_value = True
    appian_page = AppianPage.get(page)

    appian_page.appian_radio(
        label="How many people are you submitting in this travel request?"
    ).select("More than one")

    target.check.assert_not_called()
    target.blur.assert_not_called()


def test_appian_radio_select_clicks_associated_label() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_radio(label="Is this request for a conference?")
    before = MagicMock(spec=Locator)
    after = MagicMock(spec=Locator)
    choice_label = MagicMock(spec=Locator)
    before.is_checked.return_value = False
    component._radio_locator = MagicMock(side_effect=[before, after])  # type: ignore[method-assign]
    component._radio_label_locator = MagicMock(return_value=choice_label)  # type: ignore[method-assign]

    with (
        patch("robo_appian.appian.appian_radio_select.expect") as expect_mock,
        patch("robo_appian.appian.appian_radio_select.ComponentUtils.wait_for_appian_action_completed"),
    ):
        component.select("Yes")

    component._radio_label_locator.assert_called_once_with(before)
    choice_label.click.assert_called_once_with()
    before.check.assert_not_called()
    before.uncheck.assert_not_called()
    after.blur.assert_called_once_with()
    expect_mock.return_value.to_be_checked.assert_called_once_with(checked=True)


def test_appian_radio_select_falls_back_to_unique_visible_option_when_semantic_label_missing() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_radio(label="Are you submitting this travel request for yourself or on behalf of someone else?")
    missing_label = MagicMock(spec=Locator)
    missing_label.count.return_value = 0
    labels = MagicMock(spec=Locator)
    labels.count.return_value = 0
    option_label = MagicMock(spec=Locator)
    labels.first = option_label
    radio = MagicMock(spec=Locator)
    option_label.locator.return_value = radio
    page.locator.side_effect = [missing_label, labels]

    with patch("robo_appian.appian.appian_radio_select.expect") as expect_mock:
        expect_mock.return_value.to_be_visible.side_effect = lambda: setattr(
            labels.count, "return_value", 1
        )
        resolved = component._radio_locator("For myself")

    assert resolved is radio
    fallback_xpath = page.locator.call_args_list[1].args[0]
    assert "label[@for and normalize-space(string(.))='For myself']" in fallback_xpath
    option_label.locator.assert_called_once_with(
        "xpath=preceding-sibling::input[@type='radio'][1]"
    )
    assert "@class" not in fallback_xpath


def test_appian_checkbox_uses_live_accessible_name_locator_for_choice_label() -> None:
    page = _mock_page()
    named = MagicMock(spec=Locator)
    group = MagicMock(spec=Locator)
    combined = MagicMock(spec=Locator)
    target = MagicMock(spec=Locator)
    target.is_checked.return_value = False
    named.or_.return_value = combined
    combined.first = target
    page.get_by_role.return_value = named
    page.locator.return_value = group
    appian_page = AppianPage.get(page)

    with patch("robo_appian.appian.appian_checkbox.expect"):
        checked = appian_page.appian_checkbox(
            label="Vendor is missing in approved list"
        ).is_checked()

    assert checked is False
    page.get_by_role.assert_called_once_with(
        "checkbox",
        name="Vendor is missing in approved list",
        exact=True,
    )
    named.or_.assert_called_once_with(group)
    named.count.assert_not_called()
    group.count.assert_not_called()


def test_appian_checkbox_keeps_field_group_fallback_live_for_rerender() -> None:
    page = _mock_page()
    named = MagicMock(spec=Locator)
    group = MagicMock(spec=Locator)
    combined = MagicMock(spec=Locator)
    target = MagicMock(spec=Locator)
    target.is_checked.return_value = False
    named.or_.return_value = combined
    combined.first = target
    page.get_by_role.return_value = named
    page.locator.return_value = group
    appian_page = AppianPage.get(page)

    with patch("robo_appian.appian.appian_checkbox.expect"):
        checked = appian_page.appian_checkbox(label="IT").is_checked(timeout=10)

    assert checked is False
    group_xpath = page.locator.call_args.args[0]
    assert "@role='group'" in group_xpath
    assert "@aria-labelledby" in group_xpath
    assert "IT" in group_xpath
    assert "@type='checkbox'" in group_xpath
    assert "@class" not in group_xpath
    # Regression: resolver must not probe count() and freeze to false() before
    # an Appian SAIL rerender attaches the checkbox.
    named.count.assert_not_called()
    group.count.assert_not_called()
    assert "false()" not in group_xpath


def test_appian_checkbox_timeout_waits_for_presence_not_checked_state() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(label="IT")
    target = MagicMock(spec=Locator)
    target.is_checked.return_value = False
    component._checkbox_locator = MagicMock(return_value=target)  # type: ignore[method-assign]

    with patch("robo_appian.appian.appian_checkbox.expect") as expect_mock:
        assert component.is_checked(timeout=10) is False

    expect_mock.return_value.to_be_attached.assert_called_once_with(timeout=10000.0)
    expect_mock.return_value.to_be_checked.assert_not_called()


def test_appian_checkbox_clicks_native_label_for_pointer_intercepting_input() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(
        label="I have read and understand the qualifications for the reimbursement."
    )
    target = MagicMock(spec=Locator)
    group = MagicMock(spec=Locator)
    choice_label = MagicMock(spec=Locator)
    target.get_attribute.return_value = "qualification-checkbox-id"
    target.locator.return_value = group
    group.count.return_value = 1
    group.locator.return_value.first = choice_label

    resolved = component._checkbox_label_locator(target)

    assert resolved is choice_label
    target.get_attribute.assert_called_once_with("id")
    target.locator.assert_called_once_with("xpath=ancestor::*[@role='group'][1]")
    label_xpath = group.locator.call_args.args[0]
    assert "label[@for='qualification-checkbox-id']" in label_xpath
    assert "@class" not in label_xpath


def test_appian_checkbox_check_only_when_unchecked() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(label="Vendor is missing in approved list")
    before = MagicMock(spec=Locator)
    after = MagicMock(spec=Locator)
    choice_label = MagicMock(spec=Locator)
    before.is_checked.return_value = False
    component._checkbox_locator = MagicMock(side_effect=[before, after])  # type: ignore[method-assign]
    component._checkbox_label_locator = MagicMock(return_value=choice_label)  # type: ignore[method-assign]

    with (
        patch("robo_appian.appian.appian_checkbox.expect") as expect_mock,
        patch("robo_appian.appian.appian_checkbox.ComponentUtils.wait_for_appian_action_completed"),
    ):
        result = component.check()

    assert result is component
    component._checkbox_label_locator.assert_called_once_with(before)
    choice_label.click.assert_called_once_with()
    before.check.assert_not_called()
    before.uncheck.assert_not_called()
    after.blur.assert_called_once_with()
    expect_mock.return_value.to_be_checked.assert_called_once_with(checked=True)


def test_appian_checkbox_check_is_noop_when_already_checked() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(label="Vendor is missing in approved list")
    target = MagicMock(spec=Locator)
    target.is_checked.return_value = True
    component._checkbox_locator = MagicMock(return_value=target)  # type: ignore[method-assign]

    with patch("robo_appian.appian.appian_checkbox.expect"):
        component.check()

    target.check.assert_not_called()
    target.uncheck.assert_not_called()
    target.blur.assert_not_called()


def test_appian_checkbox_uncheck_only_when_checked() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(label="Vendor is missing in approved list")
    before = MagicMock(spec=Locator)
    after = MagicMock(spec=Locator)
    choice_label = MagicMock(spec=Locator)
    before.is_checked.return_value = True
    component._checkbox_locator = MagicMock(side_effect=[before, after])  # type: ignore[method-assign]
    component._checkbox_label_locator = MagicMock(return_value=choice_label)  # type: ignore[method-assign]

    with (
        patch("robo_appian.appian.appian_checkbox.expect") as expect_mock,
        patch("robo_appian.appian.appian_checkbox.ComponentUtils.wait_for_appian_action_completed"),
    ):
        result = component.uncheck()

    assert result is component
    component._checkbox_label_locator.assert_called_once_with(before)
    choice_label.click.assert_called_once_with()
    before.uncheck.assert_not_called()
    before.check.assert_not_called()
    after.blur.assert_called_once_with()
    expect_mock.return_value.to_be_checked.assert_called_once_with(checked=False)


def test_appian_checkbox_uncheck_is_noop_when_already_unchecked() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(label="Vendor is missing in approved list")
    target = MagicMock(spec=Locator)
    target.is_checked.return_value = False
    component._checkbox_locator = MagicMock(return_value=target)  # type: ignore[method-assign]

    with patch("robo_appian.appian.appian_checkbox.expect"):
        component.uncheck()

    target.check.assert_not_called()
    target.uncheck.assert_not_called()
    target.blur.assert_not_called()


def test_appian_checkbox_set_checked_routes_to_expected_state() -> None:
    page = _mock_page()
    appian_page = AppianPage.get(page)
    component = appian_page.appian_checkbox(label="Vendor is missing in approved list")
    component.check = MagicMock(return_value=component)  # type: ignore[method-assign]
    component.uncheck = MagicMock(return_value=component)  # type: ignore[method-assign]

    # Public method delegates through the shared idempotent state implementation.
    component._set_checked = MagicMock(return_value=component)  # type: ignore[method-assign]
    assert component.set_checked(True) is component
    component._set_checked.assert_called_once_with(True)


def test_legacy_checkbox_component_is_removed() -> None:
    """The legacy static CheckBox helper must not remain part of robo-appian."""
    import robo_appian

    package_root = Path(robo_appian.__file__).resolve().parent
    assert not (package_root / "components" / "CheckBox.py").exists()
    assert not hasattr(robo_appian, "CheckBox")

    components_init = (package_root / "components" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert "CheckBox" not in components_init


def test_legacy_radio_select_component_is_removed() -> None:
    """The static RadioSelect helper must not remain part of robo-appian."""
    import robo_appian

    package_root = Path(robo_appian.__file__).resolve().parent
    assert not (package_root / "components" / "RadioSelect.py").exists()
    assert not hasattr(robo_appian, "RadioSelect")


def test_appian_radio_select_pcard_radio_is_scoped_to_question_group() -> None:
    page = _mock_page()
    _, group, target = _radio_group_mocks(page, "pcard-receiver-id")
    target.is_checked.return_value = True
    appian_page = AppianPage.get(page)

    appian_page.appian_radio(
        label="Will you be the one to receive the purchased product or service?"
    ).select("Yes, I will be receiving the purchased product or service")

    group_xpath = page.locator.call_args_list[1].args[0]
    option_xpath = group.locator.call_args.args[0]
    assert "@role='radiogroup'" in group_xpath
    assert "@aria-labelledby='pcard-receiver-id'" in group_xpath
    assert (
        "input[@type='radio' and @value='Yes, I will be receiving the purchased product or service']"
        in option_xpath
    )
    target.check.assert_not_called()


def test_core_no_longer_references_legacy_radio_select() -> None:
    core_root = Path(__file__).resolve().parents[2] / "core-automation"
    matches = []
    for path in core_root.rglob("*.py"):
        if any(part in {".venv", ".venv-core", "dist", "__pycache__"} for part in path.parts):
            continue
        if "RadioSelect" in path.read_text(encoding="utf-8"):
            matches.append(path)
    assert not matches, f"RadioSelect remains in CORE: {matches}"


def test_appian_page_exposes_checkbox_and_radio_factories() -> None:
    """Keep the checkbox/radio public API available to consumer projects."""
    from robo_appian import AppianCheckbox, AppianRadioSelect

    page = _mock_page()
    appian_page = AppianPage.get(page)

    checkbox = appian_page.appian_checkbox(label="Vendor is missing in approved list")
    radio = appian_page.appian_radio(label="Will you be the one to receive the purchased product or service?")

    assert isinstance(checkbox, AppianCheckbox)
    assert isinstance(radio, AppianRadioSelect)
