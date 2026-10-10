# Appian Table

Use `page.table(...)` to work with rows and cells in an Appian table.

```python
items = page.table(label="Items")
```

A table can be identified by `label`, `header_name`, `row_name`, or `column_name`. Additional identifiers can narrow the match.

`label` matches only the table's accessible name. Use `header_name` for a table
inside an Appian section whose enclosing region has that accessible name:

```python
details = page.table(header_name="Item Details")
```

## Count the displayed rows

```python
count = page.table(label="Items").row_count()
```

`row_count()` returns the number of data rows currently displayed. It does not count the header and does not return the total number of records across other pages.

## Work with a row

Rows can be identified by visible text or by a one-based row number:

```python
items = page.table(label="Items")

row = items.row(name="Item 1001")
row.click()
```

## Work with a cell

A cell can be found directly from the table:

```python
cell = items.cell(
    row_name="Item 1001",
    column_name="Status",
)
```

Names and one-based numbers can be mixed:

```python
items.cell(row_name="Item 1001", column_number=3)
items.cell(row_number=1, column_name="Status")
items.cell(row_number=1, column_number=3)
```

You can also start from a row or column:

```python
items.row(name="Item 1001").cell(column_name="Owner")
items.column(name="Status").cell(row_name="Item 1001")
```

## Use components inside a cell

Cells expose the same Appian component style used elsewhere:

```python
items.cell(
    row_name="Item 1001",
    column_name="Action",
).button[0].click()

items.cell(
    row_name="Item 1001",
    column_name="Status",
).dropdown[0].select(value="Active")
```

## Matching options

`exact=True` and `visible=True` are the defaults. Use `exact=False` for an intentional partial match and `visible=None` when visibility should not filter the result.

```python
page.table(label="Items", exact=False)
page.table(label="Items", visible=None)
```

## API

::: robo_appian.appian.appian_table.AppianTable
    options:
      show_root_heading: true
      members_order: source
      members:
        - cell
        - appian_column
        - row
        - column
        - row_count
