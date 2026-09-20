"""Generic helpers for semantic link interaction and link-state validation."""

import logging

from playwright.sync_api import Page, expect

from robo_appian.utils import ComponentUtils

logger = logging.getLogger(__name__)


class Link:
    """Find, read, wait for, and click visible semantic links."""

    @staticmethod
    def is_visible(page: Page, accessible_name: str, exact: bool = False) -> bool:
        """Return whether a link with the semantic name is visible."""
        if not accessible_name or not accessible_name.strip():
            return False
        link = page.get_by_role(
            "link", name=accessible_name.strip(), exact=exact
        ).filter(visible=True)
        return link.count() > 0

    @staticmethod
    def wait_visible(page: Page, accessible_name: str, exact: bool = False) -> None:
        """Wait until a link with the semantic name becomes visible."""
        link = (
            page.get_by_role("link", name=accessible_name.strip(), exact=exact)
            .filter(visible=True)
            .first
        )
        expect(link, f"Link '{accessible_name}' was not visible.").to_be_visible()

    @staticmethod
    def get_text(
        page: Page,
        accessible_name: str,
        exact: bool = False,
    ) -> str:
        """Return visible/accessibility text for a link by semantic name."""
        if not accessible_name or not accessible_name.strip():
            raise ValueError("Link name cannot be empty.")

        link = (
            page.get_by_role("link", name=accessible_name.strip(), exact=exact)
            .filter(visible=True)
            .first
        )
        expect(link, f"Link '{accessible_name}' was not visible.").to_be_visible()
        return (link.text_content() or "").strip()

    @staticmethod
    def click(page: Page, link_text: str) -> None:
        """Click the first visible link whose rendered text contains a value.

        Use this when partial visible text uniquely identifies the link. This
        method does not perform an exact accessible-name match.

        Args:
            page: Appian page containing the link.
            link_text: Text substring expected within the link.

        Raises:
            RuntimeError: If no matching visible link is available.
        """
        target_link = (
            page.get_by_role("link")
            .filter(has_text=link_text)
            .filter(visible=True)
            .first
        )

        try:
            expect(target_link).to_be_visible()
        except Exception as exc:
            raise RuntimeError(
                f"Link with text '{link_text}' is not visible and cannot be clicked."
            ) from exc

        ComponentUtils.click(target_link)
