# AppianDataSet

Use `page.dataset(...)` to read **business data** when Appian may display that data as a summary/detail section, a repeated list, or a grid. The same BA-facing pattern works across all three presentations.

## The three dataset patterns

### 1. Summary or detail data

Use this pattern for a section such as **Basic Information**, where one business record is displayed as named values.

```python
basic_info = page.dataset(
    header="Basic Information",
    row_number=1,
)

workflow_status = basic_info.data(field="Workflow Status").value
request_status = basic_info.data(field="Request Status").value
committed_amount = basic_info.data(field="Committed Amount").value
```

A displayed field with no value is still valid and returns an empty string:

```python
om_due_date = basic_info.data(field="OM Due Date").value
# ""
```

### 2. Repeated/list data

Use this pattern for data such as **Recent Activities**, where Appian displays several records one after another.

```python
activity = page.dataset(
    header="Recent Activities",
    row_number=1,
)

action = activity.data(field="Action").value
origin = activity.data(field="Action Origin").value
status = activity.data(field="To Workflow Status").value
```

`row_number` is **1-based** because it represents the displayed business row:

```python
page.dataset(header="Recent Activities", row_number=1)  # first row
page.dataset(header="Recent Activities", row_number=2)  # second row
```

### 3. Grid data

A dataset can also read an Appian grid using the same data API:

```python
fund = page.dataset(
    header="Funds Availability",
    row_number=1,
)

available = fund.data(field="Available Funds").value
```

When the automation specifically needs grid behavior, `page.grid(...)` remains the dedicated grid API.

## Ways to identify a dataset

Use the business-visible information that best identifies the data:

```python
page.dataset(header="Recent Activities")
page.dataset(label="Request History")
page.dataset(field="Action")
page.dataset(fields=["Action", "Action Origin", "To Workflow Status"])
page.dataset(row_name="My Requests", column_name="Requests")
```

Identifiers can be combined to narrow a match:

```python
page.dataset(
    header="Recent Activities",
    fields=["Action", "Action Origin", "To Workflow Status"],
)
```

There is intentionally no generic `name` argument. `header`, `label`, `field`, `fields`, `row_name`, and `column_name` describe what the BA sees on the page more clearly.

## Multiple matching datasets

Without `row_number`, the dataset lookup can represent multiple matching datasets. Results preserve Appian's displayed order. Use normal zero-based Python collection selection:

```python
matches = page.dataset(header="Recent Activities")

first = matches[0]
# equivalent convenience form
first = matches.first
```

This is different from `row_number`, which is 1-based:

```text
row_number=1   first displayed business row
[0]            first item in a Python result collection
.first         same result as [0]
```

## Check or wait for visibility

`is_visible()` checks immediately. `wait_until_visible()` waits for the dataset
and returns it for continued use. A timeout override is expressed in seconds.

```python
funds = page.dataset(header="Funds Availability")
if funds.is_visible():
    print("Funds are displayed")
funds.wait_until_visible(timeout=8)
funds.first.wait_until_visible()
```

## Reading data values

`data()` identifies a business field. When exactly one value matches, read it directly with `.value`:

```python
activity.data(field="To Workflow Status").value
```

The explicit collection forms are also available:

```python
activity.data(field="To Workflow Status")[0].value
activity.data(field="To Workflow Status").first.value
```

If several values match, choose the intended item with `[0]`, `[1]`, or `.first` before reading `.value`. Dataset values remain in Appian's displayed order; robo-appian does not re-sort them.

A field can also be selected by its **1-based** business position:

```python
activity.data(field_number=1).value
```

## Row and cell operations

`AppianDataSet` also exposes the same `AppianRow` and `AppianCell` behavior used by `page.grid(...)` when the dataset has row/cell structure.

```python
funds = page.dataset(header="Funds Availability")
row = funds.row(row_number=1)
cell = row.cell(column_name="Available Funds")
amount = cell.text()
```

All existing row and cell component operations remain available. For example, when a cell contains an interactive control:

```python
row.cell(column_name="Employee").textbox(label="Employee").fill("John").select("John Smith")
row.cell(column_name="Status").dropdown(label="Status").select(value="Approved")
row.cell(column_name="Action").button(name="Edit").click()
row.cell(column_name="Details").link(name="View").click()
```

For list-style business data, `data(field=...)` is normally clearer to a BA than treating the record as a grid cell.

## `grid` versus `dataset`

Use `page.grid(...)` when the business control is specifically an Appian grid and the test is working with its rows/cells. Use `page.dataset(...)` when the test is reading structured business data that may be displayed as a summary, repeated list, or grid.

## Signature

```python
def dataset(
    self,
    *,
    label: str | None = None,
    header: str | None = None,
    field: str | None = None,
    fields: list[str] | None = None,
    row_name: str | None = None,
    column_name: str | None = None,
    row_number: int | None = None,
    exact: bool = True,
    visible: bool | None = True,
    timeout: float | int | None = None,
) -> AppianDataSet:
    ...
```
