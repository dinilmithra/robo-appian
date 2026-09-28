# Components

The preferred import style is through the package-level API:

```python
from robo_appian import Button, Dropdown, InputText, Table
```

## Buttons

```python
from robo_appian import Button

Button.click(page, "Submit")
```

For pages where duplicate button labels require additional disambiguation, use
the attribute-aware helpers exposed by `Button`.

## Text inputs

```python
from robo_appian import InputText

InputText.fill_by_label(page, "Request Name", "Example Request")
```

## Dropdowns

```python
from robo_appian import Dropdown

Dropdown.select(page, "Status", "Active")
```

## Tables

```python
from robo_appian import Table

# See the Table API reference for the supported table operations.
```

The API reference is generated directly from the Python source and docstrings,
so use it for exact signatures and available methods.
