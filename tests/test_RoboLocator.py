from unittest.mock import MagicMock

import pytest

from robo_appian import RoboLocator


def test_builds_xpath_from_arbitrary_attributes() -> None:
    scope = MagicMock()
    locator = MagicMock()
    scope.locator.return_value = locator

    element = RoboLocator(
        scope,
        attributes={
            "role": "button",
            "aria-label": "User options",
            "data-testid": "user-profile",
        },
        excat_match=True,
    )

    scope.locator.assert_called_once_with(
        "xpath=.//*[@role='button' and @aria-label='User options' and "
        "@data-testid='user-profile']"
    )
    assert element.locator is locator


def test_supports_any_valid_html_attribute_name() -> None:
    scope = MagicMock()
    scope.locator.return_value = MagicMock()

    RoboLocator(
        scope,
        attributes={
            "id": "menu",
            "title": "User options",
            "data-custom-value": "abc123",
            "aria-haspopup": "true",
        },
    )

    scope.locator.assert_called_once_with(
        "xpath=.//*[@id='menu' and @title='User options' and "
        "@data-custom-value='abc123' and @aria-haspopup='true']"
    )


def test_get_by_id_builds_id_locator() -> None:
    scope = MagicMock()
    locator = MagicMock()
    scope.locator.return_value = locator

    element = RoboLocator.get_by_id(scope, "jsAcceptButton")

    scope.locator.assert_called_once_with("xpath=.//*[@id='jsAcceptButton']")
    assert element.locator is locator


def test_get_by_id_rejects_empty_id() -> None:
    scope = MagicMock()

    with pytest.raises(ValueError, match="element_id must not be empty"):
        RoboLocator.get_by_id(scope, "")


def test_excat_match_false_uses_contains_for_string_values() -> None:
    scope = MagicMock()
    scope.locator.return_value = MagicMock()

    RoboLocator(
        scope,
        attributes={"aria-label": "User", "class": "profile"},
        excat_match=False,
    )

    scope.locator.assert_called_once_with(
        "xpath=.//*[contains(@aria-label, 'User') and contains(@class, 'profile')]"
    )


def test_boolean_and_none_values_use_attribute_presence_semantics() -> None:
    scope = MagicMock()
    scope.locator.return_value = MagicMock()

    RoboLocator(
        scope,
        attributes={"disabled": True, "hidden": False, "data-ready": None},
    )

    scope.locator.assert_called_once_with(
        "xpath=.//*[@disabled and not(@hidden) and @data-ready]"
    )


def test_xpath_literal_handles_single_and_double_quotes() -> None:
    scope = MagicMock()
    scope.locator.return_value = MagicMock()

    RoboLocator(
        scope,
        attributes={"title": "Bob's \"User\" options"},
    )

    selector = scope.locator.call_args.args[0]
    assert selector.startswith("xpath=.//*[")
    assert "concat(" in selector
    assert "@title=" in selector


def test_click_delegates_to_wrapped_locator() -> None:
    scope = MagicMock()
    locator = MagicMock()
    scope.locator.return_value = locator

    element = RoboLocator(
        scope,
        attributes={"role": "button", "aria-label": "User options"},
    )
    element.click(timeout=2500)

    locator.click.assert_called_once_with(timeout=2500)


def test_requires_at_least_one_attribute() -> None:
    scope = MagicMock()

    with pytest.raises(ValueError, match="must not be empty"):
        RoboLocator(scope, attributes={})


def test_all_valid_attribute_names_are_allowed_in_attributes() -> None:
    scope = MagicMock()
    scope.locator.return_value = MagicMock()

    RoboLocator(
        scope,
        attributes={
            "role": "button",
            "excat_match": "custom-value",
        },
    )

    scope.locator.assert_called_once_with(
        "xpath=.//*[@role='button' and @excat_match='custom-value']"
    )


def test_rejects_invalid_attribute_name() -> None:
    scope = MagicMock()

    with pytest.raises(ValueError, match="Invalid RoboLocator attribute name"):
        RoboLocator(scope, attributes={"bad attribute": "value"})


def test_to_be_visible_narrows_to_single_visible_match(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    visible_locator = MagicMock()
    visible_first = MagicMock()
    assertion = MagicMock()
    scope.locator.return_value = locator
    locator.filter.return_value = visible_locator
    visible_locator.first = visible_first
    visible_locator.count.side_effect = [1, 1]

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    monkeypatch.setattr(module, "expect", lambda actual: assertion)

    element = RoboLocator(
        scope,
        attributes={"role": "button", "aria-label": "User options"},
    )
    element.to_be_visible()

    locator.filter.assert_called_once_with(visible=True)
    assertion.to_be_visible.assert_called_once_with()
    assert element.locator is visible_first


def test_to_be_visible_forwards_explicit_timeout_when_unique(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    visible_locator = MagicMock()
    visible_first = MagicMock()
    assertion = MagicMock()
    scope.locator.return_value = locator
    locator.filter.return_value = visible_locator
    visible_locator.first = visible_first
    visible_locator.count.side_effect = [1, 1]

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    monkeypatch.setattr(module, "expect", lambda actual: assertion)

    element = RoboLocator(scope, attributes={"role": "button"})
    element.to_be_visible(timeout=2500)

    assertion.to_be_visible.assert_called_once_with(timeout=2500)
    assert element.locator is visible_first


def test_to_be_visible_retains_visible_set_when_multiple_visible(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    visible_locator = MagicMock()
    scope.locator.return_value = locator
    locator.filter.return_value = visible_locator
    visible_locator.count.return_value = 2

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    expect_mock = MagicMock()
    monkeypatch.setattr(module, "expect", expect_mock)

    element = RoboLocator(scope, attributes={"role": "button"})
    element.to_be_visible()

    expect_mock.assert_not_called()
    assert element.locator is visible_locator

    element.click()
    visible_locator.click.assert_called_once_with()


def test_first_returns_new_robo_locator_for_current_first_match() -> None:
    scope = MagicMock()
    locator = MagicMock()
    first_locator = MagicMock()
    scope.locator.return_value = locator
    locator.first = first_locator

    element = RoboLocator(scope, attributes={"role": "button"})
    first = element.first()

    assert first is not element
    assert first.locator is first_locator
    assert first.scope is scope
    assert first.attributes == {"role": "button"}
    assert element.locator is locator


def test_first_after_multiple_visible_uses_first_visible_match(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    visible_locator = MagicMock()
    visible_first = MagicMock()
    scope.locator.return_value = locator
    locator.filter.return_value = visible_locator
    visible_locator.count.return_value = 2
    visible_locator.first = visible_first

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    monkeypatch.setattr(module, "expect", MagicMock())

    element = RoboLocator(scope, attributes={"role": "button"})
    element.to_be_visible()
    first = element.first()

    assert element.locator is visible_locator
    assert first.locator is visible_first


def test_wait_for_attribute_uses_playwright_default_timeout_when_none(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    scope.locator.return_value = locator
    assertion = MagicMock()

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    monkeypatch.setattr(module, "expect", lambda actual: assertion)

    element = RoboLocator(
        scope,
        attributes={"role": "button", "aria-label": "User options"},
    )
    element.wait_for_attribute(attributes={"aria-expanded": "false"})

    assertion.to_have_attribute.assert_called_once_with("aria-expanded", "false")


def test_wait_for_attribute_forwards_explicit_timeout(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    scope.locator.return_value = locator
    assertion = MagicMock()

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    monkeypatch.setattr(module, "expect", lambda actual: assertion)

    element = RoboLocator(
        scope,
        attributes={"data-testid": "user-profile"},
    )
    element.wait_for_attribute(attributes={"data-state": "ready"}, timeout=2500)

    assertion.to_have_attribute.assert_called_once_with(
        "data-state", "ready", timeout=2500
    )



def test_wait_for_attribute_supports_multiple_attributes(monkeypatch) -> None:
    scope = MagicMock()
    locator = MagicMock()
    scope.locator.return_value = locator
    assertion = MagicMock()

    import importlib

    module = importlib.import_module("robo_appian.components.RoboLocator")
    monkeypatch.setattr(module, "expect", lambda actual: assertion)

    element = RoboLocator(scope, attributes={"role": "button"})
    element.wait_for_attribute(
        attributes={
            "aria-expanded": "false",
            "data-state": "ready",
        }
    )

    assert assertion.to_have_attribute.call_count == 2
    assertion.to_have_attribute.assert_any_call("aria-expanded", "false")
    assertion.to_have_attribute.assert_any_call("data-state", "ready")
