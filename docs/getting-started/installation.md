# Installation

Install `robo-appian` into the Python environment that runs your tests. The package provides Appian-specific components and a platform-independent CLI for provisioning Playwright-managed browser binaries. Generic Playwright wrappers and pytest lifecycle are supplied by its `robo-automation` dependency.

## Requirements

- Python **3.12** (`>=3.12,<3.13`)
- pytest
- one or more Playwright-supported browser engines installed for the environment that executes the tests

`playwright`, `pytest`, and `robo-automation` are direct dependencies in the current package metadata. The generic fixture stack itself is owned by `robo-automation`; a consuming project does not need `pytest-playwright` for that stack.

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

The generic lifecycle owned by the `robo-automation` pytest plugin reads browser configuration from the automation environment. The primary settings are:

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

Installing `robo-automation` registers `robo_automation.pytest_plugin` through pytest's `pytest11` entry-point group. Under normal plugin autoloading, no `conftest.py` import, `pytest_plugins` declaration, or `-p` option is required.

The lower `robo-automation` plugin owns browser/runtime lifecycle, and the `robo-appian` plugin transparently wraps the `RoboPage` fixture for Appian consumers without hiding Playwright `Page` methods:

```text
robo-automation: robo_page -> AppianPage
                         ↓
robo-appian:     appian_page -> AppianPage
                         ↓
                 page -> AppianPage
```

A normal Appian test consumes `AppianPage`:

```python
from robo_appian import AppianPage


def test_home(page: AppianPage) -> None:
    page.goto("https://your-appian-site.example/")
```

Application projects can override generic context inputs such as `storage_state`, `context_options`, `wait_time`, and `context_page_handler`, and may override `page` when application-specific navigation/login is required. See [Pytest Integration](../guides/pytest-integration.md).

## Verify the installation

Verify both package layers:

```bash
python -c "import robo_appian; from robo_appian import AppianPage, AppianLocator; print('imports OK')"
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

Those remain in the consuming project. `robo-appian` owns reusable Appian interaction mechanics; `robo-automation` owns the generic browser/runtime wrapper and pytest layer.

<div class="ra-doc-next" markdown>

**Next:** [Understand the framework architecture →](concepts.md)

</div>
