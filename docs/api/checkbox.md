# Checkbox

The legacy static `CheckBox` helper has been removed. Use [`AppianCheckbox`](appian-checkbox.md) through `AppianPage.appian_checkbox(...)`.

```python
page.appian_checkbox(
    label="Vendor is missing in approved list"
).check()
```

For radio-button groups, use [`AppianRadioSelect`](appian-radio-select.md) through `page.appian_radio(...)`.
