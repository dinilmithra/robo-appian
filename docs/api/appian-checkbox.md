# AppianCheckbox

`AppianCheckbox` represents a true Appian checkbox. Create it with `page.checkbox(...)`.

```python
missing_vendor = page.checkbox(
    label="Vendor is missing in approved list"
)
```

## Check a checkbox

```python
missing_vendor.check()
```

`check()` first reads the native checked state. If the checkbox is already checked, nothing happens.

## Uncheck a checkbox

```python
missing_vendor.uncheck()
```

`uncheck()` first reads the native checked state. If the checkbox is already unchecked, nothing happens.

## Read the state

```python
if missing_vendor.is_checked():
    print("Vendor is missing")
```

You can also set the desired state directly:

```python
missing_vendor.set_checked(True)
missing_vendor.set_checked(False)
```

`AppianCheckbox` inherits the shared post-change focus-out behavior from `AppianInputComponent`. It uses semantic HTML relationships such as `label[for]`, `role="group"`, and `aria-labelledby`; it does not rely on generated Appian CSS class names.

Use [`AppianRadioSelect`](appian-radio-select.md) for radio-button groups.
