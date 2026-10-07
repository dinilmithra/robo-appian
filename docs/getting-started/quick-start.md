# Quick Start

## 1. Install robo-appian and a browser

```bash
pip install robo-appian
robo-appian install-browser firefox
```

`robo-appian` depends on `robo-automation`, so the generic pytest/resource layer is installed with it.

## 2. Use `AppianPage`

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

## 3. Use Appian components

```python
page.textbox(label="Request Name").fill("Example Request")
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.button(name="Submit").click()
```

Keep authentication, navigation, diagnostics policy, and worker-aware session state in the consuming application. See [Pytest Integration](../guides/pytest-integration.md) for application-specific fixture overrides.
