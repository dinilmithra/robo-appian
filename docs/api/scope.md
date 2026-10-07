# Legacy Scope compatibility

Some older non-button component helpers still use the generic `Scope` type supplied by `robo-automation`. This page documents that compatibility surface only.

For new Appian APIs, use [`AppianPage`](appian-page.md), `AppianLocator`, or [`AppianScope`](appian-scope.md):

```python
AppianScope = AppianPage | AppianLocator
```

Prefer `AppianPage` when an operation is page-wide. Use `AppianLocator` only when the operation must be restricted to a dialog, region, or other subtree.

The generated API signature for an older component remains authoritative until that component is migrated.
