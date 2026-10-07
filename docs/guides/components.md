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

## Component `Scope` compatibility

The current generated component signatures still use `Scope = Playwright Page | Locator`. That type describes the component implementation's search boundary and is retained for compatibility while the framework wrapper migration continues.

For new consuming-project browser/resource code, use `RoboPage` and `RoboLocator`. Do not create duplicate raw Playwright browser/page fixtures when using the generic `robo-automation` pytest plugin.

The generated API reference is authoritative for the exact current component signatures and defaults.
