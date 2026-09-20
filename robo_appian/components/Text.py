"""Generic helpers for locating, reading, and waiting on visible text content."""

from playwright.sync_api import Page, expect


class Text:
    """Read and synchronize on visible text in Appian pages."""

    @staticmethod
    def get_visible_text(
        page: Page,
        text: str,
        exact: bool = False,
    ) -> str:
        """Return normalized text from the first visible element matching the supplied text."""
        value = str(text or "").strip()
        if not value:
            raise ValueError("Text cannot be empty or whitespace.")

        locator = page.get_by_text(value, exact=exact).filter(visible=True).first
        expect(locator, f"Text '{value}' was not visible.").to_be_visible()
        return locator.inner_text().strip()

    @staticmethod
    def get_paragraph_text_containing(page: Page, text: str) -> str:
        """Return normalized paragraph text containing the requested text fragment."""
        value = str(text or "").strip()
        if not value:
            raise ValueError("Text cannot be empty or whitespace.")

        paragraph = page.locator("p", has_text=value).filter(visible=True).first
        expect(
            paragraph,
            f"No visible paragraph containing '{value}' was found.",
        ).to_be_visible()
        return paragraph.inner_text().strip()

    @staticmethod
    def wait_visible(page: Page, text: str, exact: bool = False) -> None:
        """Wait until the first matching text element is visible.

        Use this to synchronize with rendered Appian content. The method returns
        no locator; use ``get_visible_text`` when the displayed text is needed.

        Args:
            page: Appian page containing the expected text.
            text: Text to wait for.
            exact: Whether rendered text must match exactly.
        """
        value = str(text or "").strip()
        locator = page.get_by_text(value, exact=exact).filter(visible=True).first
        expect(locator, f"Text '{value}' was not visible.").to_be_visible()

    @staticmethod
    def wait_hidden(page: Page, text: str, exact: bool = False) -> None:
        """Wait until matching text is hidden or detached."""
        value = str(text or "").strip()
        locator = page.get_by_text(value, exact=exact).filter(visible=True).first
        expect(locator, f"Text '{value}' remained visible.").to_be_hidden()

    @staticmethod
    def get_link_text_near_label(page: Page, label: str) -> str:
        """
        Return the first non-placeholder link text in the presentation block
        owning a visible field label.
        """
        value = str(label or "").strip()
        if not value:
            raise ValueError("Label cannot be empty or whitespace.")

        label_node = page.get_by_text(value, exact=True).filter(visible=True).first
        expect(label_node, f"Label '{value}' was not visible.").to_be_visible()

        container = label_node.locator("xpath=ancestor::*[@role='presentation'][1]")
        link = (
            container.get_by_role("link")
            .filter(visible=True)
            .filter(has_not=page.locator("a[href='#']"))
            .first
        )
        expect(link, f"No link was found near label '{value}'.").to_be_visible()
        return link.inner_text().strip()
