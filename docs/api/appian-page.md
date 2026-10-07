# AppianPage and AppianLocator

`AppianPage` and `AppianLocator` are Appian-specific specializations layered over the generic `robo-automation` wrappers.

```python
from robo_appian import AppianLocator, AppianPage
```

`AppianPage` derives from `RoboPage` and selects `AppianLocator` as its wrapped locator type. Generic wrapped lookups such as `get_by_id()` and `get_by_attributes()` therefore return `AppianLocator` while retaining the base `RoboPage` API.

## Pytest specialization

Installing `robo-appian` registers `robo_appian.pytest_plugin`. Its `appian_page` fixture specializes the lower-layer `robo_page` supplied by `robo-automation` and exposes that specialization as the public `page` fixture. No consumer wrapper-selector fixture or class-selection code is needed.

```text
RoboPage (robo_page)
      ↓ specialize
AppianPage (appian_page)
      ↓
page
```

A consuming application may override `page` for application-specific startup while depending on `appian_page`. Page creation and teardown remain owned by `robo-automation`.


## Fluent components

```python
button = page.button(name="Save")
button.click()
```
