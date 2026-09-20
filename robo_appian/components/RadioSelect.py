"""Generic helpers for selecting values from Appian radio-button groups."""

from typing import Union

from playwright.sync_api import Locator, Page, expect


class RadioSelect:
    """Utility for selecting Appian radio options using live Appian DOM relationships."""

    @staticmethod
    def __xpath_literal(value: str) -> str:
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        parts = value.split("'")
        return "concat(" + ', "\'", '.join(f"'{part}'" for part in parts) + ")"

    @staticmethod
    def __find_visible_label(
        scope: Union[Locator, Page],
        text: str,
    ) -> Locator:
        label_text = str(text or "").strip()
        if not label_text:
            raise ValueError("Radio option text cannot be empty.")

        # Appian renders the interactive label immediately after its native
        # radio input. Keep this locator live across SAIL rerenders.
        literal = RadioSelect.__xpath_literal(label_text)
        label = scope.locator(
            "xpath=(.//label[@for and normalize-space(string(.))=" + literal + "])[1]"
        )
        expect(
            label, f"Visible radio option '{label_text}' was not found."
        ).to_be_visible()
        return label

    @staticmethod
    def __find_locator(
        scope: Union[Locator, Page],
        text: str,
    ) -> Locator:
        label = RadioSelect.__find_visible_label(scope, text)
        # In Appian RadioSelect markup the input is the immediately preceding
        # sibling of the label. This avoids reading a transient dynamic id and
        # then looking it up after a rerender.
        radio = label.locator("xpath=preceding-sibling::input[@type='radio'][1]")
        expect(radio, f"Radio input linked to '{text}' was not found.").to_be_attached()
        return radio

    @staticmethod
    def __select_in_scope(
        scope: Union[Locator, Page],
        text: str,
    ) -> None:
        label_text = str(text or "").strip()
        if not label_text:
            raise ValueError("Radio option text cannot be empty.")

        radio = RadioSelect.__find_locator(scope, label_text)
        if radio.is_checked():
            return

        label = RadioSelect.__find_visible_label(scope, label_text)
        label.click()

        # Re-resolve through the live label relationship and let Playwright's
        # configured default timeout absorb the Appian rerender.
        radio = RadioSelect.__find_locator(scope, label_text)
        expect(radio, f"Radio option '{label_text}' was not selected.").to_be_checked()

    @staticmethod
    def click_locator(locator: Locator, option_text: str) -> None:
        """Select a radio option within the supplied Appian container.

        Args:
            locator: Appian container that scopes the radio option lookup.
            option_text: Visible option text to select.
        """
        RadioSelect.__select_in_scope(locator, option_text)

    @staticmethod
    def click_in_group(
        page: Page,
        group_label: str,
        option_name: str,
        exact: bool = True,
    ) -> None:
        """Select an option within one named Appian radio group.

        Appian exposes RadioSelect groups as ``role=radiogroup`` with an
        accessible name from ``aria-labelledby``. Scoping prevents ambiguous
        Yes/No options elsewhere on the same page.
        """
        normalized_group = str(group_label or "").strip()
        if not normalized_group:
            raise ValueError("Radio group label cannot be empty.")
        group = (
            page.get_by_role("radiogroup", name=normalized_group, exact=exact)
            .filter(visible=True)
            .first
        )
        expect(
            group, f"Radio group '{normalized_group}' was not visible."
        ).to_be_visible()
        RadioSelect.__select_in_scope(group, option_name)

    @staticmethod
    def click(page: Page, option_text: str) -> None:
        """Select a visible Appian radio option on the page.

        Args:
            page: Current Playwright page.
            option_text: Visible option text to select.
        """
        RadioSelect.__select_in_scope(page, option_text)
