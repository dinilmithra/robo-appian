# Appian Date

Use `AppianPage.date(...)` for Appian date fields. A date can be identified by its label, placeholder, or nearby header text.

```python
page.date(label="Start Date").fill("10/07/2026")
```

```python
page.date(placeholder="mm/dd/yyyy").fill("10/07/2026")
```

```python
page.date(header="Start Date").fill("10/07/2026")
```

`AppianDate` inherits the common textbox operations while preserving date-specific behavior. After `fill()` changes the value, the component immediately performs focus-out and then waits for Appian action processing to complete. Tests should not press Tab or add a separate completion wait for this purpose.

::: robo_appian.appian.components.appian_date.AppianDate
    options:
      show_root_heading: true
      members_order: source
      members:
        - normalize
        - fill
        - fill_locator

## Exact matching and visibility

By default, robo-appian uses a visible component whose displayed name or label exactly matches what you provide. Keep `exact=True` and `visible=True` for normal business automation. Use `exact=False` only when you intentionally want a partial name or label match. Change `visible` only when your scenario specifically requires a component that is not currently visible.


## Timeout

`timeout` is expressed in seconds. Leave `timeout=None` to use the normal configured wait time, or provide a positive value when this particular action needs a different wait time.
