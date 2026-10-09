# Errors

`RoboAppianError` is the public exception boundary for Appian-specific automation failures.

If you are new to the library, start with the practical guide:

[How to use `RoboAppianError`](../getting-started/error-handling.md)

The guide explains:

- when to let pytest handle the error;
- when to catch it;
- how to use `code`, `details`, and `to_dict()`;
- how to preserve the original cause;
- how to raise a well-formed Appian error from reusable helpers.

## RoboAppianError

::: robo_appian.errors.RoboAppianError

## RoboAppianNavigationError

`RoboAppianNavigationError` is the specialized Appian error used when a lower-level browser navigation failure is translated through the Appian boundary.

Application code can catch it specifically when navigation requires special recovery, or simply catch `RoboAppianError` to handle all Appian failures together.

```python
from robo_appian import RoboAppianError, RoboAppianNavigationError

try:
    run_navigation()
except RoboAppianNavigationError as error:
    print(error.code)
except RoboAppianError:
    raise
```

::: robo_appian.errors.RoboAppianNavigationError
