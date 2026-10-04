"""Generic helpers for locating, reading, and waiting on visible text content."""

from playwright.sync_api import Page, expect
from robo_appian.utils.types import Scope


class Text:
    """Reusable operations for visible text in Appian pages."""

    @staticmethod
    def get_visible_text(
        scope: Scope,
        text: str,
        excat_match: bool = False,
    ) -> str:
        """Return normalized text from the first visible element matching the supplied text.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Visible text used to identify the target element.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            str: The visible text from the matching Appian text element.
        """
        value = str(text or "").strip()
        if not value:
            raise ValueError("Text cannot be empty or whitespace.")

        locator = scope.get_by_text(value, exact=excat_match).filter(visible=True).first
        expect(locator, f"Text '{value}' was not visible.").to_be_visible()
        return locator.inner_text().strip()

    @staticmethod
    def get_paragraph_text_containing(scope: Scope, text: str) -> str:
        """Return normalized paragraph text containing the requested text fragment.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Visible text used to identify the target element.


        Returns:
            str: The paragraph text containing the requested text.
        """
        value = str(text or "").strip()
        if not value:
            raise ValueError("Text cannot be empty or whitespace.")

        paragraph = scope.locator("p", has_text=value).filter(visible=True).first
        expect(
            paragraph,
            f"No visible paragraph containing '{value}' was found.",
        ).to_be_visible()
        return paragraph.inner_text().strip()

    @staticmethod
    def wait_visible(scope: Scope, text: str, excat_match: bool = False) -> None:
        """Wait until the first matching text element is visible.

        Use this to synchronize with rendered Appian content. The method returns
        no locator; use ``get_visible_text`` when the displayed text is needed.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Text to wait for.
            excat_match: Whether rendered text must match exactly.
        """
        value = str(text or "").strip()
        locator = scope.get_by_text(value, exact=excat_match).filter(visible=True).first
        expect(locator, f"Text '{value}' was not visible.").to_be_visible()

    @staticmethod
    def wait_hidden(scope: Scope, text: str, excat_match: bool = False) -> None:
        """Wait until matching text is hidden or detached.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            text: Visible text used to identify the target element.
            excat_match: Whether matching must use the complete label or text.
        """
        value = str(text or "").strip()
        locator = scope.get_by_text(value, exact=excat_match).filter(visible=True).first
        expect(locator, f"Text '{value}' remained visible.").to_be_hidden()

    @staticmethod
    def get_link_text_near_label(scope: Scope, label: str) -> str:
        """Return the first non-placeholder link text in the presentation block
        owning a visible field label.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            label: Visible or accessible label used to identify the control.


        Returns:
            str: The visible link text associated with the nearby label.
        """
        value = str(label or "").strip()
        if not value:
            raise ValueError("Label cannot be empty or whitespace.")

        label_node = scope.get_by_text(value, exact=True).filter(visible=True).first
        expect(label_node, f"Label '{value}' was not visible.").to_be_visible()

        container = label_node.locator("xpath=ancestor::*[@role='presentation'][1]")
        link = (
            container.get_by_role("link")
            .filter(visible=True)
            .filter(has_not=scope.locator("a[href='#']"))
            .first
        )
        expect(link, f"No link was found near label '{value}'.").to_be_visible()
        return link.inner_text().strip()
