::: robo_appian.framework.robo_browser.RoboBrowser
    options:
      show_root_heading: true
      heading_level: 1
      members_order: source

## Typical use

`RoboBrowser` is normally supplied by the robo-appian pytest plugin. Create a context through the wrapper rather than handling a raw Playwright browser in the consumer project:

```python
context = browser.new_context(storage_state=storage_state)
```

`new_context()` returns [`RoboContext`](robo-context.md).
