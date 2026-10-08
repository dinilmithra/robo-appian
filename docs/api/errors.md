# Errors

`RoboAppianError` is the public exception for Appian-specific automation failures.

If you are new to the library, start with the practical guide:

[How to use `RoboAppianError`](../getting-started/error-handling.md)

The guide explains:

- when to let pytest handle the error;
- when to catch it;
- how to use `code`, `details`, and `to_dict()`;
- how to preserve the original cause;
- how to raise a well-formed Appian error from reusable helpers.

## API

::: robo_appian.errors.RoboAppianError
