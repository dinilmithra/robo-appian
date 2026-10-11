# Writing a Business Flow

This is the recommended starting point for a Business Analyst creating Appian automation.

A test should read like the business steps it protects. Use `robo-appian` for the controls a user sees and `robo-automation` for the test runtime, configuration, and diagnostics behind the test.

## Start from the business scenario

Write the main business path as a short sequence of user actions and expected outcomes. For example:

1. Enter request details.
2. Choose a requester from a searchable field.
3. Select a date and status.
4. Submit the request.
5. Verify the confirmation is visible.

Then translate those steps directly into component calls:

```python
from robo_appian import AppianPage


def test_submit_request(page: AppianPage) -> None:
    page.textbox("Request Title").fill("Example request")
    page.textbox("Employee").select(
        search_text="John",
        value="John Smith",
    )
    page.date("Start Date").fill("10/15/2026")
    page.dropdown("Status").select("Ready")
    page.button("Submit").click()
    page.wait_for_text_visible("Request submitted", exact=True)
```

The intent should be understandable without knowing the page HTML.

## Choose components by what the user sees

Prefer the Appian component that matches the business control:

```python
page.textbox("Description").fill("Example")
page.date("Start Date").fill("10/15/2026")
page.dropdown("Status").select("Active")
page.radio("Priority").select("High")
page.checkbox("Approved").check()
page.button("Continue").click()
page.link("View Details").click()
```

For a searchable text field, keep using `textbox`:

```python
page.textbox("Employee").fill("John").select("John Smith")
page.textbox("Employee").fill("John").select(index=2)
```

Suggestion indexes are 1-based. Component collection indexes such as `page.textbox[0]` are zero-based.

## Prefer business names over technical selectors

Use labels, button names, link text, table headers, dialog names, and placeholders whenever possible. Avoid raw HTML/CSS selectors in business tests.

For an unlabeled searchable textbox, a placeholder is appropriate:

```python
page.textbox(
    placeholder="Start typing reference number..."
).select(
    search_text=reference_number,
    value=reference_number,
)
```

## Let Appian components handle synchronization

Normal component actions already perform the Appian synchronization required by the library. Do not add arbitrary sleeps after every action.

Use explicit waits when the business flow itself requires waiting for a visible result:

```python
page.wait_for_text_visible("Request submitted", exact=True)
```

## Keep test data separate from the flow

When values vary by environment or scenario, pass them into the business flow rather than burying them in locator code. This keeps the test readable and reusable.

## What `robo-automation` does for you

`robo-automation` supports the test execution environment, while the business flow itself is written with the `robo-appian` component APIs shown in this guide.

Use its documentation when you need to understand test execution, configuration, fixtures, or failure evidence. For Appian page interactions, stay with `robo-appian` whenever possible.

## Next steps

- [Choosing a Component](component-basics.md)
- [Component Recipes](../guides/components.md)
- [Your First Test](first-test.md)
- [Troubleshooting](troubleshooting.md)
