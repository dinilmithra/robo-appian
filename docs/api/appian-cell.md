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

Appian cells do not always render a field label or accessible component name. For those cells, the short component accessors are both callable and zero-based indexable. Indexing is scoped strictly to the resolved cell.

```python
cell.dropdown[0].select(value="Active")
cell.button[0].click()
cell.checkbox[0].check()
cell.radio[0].select("High")
cell.link[0].click()
cell.textbox[0].fill("Approved")
cell.date[0].fill("10/09/2026")
cell.tab[0].select()
```

The same short accessors remain callable when semantic identification is available:

```python
cell.dropdown(label="Status").select(value="Active")
cell.dropdown(label="Status")[0].select(value="Active")
cell.button(name="Approve").click()
cell.checkbox(label="Include").check()
```

Component indexing is **zero-based Python indexing** (`component[0]` is the first component in the cell). This is separate from APIs that deliberately use one-based domain indexing, such as dropdown option selection:

```python
# first dropdown in the cell; then first option in that dropdown
cell.dropdown[0].select(index=1)

# first dropdown in the cell; search, then first filtered option
cell.dropdown[0].select(search_text="123", index=1)
```

A nested table can also be resolved semantically or by cell-local index:

```python
nested = cell.grid(label="Nested Items")
nested = cell.table[0]
```

Components inside a table cell use `exact=True` and `visible=True` by default. Use `exact=False` only when you intentionally want a partial name or label match. In normal business automation, keep `visible=True`. When more than one matching component exists in the cell, use component indexing to choose the required one.

## API

::: robo_appian.appian.appian_cell.AppianCell
    options:
      show_root_heading: true
      members_order: source
      members:
        - text


## Timeout

`timeout` is expressed in seconds. Leave `timeout=None` to use the normal configured wait time, or provide a positive value when this particular action needs a different wait time.
