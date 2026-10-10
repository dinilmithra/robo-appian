# Pytest Integration

`robo-automation` and `robo-appian` are discovered automatically through their installed pytest plugins. Consumers normally do not need a `pytest_plugins` declaration or `-p` option.

## Public Appian page fixture

A normal Appian test requests `page` as `AppianPage`:

```python
from robo_appian import AppianPage


def test_example(page: AppianPage) -> None:
    page.goto("https://your-appian-site.example/")
    page.button(name="Submit").is_visible()
```

Generic resource creation and teardown remain owned by `robo-automation`. `robo-appian` wraps the `RoboPage` for Appian interactions without duplicating that lifecycle or hiding browser page operations.

## Application-specific overrides

Applications should override only application policy such as authenticated storage state, URLs, diagnostics, and startup navigation.

### Authenticated storage state

```python
import pytest


@pytest.fixture(scope="session")
def storage_state(browser, worker_id: str):
    return create_worker_authenticated_state(browser, worker_id)
```

Keep authenticated state worker-aware when parallel workers may use different credentials or server sessions.

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

### Application page policy

A consuming application can override `page` while consuming `appian_page`:

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

The application fixture does not close the page; lower-layer lifecycle ownership remains in `robo-automation`.

## Plugin discovery

If an editable environment predates an entry-point change, refresh the editable installs and verify discovery with:

```powershell
pytest --trace-config
pytest --fixtures -q | findstr "appian_page page context browser"
```

Do not explicitly register `robo_appian.pytest_plugin` when the package is installed normally or as an editable dependency.
