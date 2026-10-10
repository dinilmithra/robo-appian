# Python You Need for Automation

You do not need advanced Python to start writing UI automation.

## Variables

```python
item_description = "Office Supplies"
page.textbox(label="Description").fill(item_description)
```

## Calling a method

```python
page.button(name="Next").click()
```

`page.button(...)` finds the button. `.click()` performs the action.

## Functions

A pytest test is a Python function whose name normally starts with `test_`:

```python
def test_update_item(page):
    page.button(name="Next").click()
```

## `if` conditions

```python
if item_type == "Special":
    page.radio(label="Priority").select("High")
```

## Dictionaries

A dictionary stores related values by name:

```python
item = {
    "title": "Office Supplies",
    "date": "10/15/2026",
}

page.textbox(label="Description").fill(item["title"])
```

That is enough Python for many straightforward automation tasks. Learn more Python as your test logic becomes more complex.
