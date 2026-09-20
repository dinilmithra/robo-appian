"""Generic helpers for checkbox interaction and state validation."""

from typing import Tuple

from playwright.sync_api import Locator, Page, expect

from robo_appian.utils.ComponentUtils import ComponentUtils


class CheckBox:
    """
    Utility class for interacting with Appian checkbox controls.

    Appian may re-render a checkbox after selection and regenerate dynamic
    element IDs. Hidden responsive copies are ignored by resolving the
    currently visible label first and then following its ``for`` attribute
    to the native checkbox input.
    """

    @staticmethod
    def __find_controls(page: Page, text: str) -> Tuple[Locator, Locator]:
        """
        Locate the currently visible label and its linked checkbox input.

        The native input itself is not required to be visible because Appian
        may visually hide/minimize it while making the associated label the
        interactive control.
        """
        label_text = text.strip()
        if not label_text:
            raise ValueError("Checkbox label text cannot be empty.")

        safe_text = ComponentUtils.xpath_literal(label_text)
        label = (
            page.locator(f"xpath=//label[@for and contains(., {safe_text})]")
            .filter(visible=True)
            .first
        )
        expect(
            label,
            f"Visible checkbox label for '{label_text}' was not found",
        ).to_be_visible()

        checkbox_id = label.get_attribute("for")
        if not checkbox_id:
            raise ValueError(
                f"Checkbox label for '{label_text}' has no 'for' attribute."
            )

        safe_checkbox_id = ComponentUtils.xpath_literal(checkbox_id)
        checkbox = page.locator(
            f"xpath=//input[@type='checkbox' and @id={safe_checkbox_id}]"
        ).first
        expect(
            checkbox,
            f"Checkbox labeled '{label_text}' was not found",
        ).to_be_attached()

        return checkbox, label

    @staticmethod
    def is_visible(page: Page, text: str) -> bool:
        """Return whether a visible checkbox label exists for the supplied text."""
        label_text = str(text or "").strip()
        if not label_text:
            return False

        safe_text = ComponentUtils.xpath_literal(label_text)
        label = (
            page.locator(f"xpath=//label[@for and contains(., {safe_text})]")
            .filter(visible=True)
            .first
        )
        return label.count() > 0

    @staticmethod
    def is_checked(page: Page, text: str) -> bool:
        """Return the checked state for an Appian checkbox field.

        Supports both conventional checkboxes with visible option labels and
        Appian boolean fields whose option label is visually blank (for
        example, the ``IT`` field). For blank-option fields, the field label's
        ID is linked to the checkbox group through ``aria-labelledby``.
        """
        field_text = str(text or "").strip()
        if not field_text:
            raise ValueError("Checkbox field text cannot be empty.")

        safe_text = ComponentUtils.xpath_literal(field_text)

        # First support the conventional visible option-label relationship.
        option_label = (
            page.locator(f"xpath=//label[@for and normalize-space(.)={safe_text}]")
            .filter(visible=True)
            .first
        )
        if option_label.count() > 0:
            checkbox_id = option_label.get_attribute("for")
            if checkbox_id:
                checkbox = page.locator(
                    f'input[type="checkbox"][id="{checkbox_id}"]'
                ).first
                expect(checkbox).to_be_attached()
                return checkbox.is_checked()

        # Appian boolean fields may have a blank option label. Resolve the
        # field label, then follow the checkbox group's aria-labelledby link.
        field_label = (
            page.locator(
                f"xpath=//*[self::span or self::label]"
                f"[@id and normalize-space(.)={safe_text}]"
            )
            .filter(visible=True)
            .first
        )
        expect(
            field_label,
            f"Visible checkbox field label '{field_text}' was not found",
        ).to_be_visible()

        label_id = field_label.get_attribute("id")
        if not label_id:
            raise ValueError(
                f"Checkbox field label '{field_text}' has no id attribute."
            )

        group = page.locator(
            f'[role="group"][aria-labelledby="{label_id}"]'
        ).first
        expect(
            group,
            f"Checkbox group for field '{field_text}' was not found",
        ).to_be_attached()

        checkbox = group.locator('input[type="checkbox"]').first
        expect(
            checkbox,
            f"Checkbox input for field '{field_text}' was not found",
        ).to_be_attached()
        return checkbox.is_checked()

    @staticmethod
    def select(page: Page, text: str, selected: bool = True) -> None:
        """
        Selects or deselects a checkbox safely by clicking its visible label.

        The checkbox is re-resolved after clicking because Appian may replace
        the control during a SAIL re-render. Final state validation uses an
        immediate ``is_checked()`` probe instead of waiting for the full
        framework assertion timeout on a stale locator.

        Args:
            page: Playwright Page instance.
            text: Visible checkbox label text.
            selected: True to check, False to uncheck.
        """
        label_text = text.strip()
        checkbox, label = CheckBox.__find_controls(page, label_text)
        current_state = checkbox.is_checked()

        if current_state == selected:
            return

        label.scroll_into_view_if_needed()
        label.click()

        checkbox, _ = CheckBox.__find_controls(page, label_text)
        expect(
            checkbox,
            f"Checkbox '{label_text}' did not reach selected={selected}.",
        ).to_be_checked(checked=selected)

        ComponentUtils.wait_for_appian_action_completed(page)
