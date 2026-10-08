# Handling Errors

`robo-appian` exposes an Appian-specific public exception:

```python
from robo_appian import RoboAppianError
```

`RoboAppianError` is a subclass of `RoboAutomationError`.

```text
RoboAutomationError
└── RoboAppianError
```

This lets your code choose how broadly it wants to handle a failure.

## Normal test code

For most tests, do **not** catch the exception. Let pytest report it so you keep the complete traceback, logs, screenshot, and failure evidence.

```python
def test_request(page):
    page.textbox(label="Request Title").fill("Office Supplies")
    page.button(name="Next").click()
```

If the Appian interaction fails, pytest should normally fail the test.

## Catch only Appian failures

Use this when your application has a real Appian-specific recovery path:

```python
from robo_appian import RoboAppianError

try:
    complete_appian_step()
except RoboAppianError as error:
    print(error)
    print(error.code)
    print(error.details)
```

## Catch any automation-library failure

If you do not care whether the failure came from generic browser automation or Appian semantics:

```python
from robo_automation import RoboAutomationError

try:
    complete_test_step()
except RoboAutomationError as error:
    print(error)
```

Because `RoboAppianError` inherits from `RoboAutomationError`, this also catches Appian errors.

## Information available on an error

Every public library error provides:

| Property | Meaning |
| --- | --- |
| `str(error)` | Short readable explanation |
| `error.code` | Stable error code for logs or conditional handling |
| `error.details` | Extra diagnostic values such as component label or requested value |
| `error.to_dict()` | Dictionary containing type, code, message, and details |

Example diagnostic information might look like:

```python
{
    "label": "Is this request for a conference?",
    "value": "Yes",
}
```

The contents of `details` depend on the operation that failed. Do not assume every error contains the same keys.

## Adding business context

Application code can add context without hiding the original failure:

```python
from robo_appian import RoboAppianError

try:
    select_request_type()
except RoboAppianError as exc:
    raise RuntimeError(
        "Could not complete the Request Type section"
    ) from exc
```

The original `RoboAppianError` remains visible in the traceback.

## What should a new developer do when one occurs?

1. Read the short error message.
2. Look at the screenshot and HTML report if the test produced them.
3. Check `error.code` and `error.details` in the log when available.
4. Read the original cause at the bottom of the traceback.
5. Fix the test, data, or application problem rather than catching and ignoring the exception.
