# Your First Test

A pytest test is just a Python function whose name starts with `test_`.

```python
from robo_appian import AppianPage


def test_update_item(page: AppianPage) -> None:
    page.textbox(label="Description").fill("Example item")
    page.button(name="Submit").click()
```

## What is `page`?

You do not create `page` yourself. pytest provides it to the test automatically.

`page` represents the Appian page you are automating.

## Add more fields

```python

def test_update_item(page: AppianPage) -> None:
    page.textbox(label="Description").fill("Example item")

    page.date(
        label="Start Date"
    ).fill("10/15/2026")

    page.radio(
        label="Priority"
    ).select("High")

    page.button(name="Submit").click()
```

Prefer the label or button text a real user sees on the screen.

## Application-specific behavior

Your application project should normally own:

- the application URL;
- login and credentials;
- business workflows;
- test data;
- assertions.

`robo-appian` supplies reusable Appian interactions. `robo-automation` supplies generic browser and pytest infrastructure.
