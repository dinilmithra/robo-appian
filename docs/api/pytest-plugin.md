# Pytest Plugin

Load the plugin with:

```python
# robo-appian is discovered automatically by pytest via the pytest11 entry point
```

The plugin owns the Playwright runtime and the public wrapper fixtures:

```text
browser -> RoboBrowser
context -> RoboContext
page    -> RoboPage
```

Consumer projects can override `storage_state`, `robo_appian_context_lifecycle`, and `robo_appian_page_lifecycle` for application-specific authentication and setup without redefining the public resource fixtures.

See [Pytest Integration](../guides/pytest-integration.md) for lifecycle signatures and examples.
