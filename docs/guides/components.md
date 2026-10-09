# Components

The preferred import style is through the package-level API:

```python
from robo_appian import AppianPage, Dropdown, Table
```

Component helpers encapsulate reusable Appian-specific interaction mechanics. Browser lifecycle belongs to `robo-automation`; Appian component interactions use `AppianPage` and `AppianLocator`.

## Buttons

```python
page.button(name="Submit").click()
```

## Radio and checkbox selections

Use `page.checkbox(...)` for true Appian checkbox fields. It returns an [`AppianCheckbox`](../api/appian-checkbox.md).

Use `page.radio(...)` for Appian radio groups. It returns an [`AppianRadioSelect`](../api/appian-radio-select.md).

```python
page.radio(
    label="Is this request for a conference?"
).select("Yes")
```

Use the complete question text when possible so common option values such as `Yes` and `No` stay scoped to the correct group.


## Text inputs

```python
page.textbox(label="Request Name").fill("Example Request")
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

## Input textbox

Use `AppianPage.textbox(...)` for text fields:

```python
page.textbox(label="Request Name").fill("Example Request")
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.textbox(header="Conference Description").fill("General conference details")
```
