"""Generic semantic tab helpers.

Tab state is determined from roles, accessibility attributes, visible labels,
and selected-state text rather than application or CSS class names.
"""

import logging
import re

from playwright.sync_api import Locator, Page, expect

logger = logging.getLogger(__name__)


class Tab:
    """Utilities for selecting tabs by semantic roles and state."""

    _SELECTED_MARKER = "Selected Tab."
    _TAB_STATE_PATTERN = re.compile(r"^(?:Selected|Unselected) Tab\.")

    @staticmethod
    def _validate_name(tab_name: str) -> str:
        """Normalize and validate a requested tab name."""
        name = str(tab_name or "").strip()
        if not name:
            raise ValueError("Tab name cannot be empty or whitespace.")
        return name

    @staticmethod
    def _linked_tab(
        page: Page,
        tab_name: str,
        exact: bool = False,
    ) -> Locator:
        """
        Locate a link-based tab using semantic role, visible label, and the
        accessibility state text rendered inside the same element.

        No CSS class names or Appian implementation-specific class selectors
        are used.
        """
        label = page.get_by_text(tab_name, exact=exact)
        state_marker = page.get_by_text(Tab._TAB_STATE_PATTERN)

        return (
            page.get_by_role("link")
            .filter(has=label)
            .filter(has=state_marker)
            .filter(visible=True)
        )

    @staticmethod
    def _aria_tab(
        page: Page,
        tab_name: str,
        exact: bool = False,
    ) -> Locator:
        """Return visible standard ARIA tabs matching the requested name."""
        return page.get_by_role(
            "tab",
            name=tab_name,
            exact=exact,
        ).filter(visible=True)

    @staticmethod
    def _button_tab(
        page: Page,
        tab_name: str,
        exact: bool = False,
    ) -> Locator:
        """Return visible button-based tabs matching the requested name."""
        return page.get_by_role(
            "button",
            name=tab_name,
            exact=exact,
        ).filter(visible=True)

    @staticmethod
    def _linked_tab_is_active(tab: Locator) -> bool:
        """Return whether a semantic linked-card tab exposes the selected-state marker."""
        if tab.count() == 0:
            return False

        return (
            tab.first.get_by_text(
                Tab._SELECTED_MARKER,
                exact=True,
            ).count()
            > 0
        )

    @staticmethod
    def _button_is_active(button: Locator) -> bool:
        """Return whether a button-based tab exposes an active ARIA state."""
        return any(
            (
                button.get_attribute("aria-selected") == "true",
                button.get_attribute("aria-pressed") == "true",
                button.get_attribute("aria-current") == "page",
            )
        )

    @staticmethod
    def is_tab_active(
        page: Page,
        tab_name: str,
        exact: bool = False,
    ) -> bool:
        """Return True when the requested tab is currently selected."""
        name = Tab._validate_name(tab_name)

        linked_tab = Tab._linked_tab(page, name, exact=exact)
        if linked_tab.count() > 0:
            return Tab._linked_tab_is_active(linked_tab)

        aria_tab = Tab._aria_tab(page, name, exact=exact)
        if aria_tab.count() > 0:
            return aria_tab.first.get_attribute("aria-selected") == "true"

        button_tab = Tab._button_tab(page, name, exact=exact)
        if button_tab.count() > 0:
            return Tab._button_is_active(button_tab.first)

        return False

    @staticmethod
    def click(
        page: Page,
        tab_name: str,
        exact: bool = False,
    ) -> None:
        """
        Select a tab only when it is inactive.

        Selection is determined from semantic accessibility state rather than
        CSS classes. After clicking, the method waits for the selected state
        before returning.
        """
        name = Tab._validate_name(tab_name)

        # Appian frequently re-renders the tab strip after form/dialog actions.
        # Locator.count() is immediate and can observe a transient zero during
        # that re-render, so wait for any supported semantic tab representation
        # before inspecting its selected state.
        linked_tab = Tab._linked_tab(page, name, exact=exact)
        aria_tab = Tab._aria_tab(page, name, exact=exact)
        button_tab = Tab._button_tab(page, name, exact=exact)
        available_tab = (
            linked_tab.or_(aria_tab).or_(button_tab).filter(visible=True).first
        )
        expect(
            available_tab,
            f"Cannot click: No visible tab named '{name}' found.",
        ).to_be_visible()

        if linked_tab.count() > 0:
            tab = linked_tab.first

            if Tab._linked_tab_is_active(tab):
                logger.info("Tab '%s' is already active; click skipped.", name)
                return

            expect(
                tab,
                f"Cannot click: Tab '{name}' is not visible.",
            ).to_be_visible()
            tab.click()

            selected_marker = Tab._linked_tab(
                page, name, exact=exact
            ).first.get_by_text(Tab._SELECTED_MARKER, exact=True)
            expect(
                selected_marker,
                f"Tab '{name}' did not become active after click.",
            ).to_have_count(1)

            logger.info("Tab '%s' selected.", name)
            return

        if aria_tab.count() > 0:
            tab = aria_tab.first

            if tab.get_attribute("aria-selected") == "true":
                logger.info("Tab '%s' is already active; click skipped.", name)
                return

            expect(tab).to_be_visible()
            tab.click()
            expect(
                tab,
                f"Tab '{name}' did not become active after click.",
            ).to_have_attribute("aria-selected", "true")
            return

        if button_tab.count() > 0:
            button = button_tab.first

            if Tab._button_is_active(button):
                logger.info("Tab '%s' is already active; click skipped.", name)
                return

            expect(button).to_be_visible()
            button.click()
            return

        raise AssertionError(f"Cannot click: No visible tab named '{name}' found.")
