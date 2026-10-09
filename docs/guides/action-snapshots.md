# Action Snapshots

`robo-appian` supports action snapshots through its dependency on **robo-automation**. No duplicate Appian-specific snapshot engine is required.

`robo-appian` components resolve Appian controls semantically and then perform Playwright `Page` or `Locator` actions. When `CAPTURE_ACTION_SNAPSHOTS=Y`, the generic `robo-automation` action monitor captures those underlying actions automatically.

```text
consumer test / CORE flow
        ↓
robo-appian
AppianPage / Appian components
        ↓
robo-automation action monitor
        ↓
Playwright Page / Locator action
        ↓
before + after evidence
```

## Enable the feature

Set the flag in the consuming project's environment configuration:

```env
CAPTURE_ACTION_SNAPSHOTS=Y
SNAPSHOT_PATH=${EVIDENCE_PATH}/actions
```

Optional controls are inherited from `robo-automation`:

```env
ACTION_SNAPSHOT_HTML=Y
ACTION_SNAPSHOT_FULL_PAGE=N
```

The feature is disabled with:

```env
CAPTURE_ACTION_SNAPSHOTS=N
```

## What is captured for Appian components

Appian component methods are captured when they invoke supported Playwright actions. Examples include:

```python
page.textbox(label="Conference Name").fill("Testing")
page.checkbox(label="Added to Concur Government Edition (CGE)").check()
page.radio(label="Conference Type").select("Scientific")
page.button(name="SAVE").click()
```

The underlying operations such as `fill`, `check`, `click`, `focus`, or `blur` receive paired action evidence.

An Appian method can legitimately produce more than one action pair. For example, a date component may fill the text input and then explicitly call `blur()` so Appian validates and rerenders the field. Those are separate browser actions and therefore have separate snapshot pairs.

## Two phases only

Every captured browser action has exactly:

```text
before
after
```

There is no `after_error` artifact. When the browser action fails, the `after` metadata records:

```json
{
  "phase": "after",
  "status": "failed",
  "error_type": "TimeoutError",
  "error": "..."
}
```

When the action succeeds, the same `after` phase records `status: "passed"` and the action duration.

## Appian rerendering

Action snapshots are especially useful for Appian because many interactions can rerender part of the page. The pair shows the DOM and visual state immediately before and after the underlying action.

The snapshot monitor does **not** change Appian rerender handling. Component logic remains responsible for resolving the current control, verifying state where required, and reacquiring elements after rerendering. Snapshot capture is observational only.

## Checkbox and radio examples

For a checkbox:

```python
checkbox = page.checkbox(label="Added to Concur Government Edition (CGE)")
checkbox.check()
assert checkbox.is_checked()
```

The `check()` interaction is captured. `is_checked()` is a state query rather than a mutating Playwright action, so it does not create an action pair by itself.

For a radio group:

```python
conference_type = page.radio(label="Conference Type")
conference_type.select("Scientific")
assert conference_type.is_selected("Scientific")
```

The mutating selection action is captured. `is_selected(value)` remains a state query.

## Action snapshots versus failure snapshots

In CORE, these are separate controls:

```env
# Before and after supported browser actions.
CAPTURE_ACTION_SNAPSHOTS=Y

# Test-level failure evidence.
CAPTURE_FAILURE_SNAPSHOTS=Y
```

`CAPTURE_ACTION_SNAPSHOTS` comes from the reusable `robo-automation` layer and automatically covers `robo-appian` actions.

`CAPTURE_FAILURE_SNAPSHOTS` belongs to CORE's test/reporting lifecycle. It captures failure-level evidence even when action snapshots are disabled.

Recommended diagnostic configuration:

```env
CAPTURE_ACTION_SNAPSHOTS=Y
CAPTURE_FAILURE_SNAPSHOTS=Y
```

Recommended routine execution when step-by-step artifacts are unnecessary:

```env
CAPTURE_ACTION_SNAPSHOTS=N
CAPTURE_FAILURE_SNAPSHOTS=Y
```

## Artifact correlation

Action evidence is partitioned by pytest-xdist worker and current correlation/process ID. The metadata includes the browser action, phase, status, target description, current URL, duration for the `after` phase, and exception information on failure.

This allows an Appian failure to be traced from a CORE testcase to the Appian component call and then to the exact underlying browser action without adding snapshot code to individual page objects or flows.
