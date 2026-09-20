"""Generic helpers for text-input and textarea interaction."""

import logging
from typing import Union

from playwright.sync_api import Locator, Page, expect

logger = logging.getLogger(__name__)


class InputText:
    """Reusable operations for text inputs and textareas."""

    @staticmethod
    def is_visible_by_label(
        scope: Union[Page, Locator],
        label: str,
        exact: bool = False,
    ) -> bool:
        """Return whether a visible input exists for the supplied label."""
        if not label or not label.strip():
            return False

        locator = scope.get_by_label(
            label.strip(),
            exact=exact,
        ).filter(visible=True)

        return locator.count() > 0

    @staticmethod
    def is_visible_by_type(
        scope: Union[Page, Locator],
        input_type: str,
    ) -> bool:
        """Return whether a visible input exists for the supplied HTML type."""
        if not input_type or not input_type.strip():
            return False

        locator = scope.locator(f'input[type="{input_type.strip()}"]').filter(
            visible=True
        )

        return locator.count() > 0

    @staticmethod
    def fill_by_locator(
        locator: Locator,
        value: str,
    ) -> None:
        """
        Fill an already-resolved Appian text input or textarea.

        Container utilities can use this public API after locating a textbox in
        their own semantic scope without duplicating input interaction logic.
        """
        expect(
            locator,
            "InputText control is not visible.",
        ).to_be_visible()
        expect(
            locator,
            "InputText control is not enabled.",
        ).to_be_enabled()

        locator.fill(str(value or ""))

    @staticmethod
    def _fill_by_locator(
        locator: Locator,
        value: str,
    ) -> None:
        """Backward-compatible internal alias for ``fill_by_locator``."""
        InputText.fill_by_locator(locator, value)

    @staticmethod
    def fill_by_label(
        scope: Union[Page, Locator],
        label: str,
        value: str,
        exact: bool = False,
    ) -> None:
        """
        Fill a visible textbox using its accessible label.

        Appian pages can expose the same accessible text on non-editable
        containers such as regions. Restricting lookup to the textbox role
        ensures this API resolves only an editable text input or textarea.

        Args:
            scope: Page or Locator used to resolve the textbox.
            label: Accessible label of the textbox.
            value: Value to enter.
            exact: Whether the accessible label must match exactly.

        Raises:
            ValueError: If the label is empty or whitespace.
            AssertionError: If a matching visible textbox is not found.
        """
        if not label or not label.strip():
            raise ValueError("Label cannot be empty or whitespace.")

        normalized_label = label.strip()

        textbox = (
            scope.get_by_role(
                "textbox",
                name=normalized_label,
                exact=exact,
            )
            .filter(visible=True)
            .first
        )

        expect(
            textbox,
            f"Textbox '{normalized_label}' was not visible.",
        ).to_be_visible()

        InputText.fill_by_locator(
            textbox,
            value,
        )

        logger.info(
            "Filled textbox using accessible label '%s'.",
            normalized_label,
        )

    @staticmethod
    def fill_by_visible_label(
        scope: Union[Page, Locator],
        label: str,
        value: str,
        exact: bool = True,
    ) -> None:
        """Fill an Appian textbox whose visible field heading is separate from it.

        Some Appian paragraph/textarea layouts render the visible field name in
        one ``FieldLayout`` and the actual textarea in the immediately following
        ``FieldLayout`` with an empty accessibility label.  In that markup,
        ``get_by_role('textbox', name=...)`` cannot resolve the control.

        This API intentionally handles that specific Appian structure without
        changing ``fill_by_label`` or adding a fallback to it.
        """
        normalized_label = str(label or "").strip()
        if not normalized_label:
            raise ValueError("Visible label cannot be empty or whitespace.")

        visible_label = (
            scope.get_by_text(normalized_label, exact=exact).filter(visible=True).first
        )
        expect(
            visible_label,
            f"Visible field label '{normalized_label}' was not found.",
        ).to_be_visible()

        label_field = visible_label.locator(
            "xpath=ancestor::*[contains(@class,'FieldLayout---field_layout')][1]"
        )
        input_field = label_field.locator(
            "xpath=following-sibling::*[contains(@class,'FieldLayout---field_layout')][1]"
        )
        textbox = input_field.get_by_role("textbox").filter(visible=True).first

        expect(
            textbox,
            f"Textbox following visible field label '{normalized_label}' was not visible.",
        ).to_be_visible()

        InputText.fill_by_locator(textbox, value)
        logger.info(
            "Filled textbox following visible field label '%s'.",
            normalized_label,
        )

    @staticmethod
    def fill_by_id(
        page: Page,
        element_id: str,
        value: str,
    ) -> None:
        """
        Fill a visible input or textarea identified by its DOM id.

        This public API is useful for reusable Appian components that resolve
        a concrete input id before delegating text interaction to InputText.

        Args:
            page: Current Playwright page.
            element_id: DOM id of the input or textarea.
            value: Value to enter.

        Raises:
            ValueError: If the element id is empty or whitespace.
            AssertionError: If the resolved input is not visible.
        """
        if not element_id or not element_id.strip():
            raise ValueError("InputText id cannot be empty or whitespace.")

        normalized_id = element_id.strip()
        locator = page.locator(f'[id="{normalized_id}"]').filter(visible=True).first

        expect(
            locator,
            f"InputText with id '{normalized_id}' was not visible.",
        ).to_be_visible()

        InputText.fill_by_locator(locator, value)

        logger.info("Filled input with id '%s'.", normalized_id)

    @staticmethod
    def fill_by_placeholder(
        scope: Union[Page, Locator],
        placeholder: str,
        value: str,
        exact: bool = True,
    ) -> None:
        """Fill a visible input using its placeholder."""
        if not placeholder or not placeholder.strip():
            raise ValueError("Placeholder cannot be empty or whitespace.")

        locator = (
            scope.get_by_placeholder(
                placeholder.strip(),
                exact=exact,
            )
            .filter(visible=True)
            .first
        )

        InputText.fill_by_locator(
            locator,
            value,
        )

    @staticmethod
    def fill_by_label_and_container(
        scope: Union[Page, Locator],
        field_label: str,
        header_text: str,
        value: str,
        exact: bool = False,
    ) -> None:
        """
        Fill a labeled input within a named semantic region.

        This is useful when the same field label occurs in multiple
        sections of a page.
        """
        if not field_label or not field_label.strip():
            raise ValueError("Field label cannot be empty or whitespace.")

        if not header_text or not header_text.strip():
            raise ValueError("Header text cannot be empty or whitespace.")

        header = (
            scope.get_by_text(
                header_text.strip(),
                exact=exact,
            )
            .filter(visible=True)
            .first
        )

        expect(
            header,
            (f"Container header " f"'{header_text.strip()}' was not found."),
        ).to_be_visible()

        container = header.locator("xpath=ancestor::*[@role='region'][1]")

        expect(
            container,
            (f"Container for header " f"'{header_text.strip()}' was not found."),
        ).to_be_visible()

        InputText.fill_by_label(
            container,
            field_label,
            value,
            exact=exact,
        )
