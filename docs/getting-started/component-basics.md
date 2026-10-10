# Choosing a Component

Start with what the user sees on the page.

| I need to... | Use |
| --- | --- |
| Enter text | `page.textbox(...)` |
| Enter a date | `page.date(...)` |
| Check or uncheck a checkbox | `page.checkbox(...).check()` / `.uncheck()` |
| Choose a radio option | `page.radio(...).select(...)` |
| Click a button | `page.button(...).click()` |
| Choose a standard dropdown value | `AppianDropdown` |
| Search in a searchable dropdown | `AppianDropdown` with `search_text` |
| Click an Appian link | `AppianLink` via `page.link(...)` |
| Select an Appian tab | `AppianTab` via `page.tab(...)` |
| Work with a table/grid | `AppianTable` |
| Click a link | `AppianLink` |

## Textbox

By label:

```python
page.textbox(label="Request Name").fill("Example Request")
```

By placeholder:

```python
page.textbox(placeholder="example@example.com").fill("user@example.com")
```

Some Appian forms introduce a textbox with nearby heading text instead of a normal field label:

```python
page.textbox(header="Conference Description").fill("Annual conference")
```

## Date

```python
page.date(label="Required Award Date").fill("10/15/2026")
```

Use `page.date(...)` for an Appian date field. Do not use a normal textbox just because the HTML input type is `text`.


## Checkbox

`page.checkbox(...)` returns an [`AppianCheckbox`](../api/appian-checkbox.md).

```python
missing_vendor = page.checkbox(
    label="Vendor is missing in approved list"
)
missing_vendor.check()
```

Use `uncheck()` to clear it and `is_checked()` to read the state. Both `check()` and `uncheck()` are idempotent.

## Radio choice / selection

`page.radio(...)` returns an [`AppianRadioSelect`](../api/appian-radio-select.md).


```python
page.radio(
    label="Is this request for a conference?"
).select("Yes")
```

Use the **complete question text** when possible. This keeps choices such as `Yes` or `No` scoped to the correct question.

You can inspect the current state without changing focus:

```python
selected = page.radio(
    label="Is this request for a conference?"
).is_selected("Yes")
```

## Appian tab

`page.link(name=...)` returns an [`AppianLink`](../api/appian-link.md) for native anchors and Appian linked-card controls.

```python
page.link(name="Open Request").click()
page.link(name="Return").click()
```

`page.tab(name=...)` returns an [`AppianTab`](../api/appian-tab.md).

```python
attendee = page.tab(name="Attendee Details")
assert attendee.is_selected()

page.tab(name="Contacts").select()
```

`select()` is idempotent. `is_selected()` reports the current accessibility state without waiting for an unselected tab to change state.

## Button

```python
page.button(name="Next").click()
```

## Automatic focus-out

After a textbox, date, or selection value actually changes, `robo-appian` moves focus out automatically so Appian can process the value.

You normally should **not** add a Tab press or manual blur in application tests.

## Advanced locators

If none of the component APIs describe the control, use `AppianPage`/`AppianLocator` or a component-specific advanced API. See the API Reference after trying the simple component approach first.
