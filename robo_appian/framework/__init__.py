"""Framework-level Playwright wrappers used by robo-appian.

``RoboBrowser`` wraps a Playwright ``Browser``; ``RoboContext`` wraps a
``BrowserContext``; ``RoboPage`` wraps a ``Page``; and ``RoboLocator`` wraps a
``Locator``. Component modules build on these wrappers, while the wrappers
remain framework-level objects rather than UI components.
"""

from robo_appian.framework.robo_browser import RoboBrowser
from robo_appian.framework.robo_context import RoboContext
from robo_appian.framework.robo_locator import RoboLocator
from robo_appian.framework.robo_page import RoboPage

__all__ = ["RoboBrowser", "RoboContext", "RoboPage", "RoboLocator"]
