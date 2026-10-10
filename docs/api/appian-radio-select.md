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

`select(value)` is idempotent. If the requested option is already selected, no click is performed. Radio groups are resolved by semantic Appian relationships such as `aria-labelledby`, and options are scoped to the owning group.

Use [`AppianCheckbox`](appian-checkbox.md) for native checkboxes.

## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
