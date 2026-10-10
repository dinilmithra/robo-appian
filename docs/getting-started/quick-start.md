# Quick Start

This page shows the shortest path from installation to a readable Appian test.

## 1. Install robo-appian and a browser

```bash
pip install robo-appian
robo-appian install-browser firefox
```

## 2. Write a simple test

```python
from robo_appian import AppianPage


def test_update_item(page: AppianPage) -> None:
    page.textbox(label="Description").fill("Example item")
    page.date(label="Start Date").fill("10/15/2026")
    page.radio(label="Priority").select("High")
    page.button(name="Submit").click()
```

Read the code the same way a user would describe the page:

1. Enter the item description.
2. Enter the required date.
3. Choose the item priority.
4. Click Submit.

## 3. Run it with pytest

```bash
pytest
```

Your application project normally owns the URL and login process. The `page` fixture is prepared by the automation framework.

## What should I learn next?

- [Your First Test](first-test.md) explains the test structure.
- [Choosing a Component](component-basics.md) shows which API to use for common controls.
- [Troubleshooting](troubleshooting.md) starts from common failure symptoms.
