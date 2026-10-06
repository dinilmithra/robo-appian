"""Appian-specific page wrapper."""

from robo_automation import RoboPage

from .appian_locator import AppianLocator


class AppianPage(RoboPage):
    """RoboPage specialization that returns Appian locators for wrapped lookups."""

    locator_class = AppianLocator


__all__ = ["AppianPage"]
