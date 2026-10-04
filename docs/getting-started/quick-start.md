# Quick Start

This guide is the shortest path from an installed package to useful Appian interactions. If `scope` is unfamiliar, read [Core Concepts](concepts.md) first.

## 1. Import from the package root

Prefer the public package-level API:

```python
from robo_appian import Button, Dropdown, InputText, Text
```

You normally call component operations directly; you do not instantiate these helper classes.

## 2. Pass a Playwright `Page` or `Locator` as `scope`

`scope` is the search boundary for every scope-aware robo-appian operation. It is **either a Playwright `Page` or a Playwright `Locator`**:

- Pass a `Page` to search the entire current document.
- Pass a `Locator` to search only inside that locator, such as a form, region, dialog, or row.

Your test project creates and owns these Playwright objects. `robo-appian` does not create a separate scope object. For example, a function can receive a Playwright `Page` and pass it directly as `scope`:

```python
from robo_appian import Button, Dropdown, InputText, Text


def create_request(scope):
    InputText.fill_by_label(scope, "Request Name", "Example Request")
    Dropdown.select(scope, "Request Type", "Travel")
    Button.click(scope, "Submit")
    Text.wait_visible(scope, "Created successfully")
```

The workflow (`create_request`) belongs to the consumer project. The reusable Appian control mechanics belong to `robo-appian`.

## 3. Think in component + user-facing identifier

For label-oriented APIs, the call usually reads like the UI:

```python
InputText.fill_by_label(scope, "Request Name", "Example Request")
Button.click(scope, "Submit")
```

`robo-appian` handles reusable component lookup and interaction behavior; your test does not need to repeat that locator implementation.

## 4. Scope repeated controls when needed

When the same label appears more than once, narrow the search by passing a Playwright `Locator` instead of the whole `Page`:

```python
scope = scope.get_by_role("region", name="Request Details")
InputText.fill_by_label(scope, "Name", "Example Request")
```

The container is application-specific, so the consumer project chooses it. The component interaction remains reusable.

## 5. Use the API reference for exact behavior

`excat_match` is optional and defaults to `False`. Pass `excat_match=True` only when the complete label or text must match exactly. The [API Reference](../api/index.md) shows the authoritative signature, parameter descriptions, and return information.

!!! tip "Want the full test shape?"
    Continue to [Your First Test](first-test.md) for browser setup, navigation, component usage, assertions, scoping, and recommended project boundaries.
