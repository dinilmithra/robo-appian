"""Appian-specific locator extension point."""

from robo_automation import RoboLocator


class AppianLocator(RoboLocator):
    """RoboLocator specialization reserved for Appian interaction semantics."""


__all__ = ["AppianLocator"]
