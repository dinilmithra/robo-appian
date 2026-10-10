# Checkbox

The legacy static `CheckBox` helper has been removed. Use [`AppianCheckbox`](appian-checkbox.md) through `AppianPage.checkbox(...)`.

```python
page.checkbox(
    label="Include Details"
).check()
```

For radio-button groups, use [`AppianRadioSelect`](appian-radio-select.md) through `page.radio(...)`.
