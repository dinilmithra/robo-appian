"""Reusable browser automation helpers for Appian UI automation.

`robo_appian` contains generic interaction mechanics only. Application-specific
business rules, workflow names, test data, and assertions belong in the
consumer project's component layer.
"""

from robo_appian.errors import RoboAppianError, RoboAppianNavigationError
from robo_appian.assertions import (
    assert_not_text,
    assert_text,
    assert_visible,
    wait_visible,
)
from robo_appian.runtime import (
    AppianRuntime,
    AppianContext,
    AutomationContext,
    automation_context_for,
    automation_test_case_id,
    automation_test_log_path,
    current_automation_context,
    measure_appian_runtime,
    resolve_appian_page,
)
from robo_appian.appian import (
    AppianButton,
    AppianCheckbox,
    AppianInputComponent,
    AppianRadioSelect,
    AppianDate,
    AppianDropdown,
    AppianTextbox,
    AppianTab,
    AppianLink,
    AppianRow,
    AppianCell,
    AppianColumn,
    AppianLocator,
    AppianPage,
    AppianScope,
    AppianTable,
)
from robo_appian.components import (
    MenuButton,
    SearchInput,
    Region,
    RecordList,
)
from robo_appian.utils import ComponentUtils

__all__ = [
    "RoboAppianError",
    "RoboAppianNavigationError",
    "assert_not_text",
    "assert_text",
    "assert_visible",
    "wait_visible",
    "AppianRuntime",
    "AppianContext",
    "AutomationContext",
    "automation_context_for",
    "automation_test_case_id",
    "automation_test_log_path",
    "current_automation_context",
    "measure_appian_runtime",
    "resolve_appian_page",
    "AppianPage",
    "AppianButton",
    "AppianCheckbox",
    "AppianInputComponent",
    "AppianRadioSelect",
    "AppianDate",
    "AppianDropdown",
    "AppianTextbox",
    "AppianTab",
    "AppianLink",
    "AppianRow",
    "AppianCell",
    "AppianColumn",
    "AppianLocator",
    "AppianScope",
    "MenuButton",
    "SearchInput",
    "AppianTable",
    "ComponentUtils",
    "Region",
    "RecordList",
]
