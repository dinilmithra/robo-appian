# robo-appian

`robo-appian` provides reusable Playwright component helpers for Appian UI automation.
It is intentionally focused on generic interaction behavior so application-specific
workflow rules, labels, waits, test data, and business logic can remain in the
consumer project.

## What it provides

The public API includes helpers for buttons, checkboxes, dropdowns, date and text
inputs, links, menu buttons, radio controls, record lists, regions, searchable
controls, tabs, tables, text, and shared component utilities.

## Install

```bash
pip install robo-appian
playwright install chromium
```

## Basic example

```python
from robo_appian import Button, InputText


def submit_request(page):
    InputText.fill_by_label(page, "Request Name", "Example Request")
    Button.click(page, "Submit")
```

Start with [Installation](getting-started/installation.md), then see the
[Components guide](guides/components.md) and [API reference](api/index.md).
