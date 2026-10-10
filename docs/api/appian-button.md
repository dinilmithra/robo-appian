# AppianButton

`AppianButton` is the fluent button component returned by `AppianPage.button(...)`.

```python
button = page.button(name="Save")
button.click()
```

::: robo_appian.appian.AppianButton

Use the fluent component to interact with Appian buttons and query their state through methods such as `click()`, `is_visible()`, `is_enabled()`, and `is_disabled()`.

## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
