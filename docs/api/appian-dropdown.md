# Appian Dropdown

Use a dropdown when a user needs to choose one value from a list.

```python
dropdown = page.dropdown(label="Category")
dropdown.select(value="General")
```

## Read the current value

```python
dropdown = page.dropdown(label="Status")

current = dropdown.value()
assert dropdown.is_selected("Active")
```

`is_selected(value)` reads the current state. It does not wait for a different value to become selected.

## Matching a dropdown

Exact, visible matching is the default:

```python
page.dropdown(label="Status")
page.dropdown(label="Stat", exact=False)
page.dropdown(label="Status", visible=False)
page.dropdown(label="Status", visible=None)
```

`visible=None`, `visible=""`, and whitespace-only visibility values apply no visibility filter.

## Select by option position

Option indexes are one-based:

```python
page.dropdown(label="Category").select(index=1)
```

`index=1` selects the first real option. Placeholder values such as `Select a Value` are not counted.

## Search before selecting

Some dropdowns provide a search box after they are opened. Use `search_text` to filter the available choices, then select by value or index:

```python
page.dropdown(label="Product").select(
    search_text="Lap",
    value="Laptop",
)

page.dropdown(label="Product").select(
    search_text="Lap",
    index=1,
)
```

The dropdown waits for the requested option to become available when Appian is still loading choices.

## Component indexing

Component indexes are zero-based Python indexes:

```python
page.dropdown[0].select(value="General")
page.dropdown(label="Category")[0].select(value="General")
```

This is different from option indexes, which are one-based.

## Inside a table cell

```python
page.table(label="Items").cell(
    row_name="Item 1001",
    column_name="Status",
).dropdown[0].select(value="Active")
```

## Waiting for a dependent dropdown

Some fields become enabled after another selection. `is_enabled()` checks immediately; `is_enabled(timeout=...)` waits up to the supplied number of seconds.

```python
page.dropdown(label="Category").select(value="General")

subcategory = page.dropdown(label="Subcategory")
if subcategory.is_enabled(timeout=8):
    subcategory.select(value="Standard")
```

A component-level `timeout` can also be supplied when creating the dropdown:

```python
page.dropdown(label="Subcategory", timeout=8).select(value="Standard")
```

## API

::: robo_appian.appian.appian_dropdown.AppianDropdown
    options:
      show_root_heading: true
      members_order: source
      members:
        - wait_until_visible
        - is_visible
        - is_disabled
        - is_enabled
        - value
        - is_selected
        - options
        - select
