# Your First Test

Installing `robo-appian` provides the Appian pytest integration automatically.

## 1. Write a test with `AppianPage`

```python
from robo_appian import AppianPage


def test_open_appian(page: AppianPage) -> None:
    page.goto("https://your-appian-site.example/")
    assert "your-appian-site" in page.url
```

Authentication and the target URL are application-specific and belong in the consuming project.

## 2. Use Appian locators

```python
from robo_appian import AppianPage


def test_user_menu(page: AppianPage) -> None:
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

## 3. Use fluent Appian components

```python
from robo_appian import AppianPage


def test_create_request(page: AppianPage) -> None:
    page.textbox(label="Request Name").fill("Example Request")
    page.button(name="Submit").click()
```

The consuming project owns URLs, authentication policy, workflow orchestration, assertions, test data, and application-specific waits. `robo-appian` owns reusable Appian interactions, while `robo-automation` owns generic resource lifecycle.
