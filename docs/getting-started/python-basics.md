# Python You Need for Automation

You do not need advanced Python to start writing UI automation.

## Variables

```python
request_title = "Office Supplies"
page.appian_textbox(label="Request Title").fill(request_title)
```

## Calling a method

```python
page.appian_button(name="Next").click()
```

`page.appian_button(...)` finds the button. `.click()` performs the action.

## Functions

A pytest test is a Python function whose name normally starts with `test_`:

```python
def test_create_request(page):
    page.appian_button(name="Next").click()
```

## `if` conditions

```python
if request_type == "Conference":
    page.appian_radio(label="Is this request for a conference?").select("Yes")
```

## Dictionaries

A dictionary stores related values by name:

```python
request = {
    "title": "Office Supplies",
    "date": "10/15/2026",
}

page.appian_textbox(label="Request Title").fill(request["title"])
```

That is enough Python for many straightforward automation tasks. Learn more Python as your test logic becomes more complex.
