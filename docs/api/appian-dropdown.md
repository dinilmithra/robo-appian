# AppianDropdown

`AppianDropdown` represents an Appian dropdown identified by its field label.
Create it with `page.dropdown(...)`.

```python
dropdown = page.dropdown(label="Order Type")
```

Appian exposes the control as a semantic `role="combobox"` associated with its
field label through `aria-labelledby`. The option list is associated through
`aria-controls`. `AppianDropdown` uses those accessibility relationships and
does not depend on generated Appian CSS classes.

## Select a value

```python
page.dropdown(label="Required Source").select("No")
```

`select()` is idempotent. If the requested value is already selected, it does
not click or reopen the dropdown. After a successful selection it re-resolves
the control to tolerate Appian rerenders and immediately triggers focus-out
with `blur()`. It does not use Tab for dropdown validation/focus-out. The same
blur behavior applies when Appian has already auto-selected the requested value.

## Read selection state

```python
dropdown = page.dropdown(label="Order Type")

current = dropdown.value()
assert dropdown.is_selected("Office Supplies")
```

`is_selected(value)` reads the current state; it does not wait for another
value to become selected.

## Disabled dropdowns

```python
holder = page.dropdown(label="P-Card Holder")

assert holder.is_disabled()
print(holder.value())
```

Disabled Appian dropdowns remain readable through their combobox text and
`aria-disabled="true"` state.

## Exact matching and visibility

The common Appian matching contract applies. `exact=True` and `visible=True` are the defaults:

```python
page.dropdown(label="Status")                 # exact + visible (defaults)
page.dropdown(label="Stat", exact=False)         # partial label match
page.dropdown(label="Status", visible=True)   # visible only
page.dropdown(label="Status", visible=False)  # hidden only
page.dropdown(label="Status", visible=None)   # no visibility filter
page.dropdown(label="Status", visible="")     # same as None
```

## Component indexing

Dropdown components can be indexed before or after semantic filtering. Component indexing is zero-based.

```python
page.dropdown[0].select(value="Dinil")
page.dropdown(label="CAN")[0].select(value="12345")
cell.dropdown[0].select(value="Dinil")
cell.dropdown(label="CAN")[0].select(value="12345")
```

Dropdown **option** indexing remains one-based, so `page.dropdown[0].select(index=1)` means the first dropdown component and then its first option.

## Inside a table cell

`AppianCell` exposes the same component factory:

```python
page.table(label="Requests").cell(
    row_name="CDRH-OCD-27-M-J501",
    column_name="Status",
).dropdown(label="Status").select("Approved")
```

## Appian DOM relationships

`AppianDropdown` identifies a dropdown from Appian accessibility relationships rather than Appian CSS classes:

```text
field label id
    -> combobox role="combobox" aria-labelledby=<label id>
    -> aria-controls=<listbox id>
    -> listbox role="listbox"
    -> option role="option"
```

Opening is asynchronous. `select()` clicks the combobox and waits for `aria-expanded="true"`, then waits for the listbox referenced by `aria-controls` to become visible. Searchable dropdowns are detected after expansion from the associated `<field-id>_searchInput`; the requested value is typed there before the exact option is selected. Normal dropdowns simply skip the search step.

Disabled dropdowns remain `role="combobox"` with `aria-disabled="true"` and can still be read with `value()`, but `select()` will not interact with them. Appian read-only display fields that contain only label-associated paragraph text are intentionally not treated as dropdowns.

## Search text, value, and index

For searchable Appian dropdowns, the text used to filter the list can differ
from the exact option value to select:

```python
page.dropdown(label="CAN").select(
    search_text="1234",
    value="12345",
)
```

`search_text` is entered only into the dynamically rendered Appian search
input. `value` is then matched against the filtered `role="option"` items and clicked.

Dropdowns also support 1-based option indexes:

```python
page.dropdown(label="P-Card Holder").select(index=2)
page.dropdown(label="P-Card Holder").select(2)
```

The index is evaluated against the live visible option order after the dropdown is
expanded (and after filtering when a search is used). Appian can expose the
listbox while its values are still loading, so index selection waits until the
requested option exists rather than treating a transient zero-option state as
out-of-range. Appian placeholder options such as `Select a Value` are excluded
from this public index. Therefore `index=1` selects the first real business value.
The `Searching...` live-region message may be useful diagnostics, but option
availability is the authoritative readiness signal.

Cell-scoped dropdowns use the same component and selection API:

```python
cell.dropdown(label="CAN").select(search_text="123", index="1")
cell.dropdown(label="CAN").select(value="12345")
```

`index` is 1-based and accepts either an integer or a numeric string.

## Component timeout

`timeout` is optional and expressed in **seconds**. `timeout=None` uses the normal Playwright/context timeout configured from `WAIT_TIME`. Supplying a positive finite timeout overrides that default for dropdown readiness, expansion, listbox/search loading, option interaction, and post-selection verification.

```python
page.dropdown(
    label="Request Category",
    timeout=10,
).select(value="Purchase Request")
```

This is especially important for dependent Appian dropdowns. A control can already exist in the DOM with `aria-disabled="true"` while Appian loads values after an upstream selection. When selecting by value with a component timeout, `select()` waits for either of two valid outcomes: Appian auto-selects the requested value while the control remains disabled, or the control becomes editable so robo-appian can select the requested value explicitly. The component re-resolves the live combobox while waiting so an Appian rerender cannot freeze the readiness check.
