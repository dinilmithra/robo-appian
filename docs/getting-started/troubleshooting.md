# Troubleshooting

## Import fails with `ModuleNotFoundError`

Confirm the package is installed in the same Python environment that runs the tests:

```bash
python -c "import robo_appian; print(robo_appian.__file__)"
```

With Poetry:

```bash
poetry run python -c "import robo_appian; print(robo_appian.__file__)"
```

## Playwright says the browser executable is missing

Installing the Python package and installing a browser are separate steps. Install Chromium in the environment that runs the tests:

```bash
playwright install chromium
```

With Poetry:

```bash
poetry run playwright install chromium
```

## A control cannot be found

Check these in order:

1. Confirm the current scope has reached the expected application state.
2. Confirm the label/text matches what the Appian UI exposes.
3. Remember that `excat_match` defaults to `False`; use `True` only when exact matching is required.
4. If the same label appears more than once, scope the operation to a meaningful container when the API accepts `Scope`.
5. Confirm you selected the correct component—for example, `Dropdown` versus `SearchDropdown`.
6. Check the component API for a specialized method that matches the rendered Appian structure.

Avoid fixing locator problems with arbitrary sleeps. Synchronize on a meaningful UI state instead.

## Exact matching behaves differently than expected

`excat_match` is optional and defaults to `False`. Use `excat_match=True` when a complete label match is required to disambiguate similar controls.

## The same label exists twice

When the method accepts a `Scope`, narrow the current scope to the correct container:

```python
scope = scope.get_by_role("region", name="Billing Address")
InputText.fill_by_label(scope, "City", "Rockville")
```

## Should I add a sleep?

Usually no. Prefer a component wait or a Playwright assertion tied to the state the workflow actually requires. Application-specific synchronization belongs in your consumer project; generic Appian component synchronization belongs in `robo-appian`.

## I need a selector that robo-appian does not provide

Using Playwright directly is valid. `robo-appian` is a focused component library, not a requirement that every browser interaction go through the package. Keep one-off and application-specific selectors in the consumer project.

## I need exact behavior for a method

Open that component's [API Reference](../api/index.md). API pages are generated from the public source signatures and docstrings and show parameter types, defaults, descriptions, and return information without exposing implementation source bodies.
