# Appian Page

`AppianPage` is the main page object you use when automating an Appian application.

Most application tests should start here. It gives you simple, readable component APIs such as `textbox()`, `date()`, `dropdown()`, `checkbox()`, `button()`, `dialog()`, `table()`, and `upload()`.

```python
from robo_appian import AppianPage
```

## Common usage

```python
page.textbox(label="Description").fill("Example item")
page.textbox("Employee").select(search_text="John", index=2)
page.date(label="Start Date").fill("10/15/2026")
page.dropdown(label="Status").select("General")
page.checkbox(label="Include Details").check()
page.radio(
    label="Priority"
).select("High")
page.button(name="Next").click()
```

Think about the page the same way an end user does: identify the visible field or button text, then choose the matching `AppianPage` component helper.


## Upload documents

Use `upload()` to add a document to an Appian upload field.

```python
page.upload("documents/receipt.pdf")
```

When a page has more than one upload field, identify the required field by its displayed label:

```python
page.upload(
    "documents/receipt.pdf",
    label="Supporting Document",
)
```

Multiple documents can be supplied together when the field supports multiple files:

```python
page.upload([
    "documents/receipt.pdf",
    "documents/approval.pdf",
])
```

The upload action waits for Appian processing to complete before continuing.

## Dialogs

Use `dialog()` to scope interactions to an Appian modal by its accessible name. Components inside the dialog use the same fluent APIs as page-level components.

```python
dialog = page.dialog(name="Confirm Action")
dialog_by_text = page.dialog(text="Are you sure", visible=None)
dialog.button("Confirm").click()
```

Dialog collection indexing is zero-based, consistent with other component collections:

```python
page.dialog[0].button("Confirm").click()
```

## Exact matching and visibility

robo-appian uses `exact=True` and `visible=True` by default. This means it normally chooses a visible component whose displayed name or label exactly matches the value you provide. Use `exact=False` only when a partial match is intentional, and change `visible` only when the business scenario requires it.

```python
page.link(name="Return")  # exact=True, visible=True
page.link(name="RETURN TO", exact=False)
page.link(name="Return", visible=False)
page.grid(label="Items", visible=None)  # visible and hidden tables
```

For `AppianGrid`, at least one of `label`, `header`, `row_name`, or `column_name` is required.

## Semantic filtering and zero-based indexing

Each short component accessor can be called with semantic identifiers or indexed as a collection. Filtering can be followed by indexing when multiple matching components exist. Component indexes are normal zero-based Python indexes.

```python
page.dropdown[0].select(value="Active")
page.dropdown(label="Status")[0].select(value="Active")
page.button(name="Edit", exact=True)[1].click()
```

This component index is separate from APIs with their own domain indexing. For example, dropdown option `index=1` means the first real option (excluding `Select a Value`), while `page.dropdown[0]` means the first dropdown component.

## Wait for Appian processing

Use `wait_for_appian_action_completed()` when the next step must wait until Appian has finished its global processing. The default uses the configured framework timeout (`WAIT_TIME`). Pass `timeout` to override that wait in seconds for this call.

```python
page.wait_for_appian_action_completed()
page.wait_for_appian_action_completed(timeout=8)
```

The method returns when Appian's global processing indicators are absent. If processing continues beyond the allowed timeout, the normal automation timeout error is raised.

## Wait for visible text

Use `wait_for_text_visible()` when the next step depends on text becoming visible. Matching is exact by default. The default timeout uses the configured framework timeout (`WAIT_TIME`); pass `timeout` in seconds to override it for the call.

```python
page.wait_for_text_visible("Ready")
page.wait_for_text_visible("Processing complete", timeout=8)
page.wait_for_text_visible("partial message", exact=False)
```

For operations inside a dialog, region, or smaller part of the page, use [`AppianLocator`](appian-locator.md).

## API

::: robo_appian.appian.page.appian_page.AppianPage
    options:
      show_root_heading: true
      members_order: source
      members:
        - upload
        - wait_for_text_visible
        - wait_for_appian_action_completed
        - button
        - dialog
        - textbox
        - dropdown
        - checkbox
        - radio
        - link
        - tab
        - date
        - table

## Per-component timeout

Every component accepts `timeout` in seconds. Leave it as `None` to use the normal configured wait time, or provide a positive value when that component needs a different wait time.

```python
page.dropdown(label="Status", timeout=10).select(value="Active")
page.textbox(label="Description", timeout=5).fill("Test")
page.button(name="Submit", timeout=10).click()
```
