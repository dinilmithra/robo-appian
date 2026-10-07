# Your First Test

This walkthrough uses the generic pytest fixtures supplied by `robo-automation` and the Appian components supplied by `robo-appian`.

## 1. Fixture discovery

Installing `robo-automation` registers its pytest plugin through the `pytest11` entry point. Under normal pytest plugin autoloading, the public fixture chain is available automatically:

```text
browser -> Playwright Browser
context -> RoboBrowserContext
page    -> RoboPage
```

## 2. Write a test with `RoboPage`

```python
from robo_automation import RoboPage


def test_open_appian(page: RoboPage) -> None:
    page.goto("https://your-appian-site.example/")
    assert "your-appian-site" in page.url
```

Authentication and the target URL are application-specific and belong in the consuming project.

## 3. Locate and act through `RoboLocator`

```python
from robo_automation import RoboPage


def test_user_menu(page: RoboPage) -> None:
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

## 4. Use a stable id when available

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## 5. Use reusable Appian component helpers

```python
from robo_automation import RoboPage
from robo_appian import AppianPage, InputText


def test_create_request(page: RoboPage) -> None:
    InputText.fill_by_label(page, "Request Name", "Example Request")
    page.button(name="Submit").click()
```

The component classes keep reusable Appian lookup and interaction mechanics out of application workflows. Their current signatures may still expose the generic `Scope` compatibility type from `robo-automation`.

## 6. Keep responsibilities separated

The consuming project owns URLs, credentials, authentication policy, workflow orchestration, assertions, test data, and application-specific waits. `robo-appian` owns reusable Appian components/utilities. `robo-automation` owns generic Playwright wrappers, pytest fixtures, and browser/context/page lifecycle.

For authenticated applications, keep authentication in the consuming project by overriding `storage_state`; customize generic context inputs as needed and override `page` only for application navigation/login. See [Pytest Integration](../guides/pytest-integration.md).
