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

`AppianDate` inherits the common textbox operations while preserving date-specific behavior. After `fill()` changes the value, the component immediately performs focus-out so Appian can validate and process the date; tests should not press Tab for this purpose.

::: robo_appian.appian.appian_date.AppianDate

## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
