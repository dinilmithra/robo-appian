# Using `RoboAppianError`

`RoboAppianError` is the public error type for failures that are specific to Appian automation.

You can import it directly from `robo_appian`:

```python
from robo_appian import RoboAppianError
```

It inherits from `RoboAutomationError`:

```text
RoboAutomationError
└── RoboAppianError
```

That means you can catch only Appian-specific failures when you need to, or catch the broader `RoboAutomationError` when you want to handle any automation-library failure.

## What should I normally do?

For normal pytest tests, **do not catch `RoboAppianError` unless you have a real recovery action**.

Let pytest fail the test so the traceback, logs, screenshot, HTML evidence, and other diagnostics remain available.

```python
def test_create_request(page):
    page.textbox(label="Request Title").fill("Office Supplies")
    page.button(name="Next").click()
```

If an Appian interaction fails, pytest reports the failure automatically.

## When should I catch it?

Catch `RoboAppianError` only when your code can do something useful after an Appian-specific failure.

For example, you may want to add business context, perform a controlled recovery, or convert the error into your application's own public error type.

```python
from robo_appian import RoboAppianError

try:
    page.checkbox(
        label="Is this request for a conference?"
    ).select("Yes")
except RoboAppianError as error:
    print(f"Appian interaction failed: {error}")
    print(f"Code: {error.code}")
    print(f"Details: {error.details}")
    raise
```

Notice the final `raise`. It preserves the original failure after you log or inspect it.

## Information available on the error

Every `RoboAppianError` provides four useful pieces of information:

| Value | What it tells you |
| --- | --- |
| `str(error)` | Human-readable description of what failed |
| `error.code` | Stable code that can be used in logs or conditional handling |
| `error.details` | Structured diagnostic information related to the failure |
| `error.to_dict()` | Dictionary containing the error type, code, message, and details |

Example:

```python
from robo_appian import RoboAppianError

try:
    complete_appian_step()
except RoboAppianError as error:
    print(str(error))
    print(error.code)
    print(error.details)
    print(error.to_dict())
    raise
```

A dictionary returned by `to_dict()` can look like this:

```python
{
    "type": "RoboAppianError",
    "code": "RADIO_OPTION_NOT_FOUND",
    "message": "Could not find the requested Appian radio option.",
    "details": {
        "label": "Is this request for a conference?",
        "value": "Yes",
    },
}
```

The exact `details` keys depend on the operation that failed. Do not assume every error contains the same fields.

## Understanding `code`

The `code` is intended for stable classification. It is safer to check a code than to search for words inside the error message.

Prefer:

```python
if error.code == "RADIO_OPTION_NOT_FOUND":
    ...
```

Avoid:

```python
if "radio" in str(error):
    ...
```

The readable message may improve over time, while a documented code can remain stable.

If no more specific code is supplied, the default code is:

```text
ROBO_APPIAN_ERROR
```

## Understanding `details`

`details` contains extra diagnostic values that help explain the failure.

For example:

```python
{
    "label": "Are you submitting this travel request for yourself or on behalf of someone else?",
    "value": "For myself",
}
```

Useful detail values may include:

- the visible Appian field label;
- the value the test tried to select;
- a component name;
- an expected state;
- an actual state.

Use `details` for diagnostics. Do not build test logic that depends on undocumented detail keys.

## Catching any automation-library error

If you do not need to distinguish Appian failures from generic browser/runtime failures, catch `RoboAutomationError` instead:

```python
from robo_automation import RoboAutomationError

try:
    complete_test_step()
except RoboAutomationError as error:
    print(error.code)
    raise
```

Because `RoboAppianError` inherits from `RoboAutomationError`, this also catches Appian errors.

## Adding your own application context

When a reusable helper fails, you may want to explain what your application was doing while preserving the original error.

```python
from robo_appian import RoboAppianError


def complete_travel_details(page):
    try:
        page.checkbox(
            label="Are you submitting this travel request for yourself or on behalf of someone else?"
        ).select("For myself")
    except RoboAppianError as error:
        raise RuntimeError(
            "Could not complete the Travel personal-details section"
        ) from error
```

The `from error` part is important. It keeps the original `RoboAppianError` visible in the traceback.

If your consumer project has its own public error type, prefer raising that instead of a generic `RuntimeError`.

## Raising `RoboAppianError` in your own reusable Appian helper

If you are building a reusable helper that belongs to an Appian automation library, you can raise `RoboAppianError` directly:

```python
from robo_appian import RoboAppianError


def select_business_option(page, label: str, value: str) -> None:
    try:
        page.checkbox(label=label).select(value)
    except RoboAppianError:
        raise
    except Exception as error:
        raise RoboAppianError(
            "Could not select the Appian option.",
            code="BUSINESS_OPTION_SELECTION_FAILED",
            details={
                "label": label,
                "value": value,
            },
        ) from error
```

Use a short, clear message, a stable uppercase error code, and only useful diagnostic details.

## Good error-handling pattern

```python
from robo_appian import RoboAppianError

try:
    perform_appian_operation()
except RoboAppianError as error:
    logger.error(
        "Appian operation failed. code=%s details=%s",
        error.code,
        error.details,
    )
    raise
```

This gives you extra logging without hiding the actual test failure.

## Patterns to avoid

### Do not silently ignore the error

Avoid:

```python
try:
    perform_appian_operation()
except RoboAppianError:
    pass
```

The test may continue in an invalid state and fail later with a less useful error.

### Do not catch every exception without a reason

Avoid:

```python
try:
    perform_appian_operation()
except Exception:
    ...
```

Use the narrowest error type that matches the recovery you actually support.

### Do not replace the original cause

Avoid:

```python
except RoboAppianError:
    raise RuntimeError("Something failed")
```

Prefer:

```python
except RoboAppianError as error:
    raise RuntimeError("Could not complete the request step") from error
```

## What should I check when I see one?

1. Read the error message at the bottom of the traceback.
2. Check `error.code` if it is shown in the log.
3. Review `error.details` for the field/value/state involved.
4. Open the failure screenshot or HTML evidence.
5. Check whether the visible application state matches the test data.
6. Look at the original chained exception if one is present.
7. Fix the application interaction, selector, data, or expected state rather than suppressing the exception.

## Quick reference

```python
from robo_appian import RoboAppianError

try:
    do_something_with_appian()
except RoboAppianError as error:
    print(str(error))       # readable message
    print(error.code)       # stable classification
    print(error.details)    # diagnostic context
    print(error.to_dict())  # structured representation
    raise                   # preserve the failure
```

For the generated class/API details, see [RoboAppianError API Reference](../api/errors.md).
