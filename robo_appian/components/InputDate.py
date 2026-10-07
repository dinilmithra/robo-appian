"""Generic helpers for entering and reading date values from UI controls."""

import logging
from datetime import datetime, timedelta

from playwright.sync_api import Locator, expect
from robo_automation import Scope

# Initialize logger for execution tracking
logger = logging.getLogger(__name__)


class InputDate:
    """Reusable operations for Appian date controls."""

    @staticmethod
    def __normalize_date_string(date_str: str) -> str:
        """
        Normalizes common Excel/pandas date representations into MM/DD/YYYY.
        Returns the original value when parsing is not possible.
        """
        if date_str is None:
            return ""

        raw_value = str(date_str).strip()
        if not raw_value:
            return ""

        known_formats = [
            "%m/%d/%Y",
            "%m/%d/%y",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
        ]

        for date_format in known_formats:
            try:
                return datetime.strptime(raw_value, date_format).strftime("%m/%d/%Y")
            except ValueError:
                continue

        try:
            iso_value = raw_value.replace("Z", "+00:00")
            return datetime.fromisoformat(iso_value).strftime("%m/%d/%Y")
        except ValueError:
            return raw_value

    @staticmethod
    def __fill(scope: Scope, locator: Locator, date_str: str) -> None:
        """
        Fill a date field with a normalized date string.

        Focus movement is intentionally controlled by application code through
        the RoboAppian facade so callers can decide when to commit/blur the
        date field.
        """
        # Ensure only the active, visible input is targeted
        active_locator = locator.filter(visible=True).first

        # 1. Assert visibility and enablement
        expect(active_locator).to_be_visible()
        expect(active_locator).to_be_enabled()

        # Fill only. Application code owns the subsequent Tab/focus change.
        normalized_date = InputDate.__normalize_date_string(date_str)
        active_locator.fill(normalized_date)

        logger.info("Filled date input with '%s'.", normalized_date)

    @staticmethod
    def fill_by_locator(
        scope: Scope,
        locator: Locator,
        date_str: str,
    ) -> None:
        """Fill an already-resolved date input.

        Use this from container utilities that locate their own date control.
        Common Excel, US, and ISO date representations are normalized to
        ``MM/DD/YYYY`` when possible. The application layer is responsible for
        any subsequent Tab/focus-change operation.

        Args:
            scope: Appian scope that owns the date control.
            locator: Date input locator; the first visible match is used.
            date_str: Date value to normalize and enter.
        """
        InputDate.__fill(scope, locator, date_str)

    @staticmethod
    def fill_date_by_label(
        scope: Scope, label: str, date_str: str, excat_match: bool = False
    ) -> None:
        """Fill a labeled date input.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Accessible label used to locate the input.
            date_str: Excel, US, or ISO-style date to normalize when possible.
            excat_match: Whether the accessible label must match exactly.
        """
        # .filter(visible=True) ignores hidden mobile layouts in Appian
        locator = scope.get_by_label(label, exact=excat_match)
        InputDate.fill_by_locator(scope, locator, date_str)

    @staticmethod
    def fill_date_by_id(scope: Scope, input_id: str, date_str: str) -> None:
        """Fill a date input by literal HTML ID.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            input_id: Exact HTML ID, including IDs that begin with numbers.
            date_str: Excel, US, or ISO-style date to normalize when possible.
        """
        # Use attribute selector [id="..."] instead of # to prevent CSS SyntaxErrors
        locator = scope.locator(f'[id="{input_id}"]')
        InputDate.fill_by_locator(scope, locator, date_str)

    @staticmethod
    def get_date_value(
        scope: Scope, label: str, excat_match: bool = False
    ) -> str:
        """Return the current value of a labeled date input.

        The value is read exactly as rendered by the browser so application
        business logic can decide how to parse or validate it. Hidden Appian
        layouts are ignored by selecting the first visible matching input.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Accessible label used to locate the input.
            excat_match: Whether the accessible label must match exactly.

        Returns:
            str: Current input value, stripped of surrounding whitespace.
        """
        locator = scope.get_by_label(label, exact=excat_match).filter(visible=True).first
        expect(locator).to_be_visible()
        value = locator.input_value().strip()
        logger.info("Read date input '%s' value '%s'.", label, value)
        return value

    @staticmethod
    def verify_date_by_label(
        scope: Scope, label: str, expected_date_str: str, excat_match: bool = False
    ) -> None:
        """Wait until a labeled date input displays an exact expected value.

        The expected value is compared as supplied and is not normalized.

        Args:
            scope: browser automation ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Accessible label used to locate the input.
            expected_date_str: Exact rendered input value to expect.
            excat_match: Whether the accessible label must match exactly.
        """
        locator = scope.get_by_label(label, exact=excat_match).filter(visible=True).first
        expect(locator).to_have_value(expected_date_str)
        logger.info("Verified input '%s' has value '%s'.", label, expected_date_str)

    @staticmethod
    def get_future_date(days: int) -> str:
        """Create a UI-ready date a number of days from local today.

        Args:
            days: Positive or negative day offset from the current local date.

        Returns:
            str: Offset date formatted as ``MM/DD/YYYY``.
        """
        today = datetime.now()
        future_date = today + timedelta(days=days)
        return future_date.strftime("%m/%d/%Y")
