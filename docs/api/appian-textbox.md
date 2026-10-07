# Appian Textbox

Use `AppianPage.textbox(...)` to work with a text field by its label or placeholder.

```python
textbox = page.textbox(label="Title")
textbox.fill("Example request")
```

A placeholder can be used when that is the natural identifier for the field:

```python
page.textbox(placeholder="example@example.com").fill("user@example.com")
```

Common operations include `fill()`, `clear()`, `click()`, `is_visible()`, `is_enabled()`, `is_disabled()`, `value()`, and `wait_until_ready()`.

::: robo_appian.appian.appian_textbox.AppianTextbox
    options:
      show_root_heading: true
      members_order: source
