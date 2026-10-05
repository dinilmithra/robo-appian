# Quick Start

This is the shortest path from installation to a test that uses the robo-appian wrapper stack.

## 1. Install robo-appian and a browser

```bash
pip install robo-appian
robo-appian install-browser firefox
```

Choose the browser engine your environment will run.

## 2. Enable the pytest plugin

In the consuming project's root `conftest.py`:

```python
pytest_plugins = ("robo_appian.pytest_plugin",)
```

The plugin provides `browser`, `context`, and `page` fixtures as `RoboBrowser`, `RoboContext`, and `RoboPage`.

## 3. Use `RoboPage`

```python
from robo_appian import RoboPage


def test_user_options(page: RoboPage) -> None:
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

`get_by_attributes(...)` returns a `RoboLocator`.

## 4. Wait for dynamic state when needed

```python
user_options.wait_for_attribute(
    attributes={
        "aria-expanded": "true",
    }
)
```

The timeout is optional. Omit it to use the configured default.

## 5. Use a stable id when available

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## 6. Use Appian components for reusable control behavior

The package also exposes component helpers such as `Button`, `Dropdown`, `InputText`, and `Table`. Their generated API reference documents the exact current signatures and the internal `Scope` compatibility boundary.

```python
from robo_appian import Button, InputText

InputText.fill_by_label(page, "Request Name", "Example Request")
Button.click(page, "Submit")
```

!!! note "Framework wrappers are the consumer boundary"
    New browser lifecycle code should use `RoboBrowser`, `RoboContext`, `RoboPage`, and `RoboLocator`. Raw Playwright `Page | Locator` remains documented as `Scope` because existing component APIs still use that implementation boundary.

## 7. Customize authentication without replacing the fixtures

Keep application-specific authentication/storage-state logic in the consuming project by overriding the lifecycle-provider or `storage_state` fixtures. See [Pytest Integration](../guides/pytest-integration.md).
