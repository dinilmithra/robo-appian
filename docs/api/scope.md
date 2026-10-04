# Scope

`Scope` tells `robo-appian` **where to search for an Appian component**.

A `Scope` is not a new browser object created by `robo-appian`. It is one of two
objects from Playwright:

```python
from typing import Union
from playwright.sync_api import Locator, Page

Scope = Union[Page, Locator]
```

| Object used as `scope` | What robo-appian searches | Use it when |
| --- | --- | --- |
| Playwright `Page` | The entire current document | The target control is unique on the page, or you want normal page-wide lookup. |
| Playwright `Locator` | Only the DOM subtree represented by that locator | Labels or controls repeat, or you intentionally want to restrict lookup to a form, region, dialog, row, or other container. |

!!! important "What does the `scope` parameter mean?"
    Whenever a robo-appian method shows `scope: Scope`, pass either a Playwright
    `Page` object or a Playwright `Locator` object. Passing a `Page` searches the
    whole page. Passing a `Locator` limits the component search to that locator.

## Using a Playwright `Page` as the scope

Most tests start with the Playwright `Page` supplied by the test framework. That
object can be passed directly to robo-appian:

```python
from playwright.sync_api import Page
from robo_appian import Button, InputText


def create_request(scope: Page):
    InputText.fill_by_label(scope, "Request Name", "Example Request")
    Button.click(scope, "Submit")
```

In this example, `scope` is a Playwright `Page`, so `robo-appian` searches the
entire document for `Request Name` and `Submit`.

## Using a Playwright `Locator` as the scope

If the page contains repeated controls, create a Playwright `Locator` for the
specific container and pass that locator as `scope`:

```python
from playwright.sync_api import Locator, Page
from robo_appian import Button, InputText


def update_request(scope: Page):
    form_scope: Locator = scope.get_by_role("region", name="Request Details")

    InputText.fill_by_label(form_scope, "Name", "Example Request")
    Button.click(form_scope, "Save")
```

Here, `form_scope` is a Playwright `Locator`. `robo-appian` searches only inside
the `Request Details` region. A `Name` or `Save` control elsewhere on the page is
outside this lookup boundary.

## Page and Locator use the same robo-appian API

You do not call a different robo-appian method for a locator-scoped interaction.
The first argument changes from a Playwright `Page` to a Playwright `Locator`:

```python
# Page scope: search the whole document.
Button.click(scope, "Save")

# Locator scope: search only inside Request Details.
request_scope = scope.get_by_role("region", name="Request Details")
Button.click(request_scope, "Save")
```

This is why the public API uses the name `scope` instead of `page`: a `Page` is
valid, but it is not the only valid search boundary.

## Choosing the right scope

Use a Playwright `Page` when the control is unique and page-wide lookup is clear.
Use a Playwright `Locator` when you need to disambiguate repeated controls or
keep an interaction inside a meaningful application container. Prefer the
narrowest stable scope that clearly represents the part of the UI your workflow
is interacting with.

::: robo_appian.utils.types.Scope
    options:
      heading_level: 2
      members_order: source
      show_source: false
