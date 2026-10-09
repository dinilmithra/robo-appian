# AppianRadioSelect

`AppianRadioSelect` represents an Appian radio group. Create it with `page.appian_radio(...)`.

```python
conference = page.appian_radio(
    label="Is this request for a conference?"
)

conference.select("Yes")
```

## Check the selected value

```python
if conference.is_selected("Yes"):
    print("Conference request")
```

`select(value)` is idempotent. If the requested option is already selected, no click is performed. Radio groups are resolved by semantic Appian relationships such as `aria-labelledby`, and options are scoped to the owning group.

Use [`AppianCheckbox`](appian-checkbox.md) for native checkboxes.
