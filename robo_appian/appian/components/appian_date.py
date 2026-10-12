"""Appian date component abstraction."""

from __future__ import annotations

from datetime import datetime

from playwright.sync_api import Locator, expect

from .appian_textbox import AppianTextbox


class AppianDate(AppianTextbox):
    """Represent an Appian date field using textbox interaction behavior."""

    DATE_TEST_ID = "DatePickerWidget-textInput"

    @staticmethod
    def normalize(value: object) -> str:
        """Return a common date value formatted as ``MM/DD/YYYY`` when possible."""
        if value is None:
            return ""
        raw_value = str(value).strip()
        if not raw_value:
            return ""

        known_formats = (
            "%m/%d/%Y",
            "%m/%d/%y",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
        )
        for date_format in known_formats:
            try:
                return datetime.strptime(raw_value, date_format).strftime("%m/%d/%Y")
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).strftime(
                "%m/%d/%Y"
            )
        except ValueError:
            return raw_value

    def fill(self, value: object) -> None:
        """Normalize and enter a date value, then commit the field."""
        super().fill(self.normalize(value))

    @classmethod
    def fill_locator(cls, locator: Locator, value: object) -> None:
        """Fill an already-resolved date control and commit its value."""
        target = locator.filter(visible=True).first
        expect(target, "Date input was not visible.").to_be_visible()
        expect(target, "Date input was not enabled.").to_be_enabled()
        target.fill(cls.normalize(value))
        cls._focus_out(target)

    def _control_predicate(self) -> str:
        return (
            "(self::input and @type='text' and " f"@data-testid='{self.DATE_TEST_ID}')"
        )


__all__ = ["AppianDate"]
