# Core Concepts

`robo-appian` is the Appian-specific interaction layer. Generic browser lifecycle and pytest resource management are provided by `robo-automation`.

## Appian resource model

Consumer code should use the Appian layer:

```python
from robo_appian import AppianLocator, AppianPage, AppianScope
```

- `AppianPage` is the main entry point for Appian page interactions.
- `AppianLocator` represents an Appian element or scoped subtree.
- `AppianScope` is `AppianPage | AppianLocator` for APIs that intentionally support either scope.

Prefer `AppianPage` for normal page-wide operations and `AppianLocator` only when an operation must be restricted to a dialog, region, or other subtree.

## Fluent components

Create reusable Appian controls directly from the page:

```python
page.textbox(label="Request Name").fill("Example Request")
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.button(name="Submit").click()
```

## Attribute-based lookup

Use `AppianPage.get_by_attributes(...)` when an element is best described by stable attributes:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    },
    excat_match=True,
)
```

For a stable id:

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## Responsibility boundaries

| Concern | robo-automation | robo-appian | Consumer project |
| --- | :---: | :---: | :---: |
| Generic browser and pytest lifecycle | ✓ | | |
| Appian page/locator abstractions | | ✓ | |
| Appian component behavior | | ✓ | |
| Application URL and authentication policy | | | ✓ |
| Worker-specific credentials/session policy | | | ✓ |
| Business workflow orchestration | | | ✓ |
| Assertions and test data | | | ✓ |

Next, use [Quick Start](quick-start.md) for the shortest working path or [Pytest Integration](../guides/pytest-integration.md) for application-specific fixture overrides.
