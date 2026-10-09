# AppianLocator

`AppianLocator` represents a specific Appian element or a smaller section of an Appian page.

Most tests should begin with [`AppianPage`](appian-page.md). Use `AppianLocator` when you need to restrict an operation to a dialog, region, row, or other subtree so that similar controls elsewhere on the page are not matched accidentally.

```python
from robo_appian import AppianLocator
```

## When to use it

Use an `AppianLocator` when the same text or control appears more than once and you need to work inside one known section of the page.

Conceptually:

```text
AppianPage
  ├─ main form
  ├─ dialog  ← AppianLocator can scope here
  └─ side panel
```

Component helpers that accept a `scope=` argument can use an `AppianLocator` to stay inside that section.

You normally do not create an `AppianLocator` just to fill a regular field. Prefer the simpler page APIs first:

```python
page.textbox(label="Request Title").fill("Example")
page.button(name="Next").click()
```

## API

::: robo_appian.appian.appian_locator.AppianLocator
    options:
      show_root_heading: true
      members_order: source
