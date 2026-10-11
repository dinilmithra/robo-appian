# AppianButton

`AppianButton` represents a button selected with `page.button(...)`.

```python
button = page.button(name="Save")
button.click()
```

::: robo_appian.appian.AppianButton
    options:
      show_root_heading: true
      members_order: source
      members:
        - click
        - is_visible
        - is_disabled
        - is_enabled
        - wait_until_ready
        - wait_until_hidden

Use the button to perform actions and check its state through methods such as `click()`, `is_visible()`, `is_enabled()`, and `is_disabled()`.

## Exact matching and visibility

By default, robo-appian uses a visible component whose displayed name or label exactly matches what you provide. Keep `exact=True` and `visible=True` for normal business automation. Use `exact=False` only when you intentionally want a partial name or label match. Change `visible` only when your scenario specifically requires a component that is not currently visible.


## Timeout

`timeout` is expressed in seconds. Leave `timeout=None` to use the normal configured wait time, or provide a positive value when this particular action needs a different wait time.
