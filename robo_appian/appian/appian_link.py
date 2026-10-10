"""Appian link component abstraction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.utils.ComponentUtils import ComponentUtils

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage


class AppianLink:
    """Represent an Appian link identified by its accessible/visible name.

    Appian renders links in more than one semantic HTML shape. Native rich-text
    links are ``<a>`` elements, while linked cards expose ``role="link"`` on a
    non-anchor container. The runtime's role locator covers both forms without
    relying on generated Appian CSS classes.
    """

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
            raise ValueError("Link name cannot be empty or whitespace.")
        self._page = page
        self._name = " ".join(name.split())
        self._exact = exact
        self._scope = scope
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

    @property
    def name(self) -> str:
        """Return the normalized link name used to identify this component."""
        return self._name

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

    def _root(self):
        """Return the framework-compatible scope used for link lookup."""
        if self._scope is not None:
            return self._scope.locator
        return self._page

    def _locator(self) -> Locator:
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed
        """Return a live semantic locator for the first visible matching link."""
        locator = self._root().get_by_role("link", name=self._name, exact=self._exact)
        if self._visible is not None:
            locator = locator.filter(visible=self._visible)
        return locator.first

    def is_visible(self) -> bool:
        """Return whether this link is currently visible."""
        return self._locator().is_visible()

    def wait_until_visible(self, timeout: float | None = None) -> "AppianLink":
        """Wait until this link is visible, then return this component."""
        link = self._locator()
        expect(link, f"Appian link '{self._name}' was not visible.").to_be_visible(
            **self._timeout_kwargs(timeout)
        )
        return self

    def click(self) -> "AppianLink":
        """Click this link and wait for the Appian action cycle to complete."""
        link = self._locator()
        expect(link, f"Appian link '{self._name}' was not visible.").to_be_visible(
            **self._timeout_kwargs()
        )
        link.click(**self._timeout_kwargs())
        ComponentUtils.wait_for_appian_action_completed(self._page)
        return self

    def get_text(self) -> str:
        """Return the rendered text of the link with whitespace normalized."""
        link = self._locator()
        expect(link, f"Appian link '{self._name}' was not visible.").to_be_visible(
            **self._timeout_kwargs()
        )
        return " ".join((link.inner_text() or "").split())

    def href(self) -> str | None:
        """Return the native ``href`` value, or ``None`` for linked-card links."""
        link = self._locator()
        expect(link, f"Appian link '{self._name}' was not visible.").to_be_visible(
            **self._timeout_kwargs()
        )
        return link.get_attribute("href")


__all__ = ["AppianLink"]
