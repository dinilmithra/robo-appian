::: robo_appian.framework.robo_context.RoboContext
    options:
      show_root_heading: true
      heading_level: 1
      members_order: source

## Typical use

```python
context.set_default_timeout(90_000)
context.set_default_navigation_timeout(90_000)
page = context.new_page()
```

`new_page()` and `pages` return [`RoboPage`](robo-page.md) objects.
