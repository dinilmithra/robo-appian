"""Public exception types for robo-appian consumers."""

from __future__ import annotations

from typing import Any, Mapping

from robo_automation import RoboAutomationError


class RoboAppianError(RoboAutomationError):
    """Base exception for Appian-specific automation failures.

    Catch this exception when a caller wants to handle Appian component or
    Appian interaction failures separately from generic automation failures.

    Args:
        message: Clear description of what failed.
        code: Optional stable machine-readable error code.
        details: Optional structured context that helps diagnose the failure.
    """

    default_code = "ROBO_APPIAN_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message, code=code or self.default_code, details=details)


class RoboAppianNavigationError(RoboAppianError):
    """Appian navigation failure translated from robo-automation."""

    default_code = "ROBO_APPIAN_NAVIGATION_ERROR"
