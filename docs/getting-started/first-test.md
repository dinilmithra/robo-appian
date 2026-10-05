# Your First Test

This walkthrough uses the robo-appian pytest plugin, so the consuming test never creates a raw Playwright browser, context, or page.

## 1. Enable robo-appian fixtures

Create or update the root `conftest.py`:

```python
pytest_plugins = ("robo_appian.pytest_plugin",)
```

The public fixture chain is:

```text
browser -> RoboBrowser
context -> RoboContext
page    -> RoboPage
```

## 2. Write a test with `RoboPage`

```python
from robo_appian import RoboPage


def test_open_appian(page: RoboPage) -> None:
    page.goto("https://your-appian-site.example/")
    assert "your-appian-site" in page.url
```

Authentication and the target URL are application-specific. A real project can put those operations in lifecycle callbacks so tests receive an already-authenticated `RoboPage`.

## 3. Locate and act through `RoboLocator`

```python
from robo_appian import RoboPage


def test_user_menu(page: RoboPage) -> None:
    page.goto("https://your-appian-site.example/")

    user_options = page.get_by_attributes(
        attributes={
            "role": "button",
            "aria-label": "User options",
        },
        excat_match=True,
    )

    user_options.to_be_visible()
    user_options.wait_for_attribute(attributes={"aria-expanded": "false"})
    user_options.click()
    user_options.wait_for_attribute(attributes={"aria-expanded": "true"})
```

## 4. Use `get_by_id()` when the DOM has a stable id

For markup such as:

```html
<input id="jsAcceptButton" type="button" value="I Agree">
```

use:

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## 5. Use reusable Appian component helpers

```python
from robo_appian import Button, InputText, RoboPage


def test_create_request(page: RoboPage) -> None:
    InputText.fill_by_label(page, "Request Name", "Example Request")
    Button.click(page, "Submit")
```

The component classes keep reusable Appian lookup mechanics out of application workflows. Their current generated signatures may still expose the internal `Scope` compatibility type; the framework fixture boundary remains `RoboPage`.

## 6. Keep business rules in the consuming project

A maintainable project can keep application concerns separate:

```text
my-automation-project/
├── tests/
│   └── test_request.py
├── workflows/
│   └── request_workflow.py
├── conftest.py
└── pyproject.toml
```

The consumer project owns URLs, credentials, authentication policy, workflow orchestration, assertions, test data, and application-specific waits. robo-appian owns reusable browser wrappers, pytest resource fixtures, and generic Appian interactions.

## 7. Add application-specific lifecycle behavior

For authenticated applications, override `storage_state`, `robo_appian_context_lifecycle`, or `robo_appian_page_lifecycle` instead of replacing the public fixtures. See [Pytest Integration](../guides/pytest-integration.md).
