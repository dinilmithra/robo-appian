# AppianPage

`AppianPage` is the main page object you use when automating an Appian application.

Most application tests should start here. It gives you simple, readable component APIs such as `textbox()`, `date()`, `checkbox()`, and `button()`.

```python
from robo_appian import AppianPage
```

## Common usage

```python
page.textbox(label="Request Title").fill("Office Supplies")
page.date(label="Required Award Date").fill("10/15/2026")
page.checkbox(label="Vendor is missing in approved list").check()
page.radio(
    label="Is this request for a conference?"
).select("Yes")
page.button(name="Next").click()
```

Think about the page the same way an end user does: identify the visible field or button text, then choose the matching `AppianPage` component helper.

## Visible text

Use `page.get_by_text("...")` when you need rendered text that is not represented by one of the component helpers.

```python
message = page.get_by_text("Request submitted")
```

For operations inside a dialog, region, or smaller part of the page, use [`AppianLocator`](appian-locator.md).

## API

::: robo_appian.appian.appian_page.AppianPage
    options:
      show_root_heading: true
      members_order: source
