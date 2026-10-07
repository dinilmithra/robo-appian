"""Appian-specific page wrapper."""

from robo_automation import RoboPage

from .appian_button import AppianButton
from .appian_locator import AppianLocator


class AppianPage(RoboPage):
    """RoboPage specialization that exposes Appian-aware components and locators."""

    locator_class = AppianLocator

    def button(
        self,
        *,
        name: str,
        exact: bool = True,
        scope: AppianLocator | None = None,
    ) -> AppianButton:
        """Return an Appian button component identified by ``name``.

        Args:
            name: Visible or accessible button name.
            exact: Whether the complete normalized button name must match.
            scope: Optional locator scope used to restrict the button search.

        Returns:
            The Appian button component bound to this page.
        """
        return AppianButton(page=self, name=name, exact=exact, scope=scope)


__all__ = ["AppianPage"]
