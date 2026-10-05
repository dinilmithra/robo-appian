::: robo_appian.framework.robo_page.RoboPage
    options:
      show_root_heading: true
      heading_level: 1
      members_order: source

## Attribute-based lookup

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    },
    excat_match=True,
)
```

The result is [`RoboLocator`](robo-locator.md).

## Lookup by id

```python
agree = page.get_by_id("jsAcceptButton")
agree.to_be_visible()
agree.click()
```

## Compatibility locator methods

Methods such as `locator()`, `get_by_role()`, `get_by_text()`, and related helpers currently return Playwright locators because existing component implementations still use the locator-level compatibility boundary. Prefer `get_by_attributes()` and `get_by_id()` for new generic consumer interactions when they fit the use case.
