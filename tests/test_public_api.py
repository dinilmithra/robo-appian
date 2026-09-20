"""Smoke tests for the standalone robo_appian package boundary."""

import inspect

from robo_appian import Dropdown, InputDate, SearchDropdown


def test_public_components_import() -> None:
    """Core public components are importable from the package root."""
    assert Dropdown is not None
    assert InputDate is not None
    assert SearchDropdown is not None


def test_search_dropdown_exact_label_defaults_to_true() -> None:
    """Strict label matching remains the SearchDropdown default."""
    signature = inspect.signature(SearchDropdown.select)
    assert signature.parameters["exact_label"].default is True
