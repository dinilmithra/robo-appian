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

By default, robo-appian uses a visible component whose displayed name or label exactly matches what you provide. Keep `exact=True` and `visible=True` for normal business automation. Use `exact=False` only when you intentionally want a partial name or label match. Change `visible` only when your scenario specifically requires a component that is not currently visible.


## Timeout

`timeout` is expressed in seconds. Leave `timeout=None` to use the normal configured wait time, or provide a positive value when this particular action needs a different wait time.

## Identify a checkbox group by header

Use `header` when the displayed heading is the clearest way to identify the checkbox group:

```python
page.checkbox(header="More Details")
```

`header` is the displayed heading used to identify the checkbox or checkbox group.
