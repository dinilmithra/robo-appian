# Quick Start

Import components from the package-level public API whenever possible:

```python
from robo_appian import Button, InputText, Text
```

A simple Playwright interaction can then use the reusable component helpers:

```python
from robo_appian import Button, InputText, Text


def create_item(page):
    InputText.fill_by_label(page, "Name", "Example")
    Button.click(page, "Submit")
    Text.wait_visible(page, "Created successfully")
```

Keep application-specific workflow orchestration in the consuming project. The
library should remain focused on reusable Appian/Playwright interaction mechanics.
