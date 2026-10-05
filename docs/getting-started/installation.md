# Installation

Install `robo-appian` into the Python environment that runs your tests. The package owns the Playwright Python dependency and can also provision Playwright-managed browser binaries through its platform-independent CLI.

## Requirements

- Python **3.12** (`>=3.12,<3.13`)
- pytest
- one or more Playwright-supported browser engines installed for the environment that executes the tests

`playwright`, `pytest`, and `robo-automation` are direct `robo-appian` dependencies. A consuming project does not need to declare `playwright` or `pytest-playwright` merely to use the robo-appian fixture stack.

## Install with pip

```bash
pip install robo-appian
```

## Install with Poetry

```bash
poetry add robo-appian
```

Installing the Python package installs Playwright's Python library. Browser binaries are provisioned explicitly so projects can choose only what they need.

## Install browser binaries

The CLI invokes Playwright with the **current Python interpreter** (`sys.executable -m playwright install ...`), so it works consistently in Windows, Linux, macOS, virtual environments, Poetry environments, and CI agents.

Install the full Playwright-managed browser set:

```bash
robo-appian install-browser
```

`all` is an explicit alias for the same full install:

```bash
robo-appian install-browser all
```

Install only one engine:

```bash
robo-appian install-browser firefox
robo-appian install-browser chromium
robo-appian install-browser webkit
```

With Poetry:

```bash
poetry run robo-appian install-browser firefox
```

!!! tip "Install the browser you actually run"
    The default generic browser lifecycle uses `BROWSER=chromium` when no browser is configured. If your test environment sets `BROWSER=firefox`, install Firefox with `robo-appian install-browser firefox`.

## Configure the runtime browser

The generic lifecycle used by the robo-appian pytest plugin reads the browser configuration supplied through the automation environment. The primary settings are:

| Setting | Purpose | Default |
| --- | --- | --- |
| `BROWSER` | Browser engine: `chromium`, `firefox`, or `webkit` | `chromium` |
| `HEAD_LESS` | Run without a visible browser window | `true` |
| `WAIT_TIME` | Default operation/navigation timeout in seconds | automation-project configuration |

For example:

```text
BROWSER=firefox
HEAD_LESS=false
```

Then provision the matching engine:

```bash
robo-appian install-browser firefox
```

## Enable the pytest fixtures

Load the plugin from the consuming project's root `conftest.py`:

```python
pytest_plugins = ("robo_appian.pytest_plugin",)
```

The plugin owns these public fixtures:

```text
browser -> RoboBrowser
context -> RoboContext
page    -> RoboPage
```

A test can therefore consume `RoboPage` without importing Playwright:

```python
from robo_appian import RoboPage


def test_home(page: RoboPage) -> None:
    page.goto("https://your-appian-site.example/")
```

Application projects can override authenticated storage state and lifecycle-provider fixtures without replacing the public `browser`, `context`, or `page` fixtures. See [Pytest Integration](../guides/pytest-integration.md).

## Verify the installation

Verify the package and framework wrappers:

```bash
python -c "from robo_appian import RoboBrowser, RoboContext, RoboPage, RoboLocator; print('robo-appian import OK')"
```

Verify the CLI:

```bash
robo-appian --help
robo-appian install-browser --help
```

## What installation does not configure

`robo-appian` intentionally does not know your application-specific:

- Appian URLs
- credentials or secret-management policy
- authentication workflow
- business workflows and assertions
- test data
- application labels and rules
- worker-to-credential mapping

Those remain in the consuming project. `robo-appian` owns the browser/runtime wrapper layer and reusable Appian interaction mechanics.

<div class="ra-doc-next" markdown>

**Next:** [Understand the framework architecture →](concepts.md)

</div>
