"""Appian date component abstraction."""

from __future__ import annotations

from .appian_textbox import AppianTextbox


class AppianDate(AppianTextbox):
    """Represent an Appian date field using textbox interaction behavior."""

    DATE_TEST_ID = "DatePickerWidget-textInput"

    def _control_predicate(self) -> str:
        return (
            "(self::input and @type='text' and "
            f"@data-testid='{self.DATE_TEST_ID}')"
        )


__all__ = ["AppianDate"]
