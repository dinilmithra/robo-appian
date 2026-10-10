# Assertion Helpers

`robo-appian` provides Appian-facing assertion helpers so application projects can use a stable Appian error boundary instead of depending directly on browser-runtime assertion types.

```python
from robo_appian import assert_text, assert_visible, wait_visible
```

## Wait for visibility

```python
wait_visible(page.get_by_text("Item saved"))
```

## Assert visibility

```python
assert_visible(page.get_by_text("Item saved"))
```

## Assert text

```python
assert_text(status, "Approved")
```

## Assert text does not match

```python
from robo_appian import assert_not_text

assert_not_text(status, "Draft")
```

When these checks fail, they raise `RoboAppianError` with an Appian-specific error code and useful details.

## API

::: robo_appian.assertions.wait_visible

::: robo_appian.assertions.assert_visible

::: robo_appian.assertions.assert_text

::: robo_appian.assertions.assert_not_text
