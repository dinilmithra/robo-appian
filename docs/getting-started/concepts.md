# Core Concepts

`robo-appian` is the controller layer between a consuming pytest project and Playwright. Consumer tests work with framework objects (`RoboBrowser`, `RoboContext`, `RoboPage`, and `RoboLocator`) instead of owning raw browser, context, and page resources directly.

## Framework object model

```text
pytest / consumer project
        ↓
RoboBrowser
        ↓ new_context()
RoboContext
        ↓ new_page()
RoboPage
        ↓ element lookup
RoboLocator
        ↓
Playwright implementation
        ↓
Appian
```

The wrappers are framework-level classes under `robo_appian.framework`, and they are exported from the package root:

```python
from robo_appian import RoboBrowser, RoboContext, RoboPage, RoboLocator
```

### `RoboBrowser`

Owns the browser-level boundary. `new_context(...)` returns a `RoboContext`.

### `RoboContext`

Owns a browser context. `new_page()` and `pages` return `RoboPage` objects. It also exposes context timeout, storage-state, event, and close operations needed by the framework lifecycle.

### `RoboPage`

Owns a browser page. It exposes controlled navigation, page operations, and page-level element lookup. Attribute-based lookup methods return `RoboLocator` objects:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    },
    excat_match=True,
)
```

### `RoboLocator`

Wraps a resolved Playwright locator and provides framework operations such as:

```python
user_options.to_be_visible()
user_options.wait_for_attribute(attributes={"aria-expanded": "false"})
user_options.click()
```

It supports arbitrary HTML attributes rather than a fixed attribute whitelist.

## Pytest fixture ownership

When `robo_appian.pytest_plugin` is loaded, robo-appian owns the public fixture chain:

```text
playwright runtime
      ↓
browser -> RoboBrowser
      ↓
context -> RoboContext
      ↓
page -> RoboPage
```

A consuming project can override lifecycle providers for authentication, storage state, diagnostics, or application navigation while leaving resource ownership in robo-appian.

This keeps application-specific behavior separate from browser-control mechanics.

## Application responsibility versus framework responsibility

| Concern | robo-appian | Consumer project |
| --- | :---: | :---: |
| Playwright Python dependency | ✓ | |
| Playwright runtime fixture | ✓ | |
| Browser/context/page fixture ownership | ✓ | |
| Browser/context/page wrappers | ✓ | |
| Browser binary installation CLI | ✓ | |
| Generic Appian component mechanics | ✓ | |
| Generic element lookup / visibility / attribute waits | ✓ | |
| Appian URL | | ✓ |
| Credentials and authentication policy | | ✓ |
| Worker-specific credential mapping | | ✓ |
| Business workflow orchestration | | ✓ |
| Application assertions and test data | | ✓ |
| Application-specific synchronization | | ✓ |

## Component APIs and `Scope`

The reusable component layer (`Button`, `InputText`, `Dropdown`, and others) predates the framework wrappers and still exposes the internal `Scope` type in many generated signatures:

```python
Scope = Page | Locator
```

`Scope` describes the Playwright search boundary used by those component implementations: a page searches the whole document and a locator restricts the operation to a subtree.

For new consumer lifecycle code, prefer `RoboPage` and `RoboLocator`. The raw Playwright `Scope` type remains a component/internal compatibility boundary while the component layer continues to migrate toward the wrapper model. Some `RoboPage` locator helpers also currently return Playwright `Locator` objects for compatibility with existing components; this does not re-expose the raw browser/context/page resources. See [Scope](../api/scope.md).

## Attribute-based lookup

Use `RoboPage.get_by_attributes(...)` when an element is best described directly from its HTML or accessibility attributes:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    },
    excat_match=True,
)
```

The attribute map can include standard attributes, ARIA attributes, `data-*` attributes, and custom attributes.

For a stable HTML id:

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## Exact matching

`excat_match` is intentionally the robo-appian parameter name used by the current public API. For `RoboLocator` attribute lookup:

- `True` or `None` → exact attribute equality
- `False` → substring (`contains`) matching

The Playwright keyword `exact` remains an internal implementation detail at direct Playwright boundaries.

## Visibility and duplicate Appian DOM elements

Appian can render hidden and visible copies of the same control. `RoboLocator.to_be_visible()` filters the current match set by visibility:

- zero visible matches → the visibility assertion waits/fails normally
- one visible match → the locator narrows to that match
- multiple visible matches → the visible set remains; use `first()` only when selecting the first visible match is intentional

```python
user_options.to_be_visible()
user_options = user_options.first()
user_options.click()
```

## Dynamic attribute waits

Wait for one or more attributes without rebuilding the locator:

```python
user_options.wait_for_attribute(
    attributes={
        "aria-expanded": "true",
    }
)
```

`timeout` is optional. When omitted or `None`, Playwright's configured default assertion timeout is used.

## Browser provisioning versus browser execution

Installing `robo-appian` installs the Playwright Python dependency. Browser binaries are installed separately with:

```bash
robo-appian install-browser [firefox|chromium|webkit|all]
```

With no argument, the command installs the full browser set. Browser execution is then controlled by the fixture lifecycle/environment, for example `BROWSER=firefox`.

Next, use [Quick Start](quick-start.md) for the shortest working path or [Pytest Integration](../guides/pytest-integration.md) for lifecycle customization.
