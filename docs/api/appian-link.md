# AppianLink

`AppianLink` is the semantic Appian link component returned by `AppianPage.link(...)`.

It supports both Appian link shapes observed in SAIL pages:

- native `<a>` links, including rich-text page links;
- linked-card controls that expose `role="link"` without an `<a>` element.

The component identifies links by accessible/visible name through the native link role. It does not use generated Appian CSS classes.

```python
page.link(name="View Details").click()
page.link(name="Item 1001").click()
page.link(name="Item Details").click()
page.link(name="Return").click()
```

Links that belong to table rows are handled by `AppianTable`, which owns table/row/cell resolution. Do not build table-row scopes just to use `AppianLink`:

```python
table = page.table(label="Items")
table.row(name="Item 1001").cell(column_name="Owner").link(name="View").click()
```

Useful operations are:

```python
link = page.link(name="Item 1001")

link.is_visible()
link.wait_until_visible()
link.get_text()
link.href()       # None for linked-card links with no native href
link.click()
```

`click()` waits for Appian action completion after activating the link. The locator remains live, so it is re-evaluated against the current Appian DOM when used.

::: robo_appian.appian.appian_link.AppianLink
    options:
      show_source: false
      members_order: source

## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework Playwright timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
