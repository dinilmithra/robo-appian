"""Generic helpers for semantic link interaction and link-state validation."""

import logging

from playwright.sync_api import Page, expect
from robo_appian.utils.types import Scope

from robo_appian.utils import ComponentUtils

logger = logging.getLogger(__name__)


class Link:
    """Reusable operations for Appian link controls."""

    @staticmethod
    def is_visible(scope: Scope, accessible_name: str, excat_match: bool = False) -> bool:
        """Return whether a link with the semantic name is visible.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            accessible_name: Accessible name used to identify the control.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            bool: ``True`` when a matching Appian link is visible; otherwise ``False``.
        """
        if not accessible_name or not accessible_name.strip():
            return False
        link = scope.get_by_role(
            "link", name=accessible_name.strip(), exact=excat_match
        ).filter(visible=True)
        return link.count() > 0

    @staticmethod
    def wait_visible(scope: Scope, accessible_name: str, excat_match: bool = False) -> None:
        """Wait until a link with the semantic name becomes visible.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            accessible_name: Accessible name used to identify the control.
            excat_match: Whether matching must use the complete label or text.
        """
        link = (
            scope.get_by_role("link", name=accessible_name.strip(), exact=excat_match)
            .filter(visible=True)
            .first
        )
        expect(link, f"Link '{accessible_name}' was not visible.").to_be_visible()

    @staticmethod
    def get_text(
        scope: Scope,
        accessible_name: str,
        excat_match: bool = False,
    ) -> str:
        """Return visible/accessibility text for a link by semantic name.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            accessible_name: Accessible name used to identify the control.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            str: The visible text of the matching Appian link.
        """
        if not accessible_name or not accessible_name.strip():
            raise ValueError("Link name cannot be empty.")

        link = (
            scope.get_by_role("link", name=accessible_name.strip(), exact=excat_match)
            .filter(visible=True)
            .first
        )
        expect(link, f"Link '{accessible_name}' was not visible.").to_be_visible()
        return (link.text_content() or "").strip()

    @staticmethod
    def click(scope: Scope, link_text: str) -> None:
        """Click the first visible link whose rendered text contains a value.

        Use this when partial visible text uniquely identifies the link. This
        method does not perform an excat_match accessible-name match.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            link_text: Text substring expected within the link.

        Raises:
            RuntimeError: If no matching visible link is available.
        """
        target_link = (
            scope.get_by_role("link")
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
