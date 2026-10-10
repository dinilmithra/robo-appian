"""Appian tab component abstraction."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.utils.ComponentUtils import ComponentUtils

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage


class AppianTab:
    """Represent an Appian linked-card tab identified by its visible name.

    Appian renders these tabs as ``role="link"`` containers. The same
    container includes accessibility-only state text:

    * ``Selected Tab.`` for the active tab;
    * ``Unselected Tab. Press enter to select tab.`` for an inactive tab.

    The component intentionally uses those semantic role/text relationships
    instead of generated Appian CSS classes.
    """

    _STATE_PATTERN = re.compile(r"^(?:Selected Tab\.|Unselected Tab\.)")
    _SELECTED_TEXT = "Selected Tab."

    def __init__(
        self,
        *,
        page: "AppianPage",
        name: str,
        exact: bool = True,
        scope: "AppianLocator | None" = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Tab name cannot be empty or whitespace.")
        self._page = page
        self._name = " ".join(name.split())
        self._exact = exact
        self._scope = scope
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

    @property
    def name(self) -> str:
        """Return the visible tab name used to identify this component."""
        return self._name

    def _root(self):
        """Return the framework-compatible scope used for tab lookup."""
        if self._scope is not None:
            return self._scope.locator
        return self._page

    def _locator(self) -> Locator:
        """Return a live semantic locator for the Appian tab container."""
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed
        root = self._root()
        label = root.get_by_text(self._name, exact=self._exact)
        state = root.get_by_text(self._STATE_PATTERN)
        return (
            root.get_by_role("link")
            .filter(has=label)
            .filter(has=state)
            .filter(visible=self._visible)
            .first
        )

    @property
    def visible(self) -> bool | None:
        """Return the visibility constraint used to resolve this component."""
        return self._visible

    @property
    def timeout(self) -> float | None:
        """Return this component's timeout override in seconds, if any."""
        return self._timeout

    def _timeout_kwargs(self, timeout: float | int | None = None) -> dict[str, float]:
        effective = self._timeout if timeout is None else timeout
        return ComponentUtils.timeout_kwargs(effective)

    @staticmethod
    def _selected_marker(tab: Locator) -> Locator:
        """Return the accessibility marker that identifies a selected tab."""
        return tab.get_by_text(AppianTab._SELECTED_TEXT, exact=True)

    def is_visible(self) -> bool:
        """Return whether this tab is currently visible."""
        return self._locator().is_visible()

    def is_selected(self, timeout: float | None = None) -> bool:
        """Return the tab's current selected state.

        ``timeout`` is used only to wait for the tab itself to become visible.
        Once the tab exists, the method returns its current state immediately;
        it does not wait for an unselected tab to become selected.
        """
        tab = self._locator()
        expect(tab, f"Appian tab '{self._name}' was not found.").to_be_visible(
            **self._timeout_kwargs(timeout)
        )
        return self._selected_marker(tab).count() > 0

    def select(self) -> "AppianTab":
        """Idempotently select this tab and wait for Appian to expose it as selected."""
        tab = self._locator()
        expect(tab, f"Appian tab '{self._name}' was not found.").to_be_visible(
            **self._timeout_kwargs()
        )

        if self._selected_marker(tab).count() > 0:
            return self

        tab.click(**self._timeout_kwargs())
        self._page.wait_for_appian_action_completed()

        # Appian can rerender the complete tab strip after selection, so resolve
        # the live locator again before checking the post-action state.
        tab = self._locator()
        expect(
            self._selected_marker(tab),
            f"Appian tab '{self._name}' did not become selected.",
        ).to_have_count(1, **self._timeout_kwargs())
        return self


__all__ = ["AppianTab"]
