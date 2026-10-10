# AppianCheckbox

`AppianCheckbox` represents a true Appian checkbox. Create it with `page.checkbox(...)`.

```python
include_details = page.checkbox(
    label="Include Details"
)
```

## Check a checkbox

```python
include_details.check()
```

`check()` first reads the native checked state. If the checkbox is already checked, nothing happens.

## Uncheck a checkbox

```python
include_details.uncheck()
```

`uncheck()` first reads the native checked state. If the checkbox is already unchecked, nothing happens.

## Read the state

```python
if include_details.is_checked():
    print("Details are included")
```

You can also set the desired state directly:

```python
include_details.set_checked(True)
include_details.set_checked(False)
```

`AppianCheckbox` inherits the shared post-change focus-out behavior from `AppianInputComponent`. It uses semantic HTML relationships such as `label[for]`, `role="group"`, and `aria-labelledby`; it does not rely on generated Appian CSS class names.

Use [`AppianRadioSelect`](appian-radio-select.md) for radio-button groups.

## API

::: robo_appian.appian.appian_checkbox.AppianCheckbox
    options:
      show_root_heading: true
      members_order: source
      members:
        - is_visible
        - is_checked
        - check
        - uncheck
        - set_checked
        - select


## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
