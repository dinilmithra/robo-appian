# Appian Textbox

Use `AppianPage.textbox(...)` to work with a text field by its label, placeholder, or nearby header text.

```python
textbox = page.textbox(label="Title")
textbox.fill("Example request")
```

A placeholder can be used when that is the natural identifier for the field:

```python
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.textbox(header="Item Description").fill("General details")
```

`fill()` returns the same textbox, so searchable text fields can use a fluent fill-and-select flow. Searchable fields are detected from semantic input/ARIA attributes; no CSS class names are used.

```python
page.textbox("Employee").fill("John").select("John Smith")
page.textbox("Employee").fill("John").select(index=2)
```

The same operation can be expressed in one call. Suggestion `index` values are 1-based.

```python
page.textbox("Employee").select(search_text="John", value="John Smith")
page.textbox("Employee").select(search_text="John", index=2)
page.textbox(placeholder="Start typing...").select(
    search_text="Example", value="Example Result"
)
```

`value` and `index` are mutually exclusive. `search_text` is optional when `fill()` has already entered the search criteria.

Common operations include `fill()`, `select()`, `clear()`, `click()`, `is_visible()`, `is_enabled()`, `is_disabled()`, `value()`, and `wait_until_ready()`.

::: robo_appian.appian.appian_textbox.AppianTextbox
    options:
      show_root_heading: true
      members_order: source
      members:
        - fill
        - select
        - clear
        - click
        - is_visible
        - is_disabled
        - is_enabled
        - value
        - wait_until_ready
## Date fields

Use `page.date(...)` for Appian date fields rather than `page.textbox(...)`.

```python
page.date(label="Start Date").fill("10/07/2026")
```


## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
