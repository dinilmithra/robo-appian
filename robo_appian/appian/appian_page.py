"""Appian-specific page wrapper."""

from robo_automation import RoboPage

from .appian_button import AppianButton
from .appian_date import AppianDate
from .appian_textbox import AppianTextbox
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

    def textbox(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        scope: AppianLocator | None = None,
    ) -> AppianTextbox:
        """Return an Appian textbox identified by label, placeholder, or header.

        Specify exactly one identifier. Header lookup binds the matching header
        text to the first supported textbox that follows it.
        """
        return AppianTextbox(
            page=self,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            scope=scope,
        )

    def date(
        self,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        header: str | None = None,
        exact: bool = True,
        scope: AppianLocator | None = None,
    ) -> AppianDate:
        """Return an Appian date field identified by label, placeholder, or header."""
        return AppianDate(
            page=self,
            label=label,
            placeholder=placeholder,
            header=header,
            exact=exact,
            scope=scope,
        )


__all__ = ["AppianPage"]
