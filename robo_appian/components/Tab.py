"""Generic semantic tab helpers.

Tab state is determined from roles, accessibility attributes, visible labels,
and selected-state text rather than application or CSS class names.
"""

import logging
import re

from playwright.sync_api import Locator, expect
from robo_automation import Scope

logger = logging.getLogger(__name__)


class Tab:
    """Reusable operations for Appian tab controls."""

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
        scope: Scope,
        tab_name: str,
        excat_match: bool = False,
    ) -> Locator:
        """
        Locate a link-based tab using semantic role, visible label, and the
        accessibility state text rendered inside the same element.

        No CSS class names or Appian implementation-specific class selectors
        are used.
        """
        label = scope.get_by_text(tab_name, exact=excat_match)
        state_marker = scope.get_by_text(Tab._TAB_STATE_PATTERN)

        return (
            scope.get_by_role("link")
            .filter(has=label)
            .filter(has=state_marker)
            .filter(visible=True)
        )

    @staticmethod
    def _aria_tab(
        scope: Scope,
        tab_name: str,
        excat_match: bool = False,
    ) -> Locator:
        """Return visible standard ARIA tabs matching the requested name."""
        return scope.get_by_role(
            "tab",
            name=tab_name,
            exact=excat_match,
        ).filter(visible=True)

    @staticmethod
    def _button_tab(
        scope: Scope,
        tab_name: str,
        excat_match: bool = False,
    ) -> Locator:
        """Return visible button-based tabs matching the requested name."""
        return scope.get_by_role(
            "button",
            name=tab_name,
            exact=excat_match,
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
                button.get_attribute("aria-current") == "scope",
            )
        )

    @staticmethod
    def is_tab_active(
        scope: Scope,
        tab_name: str,
        excat_match: bool = False,
    ) -> bool:
        """Return True when the requested tab is currently selected.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            tab_name: Value supplied for ``tab_name``.
            excat_match: Whether matching must use the complete label or text.


        Returns:
            bool: ``True`` when the requested Appian tab is active; otherwise ``False``.
        """
        name = Tab._validate_name(tab_name)

        linked_tab = Tab._linked_tab(scope, name, excat_match=excat_match)
        if linked_tab.count() > 0:
            return Tab._linked_tab_is_active(linked_tab)

        aria_tab = Tab._aria_tab(scope, name, excat_match=excat_match)
        if aria_tab.count() > 0:
            return aria_tab.first.get_attribute("aria-selected") == "true"

        button_tab = Tab._button_tab(scope, name, excat_match=excat_match)
        if button_tab.count() > 0:
            return Tab._button_is_active(button_tab.first)

        return False

    @staticmethod
    def click(
        scope: Scope,
        tab_name: str,
        excat_match: bool = False,
    ) -> None:
        """Select a tab only when it is inactive.

        Selection is determined from semantic accessibility state rather than
        CSS classes. After clicking, the method waits for the selected state
        before returning.

        Args:
            scope: Playwright ``Page`` or ``Locator``. Pass a ``Page`` to search the entire current document; pass a ``Locator`` to restrict the operation to that locator/container.
            tab_name: Value supplied for ``tab_name``.
            excat_match: Whether matching must use the complete label or text.
        """
        name = Tab._validate_name(tab_name)

        # Appian frequently re-renders the tab strip after form/dialog actions.
        # Locator.count() is immediate and can observe a transient zero during
        # that re-render, so wait for any supported semantic tab representation
        # before inspecting its selected state.
        linked_tab = Tab._linked_tab(scope, name, excat_match=excat_match)
        aria_tab = Tab._aria_tab(scope, name, excat_match=excat_match)
        button_tab = Tab._button_tab(scope, name, excat_match=excat_match)
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
                scope, name, excat_match=excat_match
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
