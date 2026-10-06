# Pytest Integration

`robo-appian.pytest_plugin` owns the public browser-resource fixtures for consuming pytest projects.

## Enable the plugin

```python
# robo-appian is discovered automatically by pytest via the pytest11 entry point
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

`robo-appian` uses an internal `robo_appian_browser` fixture to wrap the raw browser supplied by `robo-automation`. This avoids fixture-name collisions when both installed plugins expose a backward-compatible `browser` fixture. Consuming tests can continue requesting `browser`, `context`, or `page`, and a consuming project can override them in its own `conftest.py`.

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


## Automatic plugin discovery

Installing `robo-appian` registers `robo_appian.pytest_plugin` through pytest's
`pytest11` entry-point group. Consuming projects therefore do not need a
`pytest_plugins = ("robo_appian.pytest_plugin",)` declaration in `conftest.py`.

Pytest startup is conceptually:

1. pytest discovers installed `pytest11` plugins, including robo-appian.
2. project configuration and `conftest.py` files are loaded.
3. fixtures are resolved for each test.
4. a fixture defined closer to the test overrides a same-named plugin fixture.

### Overriding `page` in a consuming project

A consuming project may replace robo-appian's `page` fixture while continuing to
reuse the plugin-provided `browser` and `context` fixtures:

```python
import pytest
from robo_appian import RoboContext, RoboPage


@pytest.fixture
def page(context: RoboContext) -> RoboPage:
    page = context.new_page()
    page.goto("https://example.test")
    try:
        yield page
    finally:
        page.close()
```

When a test requests `page`, pytest uses this consuming-project fixture instead
of `robo_appian.pytest_plugin.page`. The plugin's `context` fixture still runs
because the override depends on it. A test-module fixture with the same name can
override the conftest fixture again for that module.

If plugin autoloading is globally disabled with
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, explicitly load robo-appian with
`pytest -p robo_appian.pytest_plugin ...`.

### Editable-install entry-point refresh

`pytest11` discovery is stored in installed package metadata. If `pyproject.toml` gains or changes the `pytest11` entry point after an editable environment was already created, refresh the environment with `python tools/setup_venv.py`. The setup script verifies that the installed metadata contains `robo_appian = robo_appian.pytest_plugin`.
