::: robo_appian.framework.robo_locator.RoboLocator
    options:
      show_root_heading: true
      show_source: false
      heading_level: 1
      members_order: source

## Basic interaction

```python
user_options.to_be_visible()
user_options.click()
```

## Wait for dynamic attributes

```python
user_options.wait_for_attribute(
    attributes={
        "aria-expanded": "true",
    },
    timeout=5000,
)
```

The timeout is optional. When omitted or `None`, the configured Playwright assertion timeout is used.

## Multiple visible matches

If `to_be_visible()` retains more than one visible match and using the first is intentional:

```python
user_options.to_be_visible()
user_options = user_options.first()
user_options.click()
```

`first()` returns a new `RoboLocator`; it does not modify the original instance.
