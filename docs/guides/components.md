# Components

The preferred import style is through the package-level API. In every scope-aware component method, `scope` is **either a Playwright `Page` or a Playwright `Locator` object**. A `Page` searches the whole document; a `Locator` restricts the lookup to that locator's DOM subtree. See [Scope](../api/scope.md) for examples and guidance.

```python
from robo_appian import Button, Dropdown, InputText, Table
```

## Buttons

```python
from robo_appian import Button

Button.click(scope, "Submit")
```

For pages where duplicate button labels require additional disambiguation, use
the attribute-aware helpers exposed by `Button`.

## Text inputs

```python
from robo_appian import InputText

InputText.fill_by_label(scope, "Request Name", "Example Request")
```

## Dropdowns

```python
from robo_appian import Dropdown

Dropdown.select(scope, "Status", "Active")
```

## Tables

```python
from robo_appian import Table

# See the Table API reference for the supported table operations.
```

The API reference is generated directly from the Python source and docstrings,
so use it for exact signatures and available methods.
