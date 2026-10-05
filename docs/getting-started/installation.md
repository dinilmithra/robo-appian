# Installation

Install `robo-appian` into the same Python environment your tests will use. Browser provisioning is a separate Playwright/project concern.

## Before you start

You need:

- **Python 3.12** (`>=3.12,<3.13`)
- a Python project or virtual environment
- a Playwright-supported browser available to the environment that runs your tests

`robo-appian` uses Playwright's **synchronous Python API**. It does not create or provision your browser, fixtures, credentials, or test framework configuration.

!!! important "Chromium is not required by robo-appian"
    `robo-appian` is not tied to Chromium. Use the browser configured by your Playwright test project. Playwright supports the Chromium, Firefox, and WebKit browser engines. Chromium-based branded browsers such as Google Chrome or Microsoft Edge can also be used through Playwright browser channels when configured by the consumer project.

## Install with pip

```bash
pip install robo-appian
```

This installs the Python library and its Playwright Python dependency. It does **not** install a Playwright-managed browser binary.

## Install with Poetry

```bash
poetry add robo-appian
```

This installs `robo-appian` into your Poetry environment. Browser provisioning remains separate from package installation.

## Browser setup

If your test environment already provides the browser your project uses, no additional browser installation is required for `robo-appian`.

If your project uses a Playwright-managed browser and that browser is not installed yet, install only the browser engine your project needs. For example:

```bash
# Chromium example
playwright install chromium

# Firefox example
playwright install firefox

# WebKit example
playwright install webkit
```

With Poetry, run the command inside the same environment:

```bash
poetry run playwright install chromium
```

To install all Playwright-managed browser engines, use:

```bash
playwright install
```

The browser choice belongs to the consumer automation project. The `chromium` commands above are examples, not a `robo-appian` requirement.

## Verify robo-appian

```bash
python -c "from robo_appian import Button, InputText, Table; print('robo-appian import OK')"
```

With Poetry:

```bash
poetry run python -c "from robo_appian import Button, InputText, Table; print('robo-appian import OK')"
```

Expected output:

```text
robo-appian import OK
```

## Verify your configured Playwright browser

The following example verifies Playwright-managed Chromium. If your project uses Firefox, WebKit, Chrome, Edge, or another configured Playwright channel, adapt the launch configuration to match your project.

Create `verify_playwright.py`:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    scope = browser.new_page()
    scope.set_content("<h1>Playwright OK</h1>")
    print(scope.get_by_role("heading").text_content())
    browser.close()
```

Run it:

```bash
python verify_playwright.py
```

Or with Poetry:

```bash
poetry run python verify_playwright.py
```

You should see:

```text
Playwright OK
```

!!! note "CI and Linux runners"
    Some Linux environments also require operating-system packages used by Playwright browsers. Provision those dependencies in the runner image or according to your organization's CI setup.

## What installation does not configure

Installing the library does **not** configure:

- a specific browser engine or browser channel
- Appian URLs or credentials
- authentication or navigation flows
- pytest fixtures
- environment configuration
- application-specific labels or business rules
- application-specific test data
- workflow-specific waits

Those concerns stay in the consumer automation project.

<div class="ra-doc-next" markdown>

**Next:** [Understand the architecture and label-oriented model →](concepts.md)

</div>
