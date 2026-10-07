# AppianPage and AppianLocator

`AppianPage` is the main page abstraction for Appian automation. `AppianLocator` represents a located Appian element or a scoped subtree.

```python
from robo_appian import AppianLocator, AppianPage
```

Use `AppianPage` for normal page interactions and fluent components:

```python
page.textbox(label="Title").fill("Example request")
page.date(label="Required Award Date").fill("10/07/2026")
page.button(name="Save").click()
```

Use `AppianLocator` when an operation needs to be restricted to a specific dialog, region, or subtree.

::: robo_appian.appian.appian_page.AppianPage
    options:
      show_root_heading: true
      members_order: source

::: robo_appian.appian.appian_locator.AppianLocator
    options:
      show_root_heading: true
      members_order: source
