# Appian Cell

`AppianCell` represents a resolved table cell. It is also an `AppianLocator`, so normal locator operations remain available, while Appian component factories are automatically scoped to that cell.

```python
cell = page.table(label="Requests").cell(
    row_name="CDRH-OCD-27-M-J501",
    column_number=16,
)

cell.button(name="Approve").click()
```

The same scoped pattern is available for the other Appian semantic components:

```python
cell.link(name="robo appian").click()
cell.dropdown(label="Status").select("Approved")
cell.checkbox(label="Include").check()
cell.radio(label="Decision").select("Yes")
cell.textbox(label="Comment").fill("Approved")
cell.date(label="Date Needed By").fill("10/09/2026")
cell.tab(name="Details").select()
```

## Index-based components inside unlabeled cells

Appian cells do not always render a field label or accessible component name. For those cells, the short component accessors are both callable and zero-based indexable. Indexing is scoped strictly to the resolved cell.

```python
cell.dropdown[0].select(value="Dinil")
cell.button[0].click()
cell.checkbox[0].check()
cell.radio[0].select("Yes")
cell.link[0].click()
cell.textbox[0].fill("Approved")
cell.date[0].fill("10/09/2026")
cell.tab[0].select()
```

The same short accessors remain callable when semantic identification is available:

```python
cell.dropdown(label="CAN").select(value="699H177")
cell.dropdown(label="CAN")[0].select(value="699H177")
cell.button(name="Approve").click()
cell.checkbox(label="Include").check()
```

Component indexing is **zero-based Python indexing** (`component[0]` is the first component in the cell). This is separate from APIs that deliberately use one-based domain indexing, such as dropdown option selection:

```python
# first dropdown in the cell; then first option in that dropdown
cell.dropdown[0].select(index=1)

# first dropdown in the cell; search, then first filtered option
cell.dropdown[0].select(search_text="123", index="1")
```

A nested table can also be resolved semantically or by cell-local index:

```python
nested = cell.table(label="Nested Requests")
nested = cell.table[0]
```

All semantic cell-scoped factories default to `exact=True` and `visible=True`. Pass `exact=False` for intentional partial label/name matching. For visibility, `False` selects hidden matches, while `None`, `""`, or whitespace-only strings apply no visibility filter. Index access targets visible components by default.

## API

::: robo_appian.appian.appian_cell.AppianCell
    options:
      show_root_heading: true
      members_order: source


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework Playwright timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
