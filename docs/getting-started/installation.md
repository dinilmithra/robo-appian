# Installation

Get `robo-appian` and a Playwright browser into the same Python environment your tests will use.

## Before you start

You need:

- **Python 3.12** (`>=3.12,<3.13`)
- a Python project or virtual environment
- Playwright browser binaries for the browser your project runs

`robo-appian` uses Playwright's **synchronous Python API**. It does not create your browser, fixtures, credentials, or test framework configuration.

## Install with pip

```bash
pip install robo-appian
playwright install chromium
```

The first command installs the Python library and its Playwright dependency. The second installs Chromium for Playwright.

## Install with Poetry

```bash
poetry add robo-appian
poetry run playwright install chromium
```

Using `poetry run` ensures Playwright installs the browser for the same environment as your project.

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

## Verify Playwright can launch Chromium

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
