# Common Framework Features

`robo-appian` is the Appian-facing automation package, but Appian tests also receive a set of common automation capabilities supplied by `robo-automation`. You can use these capabilities through the `robo-appian` public boundary without importing lower-level `robo-automation` classes into application test code.

This guide summarizes the common functionality available to a `robo-appian` consumer and identifies where each responsibility lives.

## Capability map

| Capability | Available to `robo-appian` users | Primary owner |
| --- | --- | --- |
| Browser and context lifecycle | Yes | `robo-automation` |
| Appian-specialized `page` fixture | Yes | `robo-appian` |
| Playwright/expect timeout configuration | Yes | `robo-automation` |
| Pytest plugin and fixtures | Yes | Both packages |
| Worker/test correlation context | Yes | `robo-automation`, exposed by `robo-appian.runtime` |
| Framework logging | Yes | `robo-automation` |
| Performance/action timing | Yes | `robo-automation` |
| Before/after action snapshots | Yes | `robo-automation` |
| Appian semantic components | Yes | `robo-appian` |
| Appian-specific errors | Yes | `robo-appian` |
| Application/test failure snapshots | Application controlled | Consuming application (for example CORE) |

## Browser and context lifecycle

Normal tests should request `page` and let the framework own browser, context, page creation, and teardown:

```python
from robo_appian import AppianPage


def test_example(page: AppianPage) -> None:
    page.goto("https://your-appian-site.example/")
    page.button(name="Submit").is_visible()
```

The generic lifecycle is implemented by `robo-automation`; `robo-appian` specializes the page object so Appian components and semantic locators are available. Application projects should not close framework-owned pages, contexts, or browsers from normal tests.

See [Browser Management](browser-management.md) and [Pytest Integration](pytest-integration.md).

## Configuration and timeouts

Common runtime behavior is configured through the automation environment. Typical settings include:

```text
BROWSER=chromium
HEAD_LESS=N
WAIT_TIME=60
```

`WAIT_TIME` is expressed in seconds at the application/configuration boundary. The framework applies it to Playwright and expect operations as required.

Applications may override configuration policy in their own fixtures or environment files. Keep application URLs, credentials, authentication policy, and test-data paths in the consuming application rather than in `robo-appian`.

## Pytest fixtures

When installed normally or as an editable dependency, the pytest plugins are discovered through package entry points. A consumer normally does not need `pytest_plugins` or a manual `-p` option.

The important Appian-facing fixture is:

```python
page: AppianPage
```

Lower-level browser/context resources remain framework-managed. Applications can override application policy while consuming the provided Appian page fixture.

See [Pytest Integration](pytest-integration.md).

## Correlation and worker context

Parallel execution needs stable identifiers for logs, evidence, performance records, and authentication/session policy. `robo-appian.runtime` exposes the common correlation context without requiring application code to import `robo-automation` directly:

```python
from robo_appian.runtime import current_automation_context

context = current_automation_context()
```

The context can identify values such as the testcase, process/attempt, and pytest-xdist worker. This keeps artifacts from concurrent workers separable and supports future per-worker credential isolation.

See [Runtime API](../api/runtime.md).

## Logging

Framework/browser operations can participate in the common automation logging pipeline. Application projects can configure their own pytest log levels, formats, and artifact locations while the lower layer provides consistent action/runtime context.

Do not log passwords, tokens, authenticated storage-state contents, or other secrets. When a component action contains sensitive input, diagnostics should record the action and target while redacting the sensitive value.

## Performance telemetry

The common automation layer can measure framework lifecycle and Playwright action durations. `robo-appian` component operations benefit from that instrumentation because their browser interactions ultimately execute through the shared automation layer.

An Appian semantic operation can involve more than one low-level action. For example, filling an Appian date can include the input update and the required focus-out/blur operation. Performance records therefore describe the underlying browser actions as well as the higher-level test flow.

## Action snapshots

When action snapshots are enabled, supported browser actions can capture a `before` and `after` evidence pair:

```text
CAPTURE_ACTION_SNAPSHOTS=Y
```

The normal lifecycle is always:

```text
before -> action -> after
```

If the action fails, the `after` metadata records `status=failed` and error details. There is no separate `after_error` phase.

Appian component operations automatically benefit from this common instrumentation; application tests do not need to add screenshot calls around every component action.

See [Action Snapshots](action-snapshots.md) for artifact layout, metadata, supported behavior, and performance considerations.

## Failure snapshots are separate

Action snapshots and test-level failure evidence solve different problems. `CAPTURE_ACTION_SNAPSHOTS` belongs to the common action instrumentation. A consuming application may separately provide a failure-evidence flag, such as CORE's:

```text
CAPTURE_FAILURE_SNAPSHOTS=Y
```

That application flag is not a `robo-appian` configuration option. It controls the application's pytest failure evidence even when per-action snapshots are disabled.

## Error handling

`robo-appian` exposes `RoboAppianError` for Appian-specific failures while preserving the common automation error boundary underneath it. Application projects can derive their own errors for application policy without coupling tests to low-level implementation classes.

```python
from robo_appian import RoboAppianError

try:
    page.checkbox(label="Acknowledgement").check()
except RoboAppianError as exc:
    print(exc)
```

See [Handling Errors](../getting-started/error-handling.md) and [Errors API](../api/errors.md).

## Parallel execution and isolation

The shared lifecycle is compatible with pytest-xdist. Browser contexts, correlation data, logs, snapshots, and application authentication state should remain worker-aware.

A consuming application can assign different credentials or storage state to each worker. Do not introduce shared browser-context/session reuse that would force multiple workers to use one authenticated identity.

## Appian-specific functionality remains in `robo-appian`

Common framework services should not replace Appian semantics. Continue to use the Appian component API for application interactions:

```python
page.textbox(label="Request Title").fill("CORE Test")
page.checkbox(label="IT").check()
page.radio(label="Conference Type").select("Scientific")
page.date(label="From").fill("12/12/2026")
```

This separation keeps application code readable: `robo-automation` owns reusable automation infrastructure, while `robo-appian` owns Appian-specific component discovery, state, rerender handling, and interaction semantics.
