# Appian Runtime

The runtime API provides Appian-level browser/session services without exposing lower-level `robo-automation` classes to application projects.

Most normal tests do not need to create these objects directly. They are primarily useful for framework integration, custom fixtures, authentication setup, and advanced diagnostics.

## AppianRuntime

`AppianRuntime` creates Appian contexts/pages, records runtime measurements, and closes resources through the Appian boundary.

::: robo_appian.runtime.AppianRuntime

## AppianContext

`AppianContext` wraps a browser context for Appian consumers.

::: robo_appian.runtime.AppianContext

## AutomationContext

`AutomationContext` exposes stable test correlation values such as testcase, process, attempt, and worker IDs without requiring a consumer to import `robo-automation`.

::: robo_appian.runtime.AutomationContext

## Runtime helpers

::: robo_appian.runtime.current_automation_context

::: robo_appian.runtime.automation_context_for

::: robo_appian.runtime.automation_test_case_id

::: robo_appian.runtime.automation_test_log_path

::: robo_appian.runtime.measure_appian_runtime

::: robo_appian.runtime.resolve_appian_page
