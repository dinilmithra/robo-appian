# Appian Menu

Describe a path with `menu(name=...)`, then click the final item:

```python
page.menu(name="CORE Admin Console").menu(name="CORE User Hub").click(
    opens_new_page=False
)
```

Building the chain does not click the page. `click()` opens each ancestor as
needed and clicks the final item once. It defaults to `opens_new_page=False`.
This skips popup waiting; it does not override the application's link target.

For application switches that open another tab, request and use the new page:

```python
user_hub_page = (
    page.menu(name="CORE Admin Console")
    .menu(name="CORE User Hub")
    .click(opens_new_page=True)
)
```

With `opens_new_page=True`, a popup is required. Its DOM must load before the
method returns an `AppianPage`. A missing popup, failed click, or load failure
raises an error. With `False`, the method waits for Appian processing to finish
and returns the current `AppianPage`.

Sign out through the same API:

```python
page.menu(name="User options").menu(name="Sign Out").click(opens_new_page=False)
```

Nested paths and 1-based option indexes work the same way:

```python
page.menu(name="Administration").menu(name="User Management").menu(name="Users").click()
page.menu(name="CORE Admin Console").menu(index=1).click(opens_new_page=True)
```

Use `open()` or `options()` to inspect a menu:

```python
page.menu(name="User options").open()
choices = page.menu(name="User options").options()
```

`is_visible()` checks the currently rendered item without opening any part of
the path. Menu triggers support native buttons and explicit button roles,
including the captured Appian profile-menu anchor. Profile actions are resolved
by accessible name inside their named dialog; application switch choices use
the option role. Exact name matching is the default; root `exact=False` applies
to the whole path. Visibility and timeout settings also apply to the whole path.
