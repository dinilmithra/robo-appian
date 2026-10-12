"""Read-only Appian text component."""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

from robo_appian.internal.component_support import ComponentSupport

if TYPE_CHECKING:
    from robo_appian.appian.locator.appian_locator import AppianLocator
    from robo_appian.appian.page.appian_page import AppianPage


class AppianText:
    """Represent visible business text rendered on an Appian page.

    Matching results preserve Appian display order. Use ``[0]`` or ``.first``
    when the same text appears more than once.
    """

    def __init__(
        self,
        *,
        page: "AppianPage",
        text: str,
        exact: bool = True,
        scope: "AppianLocator | None" = None,
        visible: bool | str | None = True,
        timeout: float | int | None = None,
    ) -> None:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text cannot be empty or whitespace.")
        self._page = page
        self._text = " ".join(text.split())
        self._exact = exact
        self._scope = scope
        self._visible = ComponentSupport.normalize_visibility(visible)
        self._timeout = ComponentSupport.normalize_timeout_seconds(timeout)

    @property
    def text(self) -> str:
        """Return the normalized text used to identify this component."""
        return self._text

    @property
    def first(self) -> "AppianText":
        """Return the first matching text component."""
        return self[0]

    def __getitem__(self, index: int) -> "AppianText":
        """Return a zero-based matching text component in display order."""
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("text index must be an integer.")
        if index < 0:
            raise IndexError("text index cannot be negative.")
        item = AppianText(
            page=self._page,
            text=self._text,
            exact=self._exact,
            scope=self._scope,
            visible=self._visible,
            timeout=self._timeout,
        )
        item._indexed_locator = self._matches().nth(index)
        return item

    def _timeout_kwargs(self, timeout: float | int | None = None) -> dict[str, float]:
        effective = self._timeout if timeout is None else timeout
        return ComponentSupport.timeout_kwargs(effective)

    def _root(self):
        if self._scope is not None:
            return self._scope.locator
        return self._page

    def _matches(self) -> Locator:
        root = self._root()
        locator = root.get_by_text(self._text, exact=self._exact)
        if self._visible is not None:
            locator = locator.filter(visible=self._visible)
        return locator

    def _locator(self) -> Locator:
        indexed = getattr(self, "_indexed_locator", None)
        return indexed if indexed is not None else self._matches()

    @property
    def count(self) -> int:
        """Return the number of matching text components."""
        return self._matches().count()

    @property
    def value(self) -> str:
        """Return the matching rendered text with whitespace normalized.

        Direct ``.value`` requires exactly one match. When several matches are
        present, select one explicitly with ``[0]`` or ``.first``.
        """
        locator = self._locator()
        count = locator.count()
        if count == 0:
            raise LookupError(f"No text matched '{self._text}'.")
        if count != 1:
            raise LookupError(
                f"{count} text values matched '{self._text}'. "
                "Use [0], [1], or .first to select one."
            )
        return " ".join((locator.inner_text(**self._timeout_kwargs()) or "").replace("\u00a0", " ").split())

    def is_visible(self) -> bool:
        """Return whether at least one matching text component is visible."""
        return self._matches().first.is_visible()

    def wait_until_visible(self, timeout: float | int | None = None) -> "AppianText":
        """Wait until matching text is visible and return this component."""
        expect(self._matches().first, f"Appian text '{self._text}' was not visible.").to_be_visible(
            **self._timeout_kwargs(timeout)
        )
        return self

    def wait_until_hidden(self, timeout: float | int | None = None) -> "AppianText":
        """Wait until matching text is hidden and return this component."""
        expect(self._matches().first, f"Appian text '{self._text}' remained visible.").to_be_hidden(
            **self._timeout_kwargs(timeout)
        )
        return self


__all__ = ["AppianText"]
