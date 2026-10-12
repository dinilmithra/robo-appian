# AppianRadioSelect

`AppianRadioSelect` represents an Appian radio group. Create it with `page.radio(...)`.

```python
priority = page.radio(
    label="Priority"
)

priority.select("High")
```

## Check the selected value

```python
if priority.is_selected("High"):
    print("High priority")
```

`select(value)` is idempotent. If the requested option is already selected, no additional action is performed.

Use [`AppianCheckbox`](appian-checkbox.md) for native checkboxes.

## API

::: robo_appian.appian.components.appian_radio_select.AppianRadioSelect
    options:
      show_root_heading: true
      members_order: source
      members:
        - is_selected
        - select


## Exact matching and visibility

By default, robo-appian uses a visible component whose displayed name or label exactly matches what you provide. Keep `exact=True` and `visible=True` for normal business automation. Use `exact=False` only when you intentionally want a partial name or label match. Change `visible` only when your scenario specifically requires a component that is not currently visible.


## Timeout

`timeout` is expressed in seconds. Leave `timeout=None` to use the normal configured wait time, or provide a positive value when this particular action needs a different wait time.

## Identify a radio group by header

```python
page.radio(header="Priority Details").select("High")
```

`header` is the displayed heading used to identify the radio group.
