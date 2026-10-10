# Core Concepts

You only need a few ideas to start using `robo-appian`.

## Think like the user

Prefer visible application text over low-level HTML selectors.

```python
page.textbox(label="Description").fill("Example item")
page.button(name="Next").click()
```

## `page` is your main entry point

`page` is an `AppianPage`. It provides Appian-aware components such as:

```python
page.textbox(...)
page.date(...)
page.checkbox(...)
page.radio(...)
page.button(...)
```

## Components do the Appian-specific work

For example, a date input is still an Appian control even though it looks like a textbox in HTML. Use:

```python
page.date(label="Start Date").fill("10/15/2026")
```

instead of treating it as a normal textbox.

Textboxes, dates, and selection controls automatically move focus out after a value changes so Appian can process the update.

## Only use lower-level locators when necessary

Most tests should start with the component APIs above. If the application has a control that cannot be described that way, `AppianPage` and `AppianLocator` also provide lower-level lookup methods. Those are covered in the API and advanced guides.

## Where responsibilities live

| Concern | Owner |
| --- | --- |
| Browser and pytest lifecycle | `robo-automation` |
| Appian controls and Appian behavior | `robo-appian` |
| Application URL, login, workflow and test data | Consumer project |

For a first test, continue to [Quick Start](quick-start.md).
