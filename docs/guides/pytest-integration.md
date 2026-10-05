# Pytest Integration

`robo-appian.pytest_plugin` owns the public browser-resource fixtures for consuming pytest projects.

## Enable the plugin

```python
pytest_plugins = ("robo_appian.pytest_plugin",)
```

## Public fixtures

| Fixture | Scope | Value |
| --- | --- | --- |
| `playwright` | session | Internal Playwright runtime owned by robo-appian |
| `browser` | session | `RoboBrowser` |
| `storage_state` | session | `None` by default; consumers can override |
| `context` | test | `RoboContext` |
| `page` | test | `RoboPage` |
| `robo_appian_context_lifecycle` | test | Context lifecycle provider |
| `robo_appian_page_lifecycle` | test | Page lifecycle provider |

The runtime fixture is intentionally owned by robo-appian, so `pytest-playwright` is not required merely to obtain a Playwright runtime or page fixture.

## Basic test

```python
from robo_appian import RoboPage


def test_example(page: RoboPage) -> None:
    page.goto("https://your-appian-site.example/")
    agree = page.get_by_id("jsAcceptButton")
    agree.to_be_visible()
    agree.click()
```

## Override authenticated storage state

The default `storage_state` fixture returns `None`. An application can replace it with authenticated state while preserving the robo-appian context/page fixtures:

```python
import pytest
from robo_appian import RoboBrowser


@pytest.fixture(scope="session")
def storage_state(browser: RoboBrowser, worker_id: str):
    return create_worker_authenticated_state(browser, worker_id)
```

For xdist, keep this worker-aware if workers may use separate credentials or sessions.

## Override the context lifecycle

Return a lifecycle function rather than redefining the public `context` fixture:

```python
import pytest


@pytest.fixture
def robo_appian_context_lifecycle():
    return my_context_lifecycle
```

The lifecycle signature is conceptually:

```python
def my_context_lifecycle(browser, storage_state, performance_monitor):
    context = browser.new_context(storage_state=storage_state)
    try:
        yield context
    finally:
        context.close()
```

Use this hook for application-specific context options, authenticated state, diagnostics, default timeouts, or context event registration.

## Override the page lifecycle

```python
import pytest


@pytest.fixture
def robo_appian_page_lifecycle():
    return my_page_lifecycle
```

A lifecycle can navigate/authenticate before yielding the `RoboPage`:

```python
def my_page_lifecycle(context, performance_monitor):
    page = context.new_page()
    try:
        page.goto(APP_URL)
        ensure_application_login(page)
        yield page
    finally:
        page.close()
```

## Ownership rule

Do not redefine `browser`, `context`, or `page` in the consuming project unless you intentionally opt out of the robo-appian fixture stack. Prefer the lifecycle-provider hooks so the framework retains resource ownership and teardown behavior.

## xdist and session isolation

`browser` is session/worker scoped under pytest-xdist. `context` and `page` are test scoped. Authentication state can remain worker-specific by overriding `storage_state` with worker-aware logic.

This design allows each worker to maintain an independent server session and supports future per-worker credential assignment without collapsing all workers into one shared authenticated context.

## Plugin dependency boundary

A consuming project that uses this fixture stack normally needs only `robo-appian` as its browser-control dependency. Playwright remains a dependency of robo-appian and is not required as a direct dependency of the consumer package.
