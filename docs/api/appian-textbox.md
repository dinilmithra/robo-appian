# Appian Textbox

Use `AppianPage.textbox(...)` for ordinary text entry and searchable text-entry controls. Identify a textbox by its label, placeholder, or nearby header text.

```python
textbox = page.textbox(label="Title")
textbox.fill("Example request")
```

A placeholder can be used when that is the natural identifier for the field:

```python
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.textbox(header="Item Description").fill("General details")
```

`fill(value)` replaces the current text and returns the same `AppianTextbox`, so calls can be chained. For an ordinary textbox, `fill()` performs the normal Appian focus-out and action-completion wait. For a searchable textbox, `fill()` keeps the field active so a following `select()` can choose a rendered suggestion. Searchable controls are recognized from semantic input/ARIA behavior; Appian CSS class names are not used.

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

`select(value=None, *, search_text=None, index=None, exact=True, timeout=None)` requires exactly one of `value` or `index`:

- `value` selects a visible suggestion by displayed text. Matching is exact by default; use `exact=False` for intentional partial matching.
- `index` selects by **1-based suggestion position**. `index=1` is the first visible suggestion and `index=2` is the second.
- `search_text` optionally enters the search criteria before selecting. Omit it when `fill()` has already entered the search text.
- `timeout` is expressed in seconds. `None` uses the component/framework timeout.

`value` and `index` are mutually exclusive. Calling `select()` with neither, with both, with an index below 1, or with blank search/value text raises a clear argument error. A searchable textbox with no results raises `LookupError`; an out-of-range suggestion index raises `IndexError`. After a suggestion is clicked, `select()` waits for Appian action processing to complete and returns the same textbox.

Textbox **component collection indexing remains zero-based**:

```python
page.textbox[0].fill("John").select(index=2)
```

Here `[0]` means the first textbox on the page, while `select(index=2)` means the second suggestion.

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
