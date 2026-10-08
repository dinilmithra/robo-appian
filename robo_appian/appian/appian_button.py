"""Appian button component abstraction."""

from __future__ import annotations

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
    ) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Button name cannot be empty or whitespace.")
        self._page = page
        self._name = name
        self._exact = exact
        self._scope = scope

    @property
    def name(self) -> str:
        """Return the button name used to identify this component."""
        return self._name

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
        """Return the first visible match for this button."""
        return self._locator().filter(visible=True).first

    def click(self) -> None:
        """Wait until the button is actionable, then click it."""
        button = self._wait_until_ready_locator()
        logger.info("Before Appian button click: name='%s'.", self._name)
        button.click()
        logger.info("After Appian button click: name='%s'.", self._name)

    def is_visible(self) -> bool:
        """Return whether the button is currently visible."""
        return self._locator().is_visible()

    def is_disabled(self) -> bool:
        """Return whether the HTML ``disabled`` attribute is present."""
        return self._visible_locator().get_attribute("disabled") is not None

    def is_enabled(self) -> bool:
        """Return whether the HTML ``disabled`` attribute is absent."""
        return not self.is_disabled()

    def _wait_until_ready_locator(self) -> Locator:
        """Wait until the button is visible and has no ``disabled`` attribute."""
        button = self._visible_locator()
        expect(
            button,
            f"Button '{self._name}' was not rendered and visible.",
        ).to_be_visible()
        expect(
            button,
            f"Button '{self._name}' was visible but remained disabled.",
        ).not_to_have_attribute("disabled", "")
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
        ).to_be_hidden()


__all__ = ["AppianButton"]
