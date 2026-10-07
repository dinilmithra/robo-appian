# AppianPage and AppianLocator

`AppianPage` and `AppianLocator` are Appian-specific specializations layered over the generic `robo-automation` wrappers.

```python
from robo_appian import AppianLocator, AppianPage
```

`AppianPage` derives from `RoboPage` and selects `AppianLocator` as its wrapped locator type. Generic wrapped lookups such as `get_by_id()` and `get_by_attributes()` therefore return `AppianLocator` while retaining the base `RoboPage` API.
