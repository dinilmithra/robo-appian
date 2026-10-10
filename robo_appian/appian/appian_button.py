"""Appian button component abstraction."""

from __future__ import annotations

from robo_appian.utils.ComponentUtils import ComponentUtils

import logging
from typing import TYPE_CHECKING

from playwright.sync_api import Locator, expect

if TYPE_CHECKING:
    from .appian_locator import AppianLocator
    from .appian_page import AppianPage

logger = logging.getLogger(__name__)


class AppianButton:
    """Represent an Appian ``button`` element bound to a page and name.

    Appian action buttons are identified by the DOM contract
    ``<button type="button">``. A button is disabled when the HTML
    ``disabled`` attribute is present and enabled when that attribute is absent.
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
            raise ValueError("Button name cannot be empty or whitespace.")
        self._page = page
        self._name = name
        self._exact = exact
        self._scope = scope
        self._visible = ComponentUtils.normalize_visibility(visible)
        self._timeout = ComponentUtils.normalize_timeout_seconds(timeout)

    @property
    def name(self) -> str:
        """Return the button name used to identify this component."""
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

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """Return ``value`` as a safe XPath string literal."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'

        parts = value.split("'")
        literals: list[str] = []
        for index, part in enumerate(parts):
            if part:
                literals.append(f"'{part}'")
            if index < len(parts) - 1:
                literals.append('"\'"')
        return f"concat({', '.join(literals)})"

    @staticmethod
    def _normalized_xpath(expression: str) -> str:
        """Return an XPath expression normalized for Appian button text."""
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return (
            "translate("
            "normalize-space(translate(" + expression + ", '\u00a0', ' ')), "
            f"'{lowercase}', '{uppercase}')"
        )

    def _locator(self) -> Locator:
        """Return the live locator for this Appian button."""
        indexed = getattr(self, "_indexed_locator", None)
        if indexed is not None:
            return indexed
        normalized_name = " ".join(self._name.split()).upper()
        expected = self._xpath_literal(normalized_name)

        def compare(expression: str) -> str:
            normalized = self._normalized_xpath(expression)
            if self._exact:
                return f"{normalized} = {expected}"
            return f"contains({normalized}, {expected})"

        predicates = " or ".join(
            [
                compare("string(.)"),
                compare("@aria-label"),
                compare("@title"),
                compare("@data-owl-test-label"),
            ]
        )
        xpath = f"xpath=(.//button[@type='button' and ({predicates})])[1]"
        if self._scope is not None:
            return self._scope.locator.locator(xpath)
        return self._page.locator(xpath)

    def _visible_locator(self) -> Locator:
        """Return the first match after applying the visibility constraint."""
        locator = self._locator()
        if self._visible is not None:
            locator = locator.filter(visible=self._visible)
        return locator.first

    def click(self) -> None:
        """Wait for Appian, click the actionable button, then wait for completion."""
        from .appian_page import AppianPage

        page = AppianPage.get(self._page)
        page.wait_for_appian_action_completed(timeout=self._timeout)
        button = self._wait_until_ready_locator()
        logger.info("Before Appian button click: name='%s'.", self._name)
        button.click(**self._timeout_kwargs())
        logger.info("After Appian button click: name='%s'.", self._name)
        page.wait_for_appian_action_completed(timeout=self._timeout)

    def is_visible(self) -> bool:
        """Return whether the button is currently visible."""
        return self._locator().is_visible()

    def is_disabled(self) -> bool:
        """Return whether the HTML ``disabled`` attribute is present."""
        return self._visible_locator().get_attribute("disabled") is not None

    def is_enabled(self, timeout: float | int | None = None) -> bool:
        """Return whether the button is enabled, optionally waiting.

        Omitting ``timeout`` performs an immediate state query. Supplying a
        positive timeout in seconds waits up to that duration and returns
        ``False`` if the button never becomes enabled.
        """
        button = self._visible_locator()
        if timeout is None:
            if button.count() == 0:
                return False
            return button.get_attribute("disabled", timeout=0) is None

        try:
            expect(
                button,
                f"Button '{self._name}' did not become enabled.",
            ).to_be_enabled(**ComponentUtils.timeout_kwargs(timeout))
            return True
        except AssertionError:
            return False

    def _wait_until_ready_locator(self) -> Locator:
        """Wait until the button is visible and has no ``disabled`` attribute."""
        button = self._visible_locator()
        expect(
            button,
            f"Button '{self._name}' was not rendered and visible.",
        ).to_be_visible(**self._timeout_kwargs())
        expect(
            button,
            f"Button '{self._name}' was visible but remained disabled.",
        ).not_to_have_attribute("disabled", "", **self._timeout_kwargs())
        return button

    def wait_until_ready(self) -> "AppianButton":
        """Wait until the button is visible and enabled, then return it."""
        self._wait_until_ready_locator()
        return self

    def wait_until_hidden(self) -> None:
        """Wait until the button is hidden or removed."""
        expect(
            self._locator(),
            f"Button '{self._name}' remained visible.",
        ).to_be_hidden(**self._timeout_kwargs())


__all__ = ["AppianButton"]
