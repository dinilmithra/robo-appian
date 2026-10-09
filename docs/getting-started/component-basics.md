# Choosing a Component

Start with what the user sees on the page.

| I need to... | Use |
| --- | --- |
| Enter text | `page.appian_textbox(...)` |
| Enter a date | `page.appian_date(...)` |
| Check or uncheck a checkbox | `page.appian_checkbox(...).check()` / `.uncheck()` |
| Choose a radio option | `page.appian_radio(...).select(...)` |
| Click a button | `page.appian_button(...).click()` |
| Choose a standard dropdown value | `Dropdown` |
| Search in a searchable dropdown | `SearchDropdown` |
| Select a tab | `Tab` |
| Work with a table/grid | `Table` |
| Click a link | `Link` |

## Textbox

By label:

```python
page.appian_textbox(label="Request Name").fill("Example Request")
```

By placeholder:

```python
page.appian_textbox(placeholder="example@example.com").fill("user@example.com")
```

Some Appian forms introduce a textbox with nearby heading text instead of a normal field label:

```python
page.appian_textbox(header="Conference Description").fill("Annual conference")
```

## Date

```python
page.appian_date(label="Required Award Date").fill("10/15/2026")
```

Use `page.appian_date(...)` for an Appian date field. Do not use a normal textbox just because the HTML input type is `text`.


## Checkbox

`page.appian_checkbox(...)` returns an [`AppianCheckbox`](../api/appian-checkbox.md).

```python
missing_vendor = page.appian_checkbox(
    label="Vendor is missing in approved list"
)
missing_vendor.check()
```

Use `uncheck()` to clear it and `is_checked()` to read the state. Both `check()` and `uncheck()` are idempotent.

## Radio choice / selection

`page.appian_radio(...)` returns an [`AppianRadioSelect`](../api/appian-radio-select.md).


```python
page.appian_radio(
    label="Is this request for a conference?"
).select("Yes")
```

Use the **complete question text** when possible. This keeps choices such as `Yes` or `No` scoped to the correct question.

You can inspect the current state without changing focus:

```python
selected = page.appian_radio(
    label="Is this request for a conference?"
).is_selected("Yes")
```

## Button

```python
page.appian_button(name="Next").click()
```

## Automatic focus-out

After a textbox, date, or selection value actually changes, `robo-appian` moves focus out automatically so Appian can process the value.

You normally should **not** add a Tab press or manual blur in application tests.

## Advanced locators

If none of the component APIs describe the control, use `AppianPage`/`AppianLocator` or a component-specific advanced API. See the API Reference after trying the simple component approach first.
