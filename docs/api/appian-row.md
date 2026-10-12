# Appian Row

`AppianRow` represents a row returned by an Appian grid. Use it when a business flow needs to work with a particular row and then click the row or access one of its cells.

```python
from robo_appian import AppianRow
```

## Work with a row

```python
row = page.grid("Requests").row(row_number=1)
row.click()
```

Business row numbers are **1-based**: `row_number=1` means the first displayed row.

## Work with a cell in the row

```python
row = page.grid("Requests").row(row_number=1)
row.cell(column_name="Employee")
```

Components inside a cell can use the normal component APIs:

```python
row.cell(column_name="Employee").textbox[0].fill("John").select("John Smith")
```

## API

::: robo_appian.appian.appian_row.AppianRow
    options:
      show_root_heading: true
      members_order: source
