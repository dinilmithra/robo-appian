# Choosing a Component

Start with what the user sees on the page.

| I need to... | Use |
| --- | --- |
| Enter text | `page.textbox(...)` |
| Enter a date | `page.date(...)` |
| Choose a radio/selection option | `page.checkbox(...).select(...)` |
| Click a button | `page.button(...).click()` |
| Choose a standard dropdown value | `Dropdown` |
| Search in a searchable dropdown | `SearchDropdown` |
| Select a tab | `Tab` |
| Work with a table/grid | `Table` |
| Click a link | `Link` |

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

## Radio choice / selection

```python
page.checkbox(
    label="Is this request for a conference?"
).select("Yes")
```

Use the **complete question text** when possible. This keeps choices such as `Yes` or `No` scoped to the correct question.

You can inspect the current state without changing focus:

```python
selected = page.checkbox(
    label="Is this request for a conference?"
).is_selected("Yes")
```

## Button

```python
page.button(name="Next").click()
```

## Automatic focus-out

After a textbox, date, or selection value actually changes, `robo-appian` moves focus out automatically so Appian can process the value.

You normally should **not** add a Tab press or manual blur in application tests.

## Advanced locators

If none of the component APIs describe the control, use `AppianPage`/`AppianLocator` or a component-specific advanced API. See the API Reference after trying the simple component approach first.
