# Appian Textbox

Use `AppianPage.appian_textbox(...)` to work with a text field by its label, placeholder, or nearby header text.

```python
textbox = page.appian_textbox(label="Title")
textbox.fill("Example request")
```

A placeholder can be used when that is the natural identifier for the field:

```python
page.appian_textbox(placeholder="example@example.com").fill("user@example.com")
page.appian_textbox(header="Conference Description").fill("General conference details")
```

Common operations include `fill()`, `clear()`, `click()`, `is_visible()`, `is_enabled()`, `is_disabled()`, `value()`, and `wait_until_ready()`.

::: robo_appian.appian.appian_textbox.AppianTextbox
    options:
      show_root_heading: true
      members_order: source
## Date fields

Use `page.appian_date(...)` for Appian date fields rather than `page.appian_textbox(...)`.

```python
page.appian_date(label="Required Award Date").fill("10/07/2026")
```

