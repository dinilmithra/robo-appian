# Your First Test

A pytest test is just a Python function whose name starts with `test_`.

```python
from robo_appian import AppianPage


def test_create_request(page: AppianPage) -> None:
    page.textbox(label="Request Name").fill("Example Request")
    page.button(name="Submit").click()
```

## What is `page`?

You do not create `page` yourself. pytest provides it to the test automatically.

`page` represents the Appian page you are automating.

## Add more fields

```python

def test_create_request(page: AppianPage) -> None:
    page.textbox(label="Request Name").fill("Example Request")

    page.date(
        label="Required Award Date"
    ).fill("10/15/2026")

    page.radio(
        label="Is this request for a conference?"
    ).select("Yes")

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
