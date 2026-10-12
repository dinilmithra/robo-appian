# Appian Menu

Use `page.menu(...)` when the page presents a business menu with choices.

```python
page.menu("CORE Admin Console").select("CORE User Hub")
```

For a nested menu, chain `menu(...)` until the final choice:

```python
page.menu("Administration") \
    .menu("User Management") \
    .select("Users")
```

A menu option can also be selected by its **1-based** displayed position:

```python
page.menu("CORE Admin Console").select(index=1)
```

Use `options()` when the test needs to read the currently available choices:

```python
choices = page.menu("CORE Admin Console").open().options()
```
