# AppianTab

`AppianTab` represents an Appian linked-card tab. Create it from `AppianPage` with `page.tab(...)`.

```python
details = page.tab(name="Details")

assert details.is_selected()

page.tab(name="Contacts").select()
```

## Select and check a tab

`select()` selects the requested tab. If it is already selected, no additional action is performed.

Use `is_selected()` when the business flow needs to verify the active tab:

```python
page.tab(name="Contacts").select()
assert page.tab(name="Contacts").is_selected()
```

::: robo_appian.appian.components.appian_tab.AppianTab
    options:
      show_root_heading: true
      members_order: source
      members:
        - is_visible
        - is_selected
        - select

## Exact matching and visibility

By default, robo-appian uses a visible component whose displayed name or label exactly matches what you provide. Keep `exact=True` and `visible=True` for normal business automation. Use `exact=False` only when you intentionally want a partial name or label match. Change `visible` only when your scenario specifically requires a component that is not currently visible.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` uses the configured default timeout; a positive finite value overrides that timeout for waits/actions performed by the component.
