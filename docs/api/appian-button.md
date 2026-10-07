# AppianButton

`AppianButton` is the fluent button component returned by `AppianPage.button(...)`.

```python
button = page.button(name="Save")
button.click()
```

::: robo_appian.appian.AppianButton

## DOM contract

Appian action buttons are identified as native `<button type="button">` elements. The component name is matched against the button's rendered or accessible label.

Button state is determined by the HTML `disabled` attribute:

- `disabled` present: the button is disabled.
- `disabled` absent: the button is enabled.

CSS classes are not used to determine enabled or disabled state.
