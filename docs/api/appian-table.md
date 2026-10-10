# Appian Table

`AppianTable` represents a semantic Appian table selection. Create it from `AppianPage.table(...)`.

At least one semantic identifier is required:

- `label` — accessible label/name of the table.
- `header_name` — surrounding accessible region/heading used to identify the table.
- `row_name` — text identifying a data row.
- `column_name` — table column header.

Additional identifiers narrow the match.

```python
requests = page.table(
    label="Requests",
    row_name="CDRH-OCD-27-M-J501",
    column_name="Created By",
)
```

## Visibility

All Appian component factories default to `visible=True`.

```python
page.table(label="Requests")                 # visible only
page.table(label="Requests", visible=False)  # hidden only
page.table(label="Requests", visible=None)   # visible + hidden
```

`visible=None` applies no visibility filter. The table's live `locator` can therefore contain both visible and hidden matches.

## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.

## API

::: robo_appian.appian.appian_table.AppianTable
    options:
      show_root_heading: true
      members_order: source

## Row component

Resolve a row from an `AppianTable` and continue with row-scoped semantic components:

```python
row = page.table(label="Requests").row(
    name="CDRH-OCD-27-M-J501"
)
row.link(name="robo appian").click()
```

`row()` accepts either `name` or `row_number`. Its `visible` argument follows the common tri-state rule: `True` (default) selects visible rows, `False` selects hidden rows, and `None`, `""`, or whitespace-only strings apply no visibility filter.

## Row and column cell access

Resolve cells from the table, row, or column direction:

```python
requests = page.table(label="Requests")

created_by = requests.row(
    name="CDRH-OCD-27-M-J501",
).cell(column_name="Created By")

cin = requests.appian_column(
    name="CIN #",
).cell(row_name="CDRH-OCD-27-M-J501")

direct = requests.cell(
    row_name="CDRH-OCD-27-M-J501",
    column_number=16,
)
```

`AppianRow.cell()` accepts `column_name` or one-based `column_number`. `AppianColumn.cell()` accepts `row_name` or one-based `row_number`. Direct `AppianTable.cell()` supports either name/number combination for the row and column.

Every cell lookup returns `AppianCell`, so Appian components inside the cell remain semantically scoped:

```python
requests.cell(
    row_name="CDRH-OCD-27-M-J501",
    column_number=16,
).button(name="Approve").click()

requests.row(
    name="CDRH-OCD-27-M-J501",
).cell(column_name="Created By").link(name="robo appian").click()
```

A resolved row can be selected/clicked directly:

```python
requests.row(name="CDRH-OCD-27-M-J501").select()
```

Cell and column visibility follows the common tri-state rule: `True` selects visible elements, `False` selects hidden elements, and `None`, `""`, or whitespace-only strings apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework Playwright timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
