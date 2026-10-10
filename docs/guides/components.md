# Components

The preferred import style is through the package-level API:

```python
from robo_appian import AppianPage, AppianTable
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

Use `page.link(name=...)` for both native Appian `<a>` links and linked-card controls exposed with `role="link"`. It returns an [`AppianLink`](../api/appian-link.md).

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

Selection is idempotent and state is derived from Appian accessibility text (`Selected Tab.` / `Unselected Tab.`), not generated CSS classes.

## Tables

Create a semantic table component from `AppianPage`. At least one of `label`, `header_name`, `row_name`, or `column_name` is required.

```python
items = page.table(
    label="Items",
    row_name="Item 1001",
    column_name="Status",
)
```

Matching is consistent across Appian component factories: `exact=True` and `visible=True` are the defaults. Use `exact=False` for intentional partial semantic-name/label matching. `visible=False` targets hidden matches; `visible=None`, `visible=""`, or whitespace removes visibility filtering. For tables, no visibility filter leaves both visible and hidden matches in the live locator.

All semantic Appian component factories also accept `timeout` in **seconds**. The default is `None`, which preserves the framework timeout configured from `WAIT_TIME`. A positive finite value overrides `WAIT_TIME` for waits and actions owned by that component:

```python
page.dropdown(label="Category", timeout=10).select(value="General")
page.button(name="Submit", timeout=15).click()
```

This is useful for dependent Appian controls that are rendered immediately but remain disabled while a preceding selection loads their values. Dropdown value selection waits for either the requested value to be auto-selected by Appian or for the control to become editable, instead of relying on a snapshot `is_enabled()` check.

`AppianTable` is the single table component API. Legacy `Table` helpers are removed.

## Common matching and indexing

The page and cell component accessors share the same matching model:

```python
page.button(name="Save")                         # exact=True, visible=True
page.button(name="Sav", exact=False)             # partial semantic match
page.dropdown(label="Category", visible=None)         # no visibility filter
page.dropdown[0].select(value="General")           # first dropdown on page
page.dropdown(label="Category")[0].select(value="General")
```

Component collection indexing is zero-based. Semantic filtering happens before an index such as `[0]` is applied. The same model is available from `AppianCell`.

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
page.textbox(label="Description").fill("Example item")
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.textbox(header="Item Description").fill("General details")
```

### Waiting for an Appian component to become enabled

Enabled-state queries are immediate unless a timeout is explicitly supplied. This is intentional: `component.is_enabled()` never inherits `WAIT_TIME` or the component's configured timeout.

```python
# Snapshot of the current state; no wait.
page.dropdown(label="Category").is_enabled()

# Wait up to a configured short timeout for an Appian dependency to enable it.
dropdown = page.dropdown(label="Category")
if dropdown.is_enabled(timeout=short_wait_seconds):
    dropdown.select(value="General")
```

An explicit `timeout` is expressed in seconds. `is_enabled(timeout=...)` returns `True` as soon as the live component becomes enabled and returns `False` if the timeout expires; the state-query timeout is not raised as an automation failure. This is useful for dependent Appian controls such as Category and Subcategory.
