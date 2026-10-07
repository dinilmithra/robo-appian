# Components

The preferred import style is through the package-level API:

```python
from robo_appian import AppianPage, Dropdown, InputText, Table
```

Component helpers encapsulate reusable Appian-specific interaction mechanics. Browser lifecycle and generic element ownership belong to the framework wrappers (Playwright `Browser`, `RoboBrowserContext`, `RoboPage`, and `RoboLocator`).

## Buttons

```python
page.button(name="Submit").click()
```

## Text inputs

```python
InputText.fill_by_label(page, "Request Name", "Example Request")
```

## Dropdowns

```python
Dropdown.select(page, "Status", "Active")
```

## Tables

```python
from robo_appian import Table

# See the Table API reference for supported table/grid operations.
```

## Appian scoping

For new Appian APIs, use `AppianPage` for page-wide operations and `AppianLocator` for dialog/subtree operations. Reusable code that intentionally accepts both can use `AppianScope = AppianPage | AppianLocator`.

Some older non-button component helpers still expose the generic lower-layer `Scope` annotation. Treat that as a compatibility signature. New component work should follow the Appian-layer model.

`AppianButton` is the reference fluent component API:

```python
button = page.button(name="Save")
button.click()
```

Button identity requires `<button type="button">`. The presence of the HTML `disabled` attribute means the button is disabled; its absence means the button is enabled. CSS classes are not used to determine enabled state.
