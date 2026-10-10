"""Appian-level runtime boundary over robo-automation infrastructure.

Consumer projects should depend on these Appian abstractions rather than
importing robo-automation browser, correlation, or performance classes directly.
"""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import dataclass
from typing import Any, Iterator, Mapping, Optional

from robo_automation import build_test_case_id, current_correlation, is_framework_page
from robo_automation.browser import (
    close_resource,
    create_browser_context,
    create_browser_page,
)

from .appian import AppianPage


@dataclass(frozen=True)
class AutomationContext:
    """Correlation metadata for the currently executing automation test."""

    test_case_id: str = ""
    process_id: str = ""
    attempt_id: str = ""
    worker_id: str = ""

    def to_dict(self) -> dict[str, str]:
        """Return the context in log/evidence friendly form."""
        return {
            "test_case_id": self.test_case_id,
            "process_id": self.process_id,
            "attempt_id": self.attempt_id,
            "worker_id": self.worker_id,
        }


class AppianContext:
    """Appian-facing browser-context wrapper.

    The lower-layer robo-automation context remains private to robo-appian.
    """

    def __init__(self, context: Any) -> None:
        self._context = context

    def storage_state(self) -> dict[str, Any]:
        """Return the current browser storage state."""
        return dict(self._context.storage_state())

    def close(self) -> None:
        """Close this context."""
        self._context.close()


class AppianRuntime:
    """Appian runtime service for browser/session mechanics.

    CORE and other Appian consumers can use this class without knowing about
    BrowserSession, RoboBrowserContext, or PytestPerformanceMonitor.
    """

    def __init__(
        self,
        browser: Any,
        performance_monitor: Any = None,
        *,
        wait_time_seconds: int = 90,
    ) -> None:
        self._browser = browser
        self._performance_monitor = performance_monitor
        self.wait_time_seconds = int(wait_time_seconds)

    def measure(
        self,
        action: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        """Measure an Appian consumer operation when monitoring is enabled."""
        monitor = self._performance_monitor
        if monitor is None:
            return nullcontext()
        return monitor.measure(action, metadata=dict(metadata or {}) or None)

    def record_duration(
        self,
        action: str,
        duration_ms: float,
        *,
        ok: bool = True,
        error_type: str | None = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> None:
        """Record a framework duration without exposing the monitor class."""
        monitor = self._performance_monitor
        if monitor is None:
            return
        monitor.record_framework_duration(
            action,
            duration_ms,
            ok=ok,
            error_type=error_type,
            metadata=dict(metadata or {}) or None,
        )

    def attach_page(self, page: AppianPage) -> None:
        """Attach performance monitoring to an Appian page when enabled."""
        monitor = self._performance_monitor
        if monitor is not None:
            monitor.attach_page(page)

    def create_context(
        self,
        *,
        context_options: Optional[dict[str, Any]] = None,
        wait_time_seconds: int | None = None,
    ) -> AppianContext:
        """Create a configured Appian browser context."""
        context = create_browser_context(
            self._browser,
            context_options=context_options,
            wait_time_seconds=(
                self.wait_time_seconds
                if wait_time_seconds is None
                else int(wait_time_seconds)
            ),
        )
        return AppianContext(context)

    def create_page(self, context: AppianContext) -> AppianPage:
        """Create an Appian page inside ``context``."""
        page = create_browser_page(context._context, AppianPage)
        assert isinstance(page, AppianPage)
        return page

    def close(self, resource: Any, label: str) -> None:
        """Close a runtime resource without masking an earlier failure."""
        target = resource._context if isinstance(resource, AppianContext) else resource
        close_resource(target, label)


def current_automation_context(*, worker_id: str = "") -> AutomationContext:
    """Return current testcase correlation without exposing robo-automation."""
    values = current_correlation()
    return AutomationContext(
        test_case_id=str(values.get("test_case_id", "") or ""),
        process_id=str(values.get("process_id", "") or ""),
        attempt_id=str(values.get("attempt_id", "") or ""),
        worker_id=str(worker_id or values.get("worker_id", "") or ""),
    )


def automation_test_case_id(nodeid: str) -> str:
    """Build the stable automation testcase ID for ``nodeid``."""
    return build_test_case_id(nodeid)


def automation_context_for(value: Any, *, nodeid: str = "") -> AutomationContext:
    """Return correlation metadata stored on a pytest item/report-like object."""
    effective_nodeid = str(nodeid or getattr(value, "nodeid", "") or "")
    current = current_automation_context()
    return AutomationContext(
        test_case_id=str(
            getattr(value, "_robo_test_case_id", "")
            or getattr(value, "core_test_case_id", "")
            or current.test_case_id
            or (automation_test_case_id(effective_nodeid) if effective_nodeid else "")
        ),
        process_id=str(
            getattr(value, "_robo_process_id", "")
            or getattr(value, "core_process_id", "")
            or current.process_id
        ),
        attempt_id=str(
            getattr(value, "_robo_attempt_id", "")
            or getattr(value, "core_attempt_id", "")
            or current.attempt_id
        ),
        worker_id=current.worker_id,
    )


def automation_test_log_path(value: Any) -> str:
    """Return the testcase log path attached by the lower pytest runtime."""
    return str(
        getattr(value, "_robo_testcase_log_path", "")
        or getattr(value, "core_test_log_path", "")
        or ""
    )


def resolve_appian_page(value: object) -> AppianPage | None:
    """Return ``value`` as an AppianPage when it is a framework page wrapper."""
    if isinstance(value, AppianPage):
        return value
    if is_framework_page(value):
        specialized = value.specialize(AppianPage)  # type: ignore[attr-defined]
        return specialized if isinstance(specialized, AppianPage) else None
    return None


def measure_appian_runtime(
    config: Any, action: str, *, metadata: Mapping[str, Any] | None = None
):
    """Measure a pytest lifecycle operation through the lower runtime if available."""
    monitor = getattr(config, "_performance_monitor", None)
    if monitor is None:
        monitor = getattr(config, "_master_performance_monitor", None)
    if monitor is None:
        return nullcontext()
    return monitor.measure(action, metadata=dict(metadata or {}) or None)
