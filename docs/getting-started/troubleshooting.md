# Troubleshooting

Start from what you see in the failure.

## A field cannot be found

Check the text visible on the page.

```python
page.textbox(label="Request Title")
```

If the application label changed, update the automation to use the current label.

For radio questions, use the complete question text whenever possible:

```python
page.checkbox(
    label="Are you submitting this travel request for yourself or on behalf of someone else?"
).select("For myself")
```

## A date is filled but Appian does not react

Use `page.date(...)` rather than a normal textbox:

```python
page.date(label="Required Award Date").fill("10/15/2026")
```

Focus-out is automatic. Do not add Tab just to trigger Appian validation.

## A radio option is not selected

Confirm both the full question and the visible choice text. Avoid searching globally for common values such as `Yes` or `No`.

## A button is found but cannot be clicked

Check whether the application currently shows the button as enabled. Appian button state is based on the native `disabled` state.

## The test times out

A timeout does not always mean the timeout value is too small. First check:

1. Is the expected page actually open?
2. Is the visible label text still correct?
3. Did the previous action finish successfully?
4. Is the control enabled/visible?

Increase a timeout only when the evidence shows that the application is genuinely slow.

## Playwright says another element intercepts pointer events

This means Playwright found the target but another visible element is receiving the click. For supported Appian radio controls, `robo-appian` handles the associated label interaction internally. If you see this elsewhere, inspect the current UI rather than forcing the click immediately.

## Need more detail?

The consumer project may collect logs, screenshots, HTML and browser diagnostics. Use those artifacts to see the actual page state at the time of failure.
