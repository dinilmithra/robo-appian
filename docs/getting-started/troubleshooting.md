# Troubleshooting

## Import fails with `ModuleNotFoundError`

Confirm robo-appian is installed in the Python environment that runs pytest:

```bash
python -c "import robo_appian; print(robo_appian.__file__)"
```

With Poetry:

```bash
poetry run python -c "import robo_appian; print(robo_appian.__file__)"
```

## Playwright says the browser executable is missing

The Playwright Python package is installed as a robo-appian dependency, but browser binaries are provisioned explicitly.

Install the full browser set:

```bash
robo-appian install-browser
```

or:

```bash
robo-appian install-browser all
```

Install one engine:

```bash
robo-appian install-browser firefox
robo-appian install-browser chromium
robo-appian install-browser webkit
```

The command uses the current Python interpreter, so run it in the same environment as your tests.

## The wrong browser starts

The generic lifecycle reads `BROWSER`, defaulting to `chromium`.

For Firefox:

```text
BROWSER=firefox
```

Make sure the matching browser binary is installed:

```bash
robo-appian install-browser firefox
```

## The `page` fixture is missing

Make sure the plugin is loaded in the root `conftest.py`:

```python
# robo-automation is discovered automatically by pytest via the pytest11 entry point
```

The `robo-automation` plugin provides `browser`, `context`, and `page`; `context` and `page` use the generic Robo* wrappers.

## I need application login before every test

If an application needs login or navigation before a test starts, override the generic `page` fixture in the consuming project and keep that application logic out of robo-appian. See [Pytest Integration](../guides/pytest-integration.md).

## I need authenticated storage state

Override the session-scoped `storage_state` fixture. For xdist, keep the state worker-aware if workers may use different credentials or independent server sessions.

## An element resolves to hidden and visible duplicates

Appian may render hidden and visible copies of the same control. `AppianLocator.to_be_visible()` filters the current match set to visible elements.

```python
user_options.to_be_visible()
```

If more than one visible match remains and selecting the first is intentional:

```python
user_options = user_options.first()
user_options.click()
```

## Wait for an attribute transition

Use `wait_for_attribute()` with an attribute map:

```python
user_options.wait_for_attribute(
    attributes={
        "aria-expanded": "true",
    },
    timeout=5000,
)
```

`timeout` is optional. When omitted or `None`, the configured default assertion timeout is used.

## A component cannot find a control

Check:

1. the application reached the expected state;
2. the user-facing label/text actually matches the rendered Appian control;
3. whether exact versus partial matching is correct;
4. whether a repeated control should be narrowed to a smaller scope;
5. whether the correct component type is being used;
6. whether generic `AppianPage.get_by_attributes()` is a better fit for the element.

Avoid arbitrary sleeps; synchronize on a meaningful UI state.

## `Scope` mentions Playwright even though my test uses `AppianPage`

Some older non-button components still expose the lower-layer generic `Scope` compatibility annotation. New Appian-facing code should use `AppianPage`, `AppianLocator`, or `AppianScope`; generated API pages reflect the actual signature of each component.

## Should CORE or another consumer declare Playwright directly?

Not for the standard fixture stack. `robo-automation` owns the generic Playwright lifecycle, and `robo-appian` currently also declares Playwright directly for its Appian implementation/tooling. A consumer should add a direct Playwright dependency only when it intentionally owns direct Playwright code.

## I need exact behavior for a method

Use the [API Reference](../api/index.md). Generated component pages are sourced from the current Python signatures and docstrings.

### Editable-install entry-point refresh

`pytest11` discovery is stored in installed package metadata. Appian consumers use both `robo_automation = robo_automation.pytest_plugin` and `robo_appian = robo_appian.pytest_plugin`. If an editable environment is stale, reinstall/refresh both sibling checkouts (CORE local development uses `tools/install_local_libraries.py`) and confirm discovery with `pytest --trace-config`.
