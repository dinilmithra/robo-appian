# Framework Architecture

The framework layer isolates consuming projects from direct browser-resource ownership.

## Object chain

```text
RoboBrowser
    ↓ new_context()
RoboContext
    ↓ new_page()
RoboPage
    ↓ get_by_attributes() / get_by_id()
RoboLocator
```

All four classes live under `robo_appian.framework` and are also exported from `robo_appian`.

## Resource ownership

`RoboBrowser` owns a Playwright browser internally. `RoboContext` owns a Playwright browser context. `RoboPage` owns a Playwright page. `RoboLocator` owns a Playwright locator.

The wrapped Playwright **browser, context, and page** objects are private implementation details. The public wrappers expose explicit operations instead of public `.browser`, `.context`, or `.page` escape hatches.

## `RoboBrowser`

Typical lifecycle:

```python
context = browser.new_context(storage_state=storage_state)
```

`new_context()` returns `RoboContext`.

## `RoboContext`

```python
context.set_default_timeout(90_000)
page = context.new_page()
```

`new_page()` and `pages` return `RoboPage` instances.

## `RoboPage`

Use page-level navigation and element lookup:

```python
page.goto(APP_URL)
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    }
)
```

`get_by_attributes()` and `get_by_id()` return `RoboLocator`.

## `RoboLocator`

```python
user_options.to_be_visible()
user_options.wait_for_attribute(attributes={"aria-expanded": "false"})
user_options.click()
```

`RoboLocator` supports nested/scoped lookup and explicit `first()` selection when multiple visible matches are intentionally acceptable.

## Why wrappers instead of raw Playwright resources?

The wrapper boundary lets consuming projects depend on robo-appian rather than Playwright APIs for browser lifecycle and common element operations. It also gives robo-appian one place to evolve browser behavior, diagnostics, synchronization, and Appian-specific behavior without forcing the same changes through every consumer project.

## Compatibility boundary: `Scope`

Existing component APIs still use `Scope = Playwright Page | Locator` in their generated signatures. This is a compatibility/internal boundary for the component layer, not the preferred resource-ownership model for new consuming projects.

The intended direction is:

```text
consumer lifecycle code -> Robo* wrappers
component internals      -> Scope / Playwright implementation boundary
```

## Current compatibility surface

The browser/context/page ownership migration is complete, but the component layer still has a Playwright-locator compatibility surface:

- `Scope` is still `Playwright Page | Locator` in existing component signatures.
- Some `RoboPage` locator helpers (`locator`, `get_by_role`, `get_by_text`, and related methods) return Playwright `Locator` objects because current components consume them.
- `RoboLocator.locator` currently exposes the wrapped locator for compatibility.

These are locator-level compatibility points, not public raw browser/context/page ownership. New consumer code should prefer `RoboPage.get_by_attributes()`, `RoboPage.get_by_id()`, and `RoboLocator` operations when they cover the use case.
