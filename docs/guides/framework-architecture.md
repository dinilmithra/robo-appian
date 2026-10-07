# Framework Architecture

The framework layer isolates consuming projects from direct browser-resource ownership.

## Object chain

```text
Playwright Browser
    ↓ new_context()
RoboBrowserContext
    ↓ new_page()
RoboPage
    ↓ get_by_attributes() / get_by_id()
RoboLocator
```

The generic wrapper classes live under `robo_automation.framework` and are exported from `robo_automation`. `robo-appian` builds Appian-specific components on top of them.

## Resource ownership

Playwright `Browser` is used directly at the top of the generic resource chain. `RoboBrowserContext` wraps a Playwright browser context, `RoboPage` wraps a Playwright page, and `RoboLocator` wraps a Playwright locator.

The wrapped Playwright **browser, context, and page** objects are private implementation details. The public wrappers expose explicit operations instead of public `.browser`, `.context`, or `.page` escape hatches.

## Playwright `Browser`

Typical lifecycle:

```python
context = browser.new_context(storage_state=storage_state)
```

`Browser.new_context()` itself returns a Playwright `BrowserContext`; the `robo-automation` context fixture wraps that value as `RoboBrowserContext`.

## `RoboBrowserContext`

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

The generic wrapper boundary in `robo-automation` centralizes browser lifecycle and common element operations. `robo-appian` then adds Appian-specific components on top without owning the generic resource lifecycle. Consuming applications keep their own authentication, navigation, diagnostics policy, and business workflows.

## Appian abstraction boundary

The preferred consumer chain is:

```text
AppianBrowserContext
    ↓
AppianPage
    ↓
AppianLocator / Appian components
```

These types specialize the generic `RoboBrowserContext`, `RoboPage`, and `RoboLocator` implementation owned by `robo-automation`. Consumer projects such as CORE should depend on the Appian types rather than importing the generic Robo* resource types directly.

`AppianScope = AppianPage | AppianLocator` is available when reusable Appian code genuinely supports either a whole page or a scoped subtree. Prefer the concrete `AppianPage` annotation when locator scoping is not needed.

### Legacy component signatures

Some older non-button component modules still use the lower-layer generic `Scope` annotation. Those signatures are retained for compatibility and are visible in their generated API pages. New Appian abstractions should use Appian-layer types instead.

`AppianButton` follows the new model completely: it lives under `robo_appian.appian`, is created with `page.button(name="...")`, and does not reuse the removed legacy `components.Button` implementation.
