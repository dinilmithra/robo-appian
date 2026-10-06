# Scope

`Scope` is the compatibility/search-boundary type used by the existing component layer:

```python
Scope = Page | Locator
```

It is a Playwright implementation type, not a separate robo-appian object.

## How Scope fits with the Robo* wrappers

New consumer lifecycle code should normally receive `RoboPage` from the `robo-automation` pytest plugin and use `RoboLocator` for generic element lookup.

The component layer still uses `Scope` in many generated signatures because those components directly implement Playwright search mechanics internally. This boundary is retained for compatibility while the framework wrapper migration continues.

```text
consumer resource ownership
    Browser -> RoboBrowserContext -> RoboPage -> RoboLocator

component implementation compatibility
    Scope = Playwright Page | Locator
```

## Playwright `Page` scope

A `Page` searches the entire current document.

```python
InputText.fill_by_label(scope, "Request Name", "Example Request")
```

## Playwright `Locator` scope

A `Locator` restricts lookup to its DOM subtree.

```python
request_scope = scope.get_by_role("region", name="Request Details")
InputText.fill_by_label(request_scope, "Name", "Example Request")
```

## Prefer wrapper-level lookup in new consumer code

For generic attribute-based interactions, avoid constructing raw Playwright scopes in the consumer project. Use `RoboPage`:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    }
)
```

That returns `RoboLocator` and keeps raw Playwright resource ownership behind `robo-automation`.

## When you see `scope` in API reference pages

Read it as **the search root for that component operation**. The generated signature is authoritative for the current implementation. A page-wide scope searches the document; a locator-backed scope narrows the operation to a container.
