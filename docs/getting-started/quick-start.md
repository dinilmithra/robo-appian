# Quick Start

This is the shortest path from installing `robo-appian` to using its Appian components with the generic browser fixtures supplied by `robo-automation`.

## 1. Install robo-appian and a browser

```bash
pip install robo-appian
robo-appian install-browser firefox
```

`robo-appian` depends on `robo-automation`, so the generic wrapper/pytest layer is installed with it.

## 2. Use the auto-discovered pytest fixtures

`robo-automation` registers `robo_automation.pytest_plugin` through the `pytest11` entry-point group. No `pytest_plugins` declaration or `-p` option is required under normal pytest plugin autoloading.

The generic fixture chain is:

```text
browser -> Playwright Browser
page    -> AppianPage
```

## 3. Use `AppianPage`

```python
from robo_appian import AppianPage


def test_user_options(page: AppianPage) -> None:
    page.goto("https://your-appian-site.example/")

    user_options = page.get_by_attributes(
        attributes={
            "role": "button",
            "aria-label": "User options",
        },
        excat_match=True,
    )

    user_options.to_be_visible()
    user_options.click()
```

`get_by_attributes(...)` returns an `AppianLocator` from `robo-appian`.

## 4. Use Appian components for reusable control behavior

```python
from robo_appian import AppianPage, InputText


def test_create_request(page: AppianPage) -> None:
    InputText.fill_by_label(page, "Request Name", "Example Request")
    page.button(name="Submit").click()
```

`robo-appian` owns Appian-specific component behavior; `robo-automation` owns the generic browser/page/locator wrappers and pytest lifecycle.

## 5. Customize application behavior narrowly

Keep authentication, navigation, diagnostics policy, and worker-aware storage state in the consuming application. Override `storage_state`, `context_options`, `wait_time`, or `context_page_handler` as needed, and override `page` when application-specific navigation/login is required. See [Pytest Integration](../guides/pytest-integration.md).
