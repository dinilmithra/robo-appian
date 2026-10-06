# Core Concepts

`robo-appian` is the Appian-specific component layer. It builds on the generic browser automation layer provided by `robo-automation`.

## Layering

```text
consumer application / tests
        ↓
robo-appian
Appian components and interaction utilities
        ↓
robo-automation
Browser -> RoboBrowserContext -> RoboPage -> RoboLocator
        ↓
Playwright
        ↓
Appian
```

The generic wrapper classes are exported by `robo_automation`:

```python
from playwright.sync_api import Browser
from robo_automation import RoboBrowserContext, RoboPage, RoboLocator
```

`robo-appian` consumes these generic types; it does not own or export them.

## Generic wrapper model

### Playwright `Browser`

The public `browser` fixture is a Playwright `Browser` supplied by the `robo-automation` pytest plugin.

### `RoboBrowserContext`

Wraps a Playwright browser context. `new_page()` and `pages` return `RoboPage` objects and the wrapper exposes the context lifecycle operations needed by the generic pytest layer.

### `RoboPage`

Wraps a Playwright page and provides framework-level navigation and lookup helpers. Attribute-based lookup methods return `RoboLocator` objects.

### `RoboLocator`

Wraps a resolved Playwright locator and provides operations such as visibility filtering, attribute waits, click, nested lookup, and `first()`.

## Pytest fixture ownership

All generic fixtures are supplied by `robo-automation`:

```text
robo-automation: Playwright runtime
      ↓
robo-automation: browser -> Playwright Browser
      ↓
robo-automation: context -> RoboBrowserContext
      ↓
robo-automation: page -> RoboPage
```

A consuming project can override generic context inputs (`storage_state`, `context_options`, `wait_time`, `context_page_handler`) and can override `page` for application navigation/login. Application-specific behavior remains in the consuming project.

## Responsibility matrix

| Concern | robo-automation | robo-appian | Consumer project |
| --- | :---: | :---: | :---: |
| Playwright runtime/browser lifecycle | ✓ | | |
| `RoboBrowserContext` / `RoboPage` / `RoboLocator` | ✓ | | |
| Generic pytest fixtures | ✓ | | |
| Generic element lookup / visibility / attribute waits | ✓ | | |
| Appian component mechanics | | ✓ | |
| Browser-binary installation CLI | | ✓ | |
| Appian URL | | | ✓ |
| Credentials and authentication policy | | | ✓ |
| Worker-specific credential mapping | | | ✓ |
| Business workflow orchestration | | | ✓ |
| Application assertions and test data | | | ✓ |
| Application-specific diagnostics policy | | | ✓ |

## Component APIs and `Scope`

The reusable Appian component layer still exposes `Scope` in many signatures:

```python
Scope = Page | Locator
```

`Scope` is owned by `robo-automation` and describes the Playwright search boundary used by component implementations: a page searches the whole document and a locator restricts the operation to a subtree.

For new consumer lifecycle code, prefer `RoboPage` and `RoboLocator`. See [Scope](../api/scope.md).

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

For a stable HTML id:

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## Browser provisioning versus execution

`robo-appian` provides the browser-install CLI:

```bash
robo-appian install-browser [firefox|chromium|webkit|all]
```

The generic browser execution lifecycle is owned by `robo-automation` and selects the runtime browser from automation configuration such as `BROWSER=firefox`.

Next, use [Quick Start](quick-start.md) for the shortest working path or [Pytest Integration](../guides/pytest-integration.md) for lifecycle customization.
