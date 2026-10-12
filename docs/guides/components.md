# Components

The preferred import style is through the package-level API:

```python
from robo_appian import AppianPage, AppianGrid
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
    label="Priority"
).select("High")
```

Use the complete question text when possible so common option values such as `Yes` and `No` stay scoped to the correct group.


## Text inputs

```python
page.textbox(label="Description").fill("Example item")
```

## Dropdowns

Use `page.dropdown(...)` for semantic Appian dropdown fields. It returns an [`AppianDropdown`](../api/appian-dropdown.md).

```python
page.dropdown(label="Status").select("Active")
assert page.dropdown(label="Status").is_selected("Active")
```


## Appian links

Use `page.link(name=...)` for business actions presented as links. It returns an [`AppianLink`](../api/appian-link.md).

```python
page.link(name="View Details").click()
page.link(name="Item 1001").click()
page.link(name="Item Details").click()
page.link(name="Return").click()
```

For links inside a table cell, resolve the cell and use its Appian link component, for example `table.cell(...).link(name="Open").click()`.

## Appian tabs

Use `page.tab(name=...)` for Appian linked-card tabs. It returns an [`AppianTab`](../api/appian-tab.md).

```python
page.tab(name="Contacts").select()
assert page.tab(name="Contacts").is_selected()
```

Selecting an already active tab is safe; no additional action is performed.

## Tables

Create a table component from `AppianPage`. At least one of `label`, `header`, `row_name`, or `column_name` is required.

```python
items = page.grid(
    label="Items",
    row_name="Item 1001",
    column_name="Status",
)
```

Matching is consistent across Appian component factories: `exact=True` and `visible=True` are the defaults. Use `exact=False` for intentional partial name/label matching. `visible=False` targets hidden matches; `visible=None`, `visible=""`, or whitespace removes visibility filtering. For tables, no visibility filter leaves both visible and hidden matches in the live locator.

Appian components accept an optional `timeout` in **seconds**. Leave it as `None` to use the configured default, or provide a positive value when a particular business action needs a different wait:

```python
page.dropdown(label="Status", timeout=10).select(value="Active")
page.button(name="Submit", timeout=15).click()
```

This is useful when a dependent field needs extra time to become ready after an earlier business action.

`AppianGrid` is the single table component API. Legacy `Table` helpers are removed.

## Common matching and indexing

The page and cell component accessors share the same matching model:

```python
page.button(name="Save")                         # exact=True, visible=True
page.button(name="Sav", exact=False)             # partial match
page.dropdown(label="Status", visible=None)       # include visible/hidden matches
page.dropdown[0].select(value="Active")           # first dropdown on page
page.dropdown(label="Status")[0].select(value="Active")
```

Component collection indexing is zero-based. The same indexing convention is available for components inside a table cell.

## Input textbox

Use `AppianPage.textbox(...)` for text fields:

```python
page.textbox(label="Description").fill("Example item")
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.textbox(header="Item Description").fill("General details")
```

Searchable text-entry controls use the same textbox API. `fill()` can be chained into `select()`, or `select()` can receive `search_text` directly:

```python
page.textbox("Employee").fill("John").select("John Smith")
page.textbox("Employee").fill("John").select(index=2)

page.textbox("Employee").select(
    search_text="John",
    value="John Smith",
)
page.textbox("Employee").select(
    search_text="John",
    index=2,
)
```

Suggestion indexes are **1-based**. Textbox collection indexes such as `page.textbox[0]` remain **zero-based**.

### Waiting for an Appian component to become enabled

Use `is_enabled()` to check the current state, or provide a timeout when the business flow needs to wait briefly for the component to become enabled.

```python
# Snapshot of the current state; no wait.
page.dropdown(label="Status").is_enabled()

# Wait up to a configured short timeout for an Appian dependency to enable it.
dropdown = page.dropdown(label="Status")
if dropdown.is_enabled(timeout=short_wait_seconds):
    dropdown.select(value="Active")
```

An explicit `timeout` is expressed in seconds. `is_enabled(timeout=...)` returns `True` as soon as the live component becomes enabled and returns `False` if the timeout expires; the state-query timeout is not raised as an automation failure. This is useful for dependent Appian controls such as Status and Owner.


## Structured data

Use `page.dataset(...)` for business data that can appear in three common patterns.

**Summary/detail data:**

```python
basic_info = page.dataset(header="Basic Information", row_number=1)
status = basic_info.data(field="Workflow Status").value
```

**Repeated/list data:**

```python
activity = page.dataset(header="Recent Activities", row_number=1)
action = activity.data(field="Action").value
```

**Grid data:**

```python
fund = page.dataset(header="Funds Availability", row_number=1)
available = fund.data(field="Available Funds").value
```

Use `page.grid(...)` when the automation specifically needs an Appian grid and its row/cell operations. A dataset can also use the complete row/cell API when appropriate. `row_number` and `column_number` are 1-based business positions; `[0]`, `[1]`, and `.first` are normal result-collection selection.

See [AppianDataSet](../api/appian-dataset.md) for all dataset lookup and access patterns.
