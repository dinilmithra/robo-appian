# Appian Text

Use `page.text(...)` to read or verify text that a business user can see on an Appian page.

```python
message = page.text("Request submitted successfully")

assert message.value == "Request submitted successfully"
```

Matching is exact and visible by default. Use `exact=False` when the displayed text intentionally contains additional content.

```python
status = page.text("Approved", exact=True)
assert status.is_visible()
```

## Multiple matches

Text matches preserve the order displayed by Appian. If the same text appears more than once, select the result with normal zero-based Python indexing or `.first`:

```python
approved = page.text("Approved")

approved[0].value
approved[1].value
approved.first.value
```

Direct `.value` is convenient when exactly one text match exists. If multiple matches exist, choose one explicitly.

## Waiting for text

```python
page.text("Request saved").wait_until_visible()
page.text("Request saved").wait_until_hidden()
```

An optional timeout is expressed in seconds:

```python
page.text("Request saved", timeout=10).wait_until_visible()
```

If the text does not appear in time, `wait_until_visible()` raises
`RoboAppianTimeoutError` with the text and effective timeout.

`page.text(...)` is intended for read-only displayed text. Use `page.textbox(...)` when the BA needs to enter or select a value in a text field, and use `page.dataset(...)` for structured label/value, list, or grid data.
