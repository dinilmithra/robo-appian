# AppianLink

`AppianLink` is the semantic Appian link component returned by `AppianPage.link(...)`.

Use `link(name=...)` when the business action is presented as a link. Scope repeated link names to their table row, cell, dialog, or other owning component.

```python
page.link(name="View Details").click()
page.link(name="Item 1001").click()
page.link(name="Item Details").click()
page.link(name="Return").click()
page.link(name="Dashboard").click()  # top navigation link
```

Links that belong to table rows are handled by `AppianGrid`, which owns table/row/cell resolution. Do not build table-row scopes just to use `AppianLink`:

```python
table = page.grid(label="Items")
table.row(name="Item 1001").cell(column_name="Owner").link(name="View").click()
```

Useful operations are:

```python
link = page.link(name="Item 1001")

link.is_visible()
link.wait_until_visible()
link.get_text()
link.href()       # None when the link action has no native href
link.click()
```

`click()` activates the link and waits for the resulting Appian action to complete.

::: robo_appian.appian.components.appian_link.AppianLink
    options:
      show_source: false
      members_order: source
      members:
        - is_visible
        - wait_until_visible
        - click
        - get_text
        - href

## Exact matching and visibility

By default, robo-appian uses a visible component whose displayed name or label exactly matches what you provide. Keep `exact=True` and `visible=True` for normal business automation. Use `exact=False` only when you intentionally want a partial name or label match. Change `visible` only when your scenario specifically requires a component that is not currently visible.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` uses the configured default timeout; a positive finite value overrides that timeout for waits/actions performed by the component.

## Identify a link by header

```python
page.link(header="View Details").click()
```

`header` is the displayed heading used to identify the link when that is the clearest business-facing name.


### Appian linked cards

`page.link(name="...")` also supports Appian linked cards. robo-appian finds the requested visible business text using the normal `exact` rule, then resolves the nearest parent link component (`role="link"`) and performs the action on that component. This lets a BA use the displayed card title even when Appian adds descriptive text to the card. `exact=True` remains an exact visible-text match; use `exact=False` only for intentional partial text matching.
