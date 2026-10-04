# Your First Test

This walkthrough shows where `robo-appian` fits in a normal Python + Playwright test. The URL and labels are examples; replace them with values from your application.

## 1. Create or obtain a Playwright-backed `scope`

`robo-appian` does not create the browser for you. Your test framework or fixture owns it.

```python
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def scope():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        scope = browser.new_page()
        yield scope
        browser.close()
```

In a real project, keep browser configuration, authentication state, tracing, screenshots, and environment handling in your consumer fixtures.

## 2. Navigate to the Appian application

Navigation and authentication are application-specific, so they stay outside `robo-appian`:

```python
def test_create_request(scope):
    scope.goto("https://your-appian-site.example/")
    # Perform your application's authentication/navigation here.
```

## 3. Use robo-appian for reusable Appian interactions

Import the component that represents the control and identify the control in user-facing terms where the API supports it:

```python
from robo_appian import Button, Dropdown, InputText, Text


def test_create_request(scope):
    scope.goto("https://your-appian-site.example/")
    # Application-specific authentication/navigation belongs here.

    InputText.fill_by_label(scope, "Request Name", "Example Request")
    Dropdown.select(scope, "Request Type", "Travel")
    Button.click(scope, "Submit")

    Text.wait_visible(scope, "Created successfully")
```

The workflow remains in your test project. `robo-appian` supplies generic Appian component mechanics and Playwright performs the browser automation.

## 4. Keep business assertions in the test project

Use pytest, Playwright assertions, or your project's assertion conventions for business expectations. Query methods can provide values when useful:

```python
from robo_appian import Text

message = Text.get_visible_text(scope, "Created successfully", excat_match=True)
assert message == "Created successfully"
```

## 5. Scope repeated labels

If the same label appears in more than one UI region, narrow the current `scope` before calling the component API:

```python
scope = scope.get_by_role("region", name="Request Details")
InputText.fill_by_label(scope, "Name", "Example Request")
```

This is a useful boundary: your project knows **which application region** matters; `robo-appian` knows **how to interact with the reusable Appian component** inside that scope.

## A maintainable consumer-project shape

One possible structure is:

```text
my-automation-project/
├── tests/
│   └── test_request.py
├── workflows/
│   └── request_workflow.py
├── conftest.py
└── pyproject.toml
```

There is no required folder structure. The important separation is architectural:

- consumer project → application workflow, assertions, data, credentials, environment
- `robo-appian` → reusable Appian component behavior
- Playwright → browser automation

## Next steps

Use [Choosing a Component](component-basics.md) when you know what the Appian control looks like but not which helper to use. Use the [API Reference](../api/index.md) for exact signatures, defaults, parameter descriptions, and return values.
