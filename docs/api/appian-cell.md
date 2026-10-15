# Appian Cell

`AppianCell` represents a resolved table cell. It is also an `AppianLocator`, so normal locator operations remain available, while Appian component factories are automatically scoped to that cell.

```python
cell = page.grid(label="Items").cell(
    row_name="Item 1001",
    column_number=16,
)

cell.button(name="Approve").click()
```

The same pattern is available for other components inside the table cell:

```python
cell.link(name="View").click()
cell.dropdown(label="Status").select("Approved")
cell.checkbox(label="Include").check()
cell.radio(label="Decision").select("High")
cell.textbox(label="Comment").fill("Approved")
cell.date(label="Date Needed By").fill("10/09/2026")
cell.tab(name="Details").select()
```

Read the user-visible value of a cell with `text()`. Whitespace is normalized, and the same method works for plain text, nested markup, and link text. An empty cell returns `""`.

```python
status = page.grid(label="Items").cell(
    row_name="Item 1001",
    column_name="Status",
).text()
```

## Index-based components inside unlabeled cells

Appian cells do not always render a field label or accessible component name. Use a plural collection's `.first` or zero-based Python index for those cells. Indexing is scoped to the resolved cell.

```python
# First component in the resolved cell
cell.dropdowns.first.select(value="Active")
cell.buttons.first.click()

# Explicit component position when a cell contains more than one
cell.dropdowns[0].select(value="Active")
cell.buttons[0].click()
cell.checkboxes[0].check()
cell.radios[0].select("High")
cell.links[0].click()
cell.textboxes[0].fill("Approved")
cell.dates[0].fill("10/09/2026")
cell.tabs[0].select()
```

Use singular lookup methods when a label or name is available:

```python
cell.dropdown(label="Status").select(value="Active")
cell.button(name="Approve").click()
cell.checkbox(label="Include").check()
```

Component indexing is **zero-based Python indexing** (`cell.dropdowns[0]` is the first dropdown in the cell). Use a plural collection to choose a component; dropdown option selection remains one-based:

```python
# first dropdown in the cell; then first option in that dropdown
cell.dropdowns[0].select(index=1)

# first dropdown in the cell; search, then first filtered option
cell.dropdowns[0].select(search_text="123", index=1)
```

A nested table can also be resolved semantically or by cell-local index:

```python
nested = cell.grid(label="Nested Items")
nested = cell.grids[0]
```

Components inside a table cell use `exact=True` and `visible=True` by default. Use `exact=False` only when you intentionally want a partial name or label match. In normal business automation, keep `visible=True`. When more than one matching component exists in the cell, use component indexing to choose the required one.

## API

::: robo_appian.appian.data.appian_cell.AppianCell
    options:
      show_root_heading: true
      members_order: source
      members:
        - text


## Timeout

`timeout` is expressed in seconds. Leave `timeout=None` to use the normal configured wait time, or provide a positive value when this particular action needs a different wait time.
