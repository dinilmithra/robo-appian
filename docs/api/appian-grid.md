# Appian Grid

Use `page.grid(...)` to work with rows and cells in an Appian grid.

```python
items = page.grid(label="Items")
```

A grid can be identified by `label`, `header`, `row_name`, or `column_name`. Additional identifiers can narrow the match.

`label` matches only the grid's own accessible name. `header` matches
either a region's accessible name or header text, without requiring a heading
role. Header text can appear in a heading, nested span, paragraph, strong text,
or table caption. Text outside the grid resolves through its nearest
table-containing ancestor; a caption resolves to its own table. Ordinary cell
text is not treated as a header. A grid matched by both region and text paths
is returned only once:

```python
details = page.grid(header="Item Details")
```

## Count the displayed rows

```python
count = page.grid(label="Items").row_count()
```

`row_count()` returns the number of data rows currently displayed. It does not count the header and does not return the total number of records across other pages.

## Work with a row

Rows can be identified by visible text or by a one-based row number:

```python
items = page.grid(label="Items")

row = items.row(name="Item 1001")
row.click()
```

## Work with a cell

A cell can be found directly from the grid:

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
page.grid(label="Items", exact=False)
page.grid(label="Items", visible=None)
```

## API

::: robo_appian.appian.data.appian_grid.AppianGrid
    options:
      show_root_heading: true
      members_order: source
      members:
        - cell
        - appian_column
        - row
        - column
        - row_count
