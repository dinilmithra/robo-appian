# Pytest Integration

`robo-automation` and `robo-appian` are layered pytest plugins. Each is registered through the package's `pytest11` entry point, so normal consumers do not need a `pytest_plugins` declaration or `-p` option.

## Fixture layers

The generic layer owns resource lifecycle; the Appian layer specializes the generic page without recreating that lifecycle.

| Package | Fixture | Scope | Purpose |
| --- | --- | --- | --- |
| `robo-automation` | `browser` | session | raw Playwright `Browser` |
| `robo-automation` | `storage_state` | session | neutral `None` default; consumers may override |
| `robo-automation` | `context_options` | test | options for `Browser.new_context()` |
| `robo-automation` | `wait_time` | session | timeout in seconds; default `90` |
| `robo-automation` | `context_page_handler` | test | optional new-page callback |
| `robo-automation` | `context` | test | configured `RoboBrowserContext` |
| `robo-automation` | `robo_page` | test | owns creation/close of a generic `RoboPage` |
| `robo-automation` | `page` | test | generic public alias for `robo_page` |
| `robo-appian` | `appian_page` | test | specializes the same `robo_page` as `AppianPage` |
| `robo-appian` | `page` | test | public Appian page fixture |

`AppianPage` derives from `RoboPage` and selects `AppianLocator` for wrapped locator APIs. The specialization reuses the same underlying Playwright page; it does not create a second browser page and does not own teardown.

## Appian test

```python
from robo_appian import AppianPage


def test_example(page: AppianPage) -> None:
    page.goto("https://your-appian-site.example/")
    page.get_by_id("jsAcceptButton").click()
```

## Application-specific overrides

Applications should override only their policy layer. Authentication state, URLs, credentials, diagnostics policy, and workflow startup do not belong in `robo-appian`.

### Authenticated storage state

```python
import pytest
from playwright.sync_api import Browser


@pytest.fixture(scope="session")
def storage_state(browser: Browser, worker_id: str):
    return create_worker_authenticated_state(browser, worker_id)
```

Keep authenticated state worker-aware when xdist workers may use different credentials or server sessions.

### Context options

```python
import pytest


@pytest.fixture
def context_options(storage_state):
    return {
        "storage_state": storage_state,
        "ignore_https_errors": True,
    }
```

### Timeout in seconds

```python
import pytest


@pytest.fixture(scope="session")
def wait_time() -> int:
    return get_application_timeout_seconds()
```

`robo-automation` performs the seconds-to-milliseconds conversion only at the Playwright timeout boundary.

### Application page policy

A higher-level application can override `page` while consuming `appian_page`. This is the preferred plug-and-play pattern:

```python
from collections.abc import Iterator

import pytest
from robo_appian import AppianPage


@pytest.fixture
def page(appian_page: AppianPage) -> Iterator[AppianPage]:
    appian_page.goto(APP_URL)
    ensure_application_login(appian_page)
    yield appian_page
```

The application fixture does **not** close the page. `robo-automation` owns the lower `robo_page` lifecycle and closes the underlying Playwright page after all higher-layer fixtures finish.

## Execution order

For a CORE-style consumer, the effective chain is:

```text
robo-automation browser
        ↓
robo-automation context
        ↓
robo-automation robo_page (owns create/close)
        ↓
robo-appian appian_page (specializes wrapper)
        ↓
CORE page (navigation/login policy)
        ↓
test
```

Teardown runs in reverse order. CORE finishes its page policy first, then `robo-automation` closes the underlying page and context.

## Plugin discovery

Both packages register pytest plugins in package metadata:

```text
robo_automation = robo_automation.pytest_plugin
robo_appian = robo_appian.pytest_plugin
```

If an editable environment predates an entry-point change, refresh both editable installs and verify discovery with:

```powershell
pytest --trace-config
pytest --fixtures -q | findstr "robo_page appian_page page context browser"
```

If `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is set, installed `pytest11` plugins are not auto-loaded.

## Plugin registration in application consumers

Do not add `pytest_plugins = ("robo_appian.pytest_plugin",)` when `robo-appian` is installed normally or as an editable dependency. Pytest auto-loads the plugin through the package's `pytest11` entry point. Explicitly registering the same module after entry-point discovery causes a duplicate-plugin error.

After changing entry-point metadata in a local checkout, refresh the editable installation and verify registration with `pytest --trace-config`.
