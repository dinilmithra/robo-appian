# Appian Page

`AppianPage` is the main page object you use when automating an Appian application.

Most application tests should start here. It gives you simple, readable component APIs such as `textbox()`, `date()`, `dropdown()`, `checkbox()`, `button()`, and `table()`.

```python
from robo_appian import AppianPage
```

## Common usage

```python
page.textbox(label="Description").fill("Example item")
page.date(label="Start Date").fill("10/15/2026")
page.dropdown(label="Status").select("General")
page.checkbox(label="Include Details").check()
page.radio(
    label="Priority"
).select("High")
page.button(name="Next").click()
```

Think about the page the same way an end user does: identify the visible field or button text, then choose the matching `AppianPage` component helper.

## Exact matching and visibility

Appian component factories use `exact=True` and `visible=True` by default. `exact=True` requires the complete normalized semantic label/name to match; pass `exact=False` when a partial match is intentional. `visible=False` targets hidden matches, while `visible=None`, `visible=""`, or a whitespace-only string removes visibility filtering.

```python
page.link(name="Return")  # exact=True, visible=True
page.link(name="RETURN TO", exact=False)
page.link(name="Return", visible=False)
page.table(label="Items", visible=None)  # visible and hidden tables
```

For `AppianTable`, at least one of `label`, `header_name`, `row_name`, or `column_name` is required.

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

::: robo_appian.appian.appian_page.AppianPage
    options:
      show_root_heading: true
      members_order: source
      members:
        - wait_for_text_visible
        - wait_for_appian_action_completed
        - button
        - textbox
        - dropdown
        - checkbox
        - radio
        - link
        - tab
        - date
        - table

## Per-component timeout

Every semantic component factory accepts `timeout` in seconds. The default `None` leaves the framework `WAIT_TIME` timeout unchanged; a positive finite value overrides it for that component.

```python
page.dropdown(label="Status", timeout=10).select(value="Active")
page.textbox(label="Description", timeout=5).fill("Test")
page.button(name="Submit", timeout=10).click()
```
