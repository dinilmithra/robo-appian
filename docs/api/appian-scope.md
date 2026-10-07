# AppianScope

`AppianScope` is the Appian-only search boundary:

```python
AppianScope = AppianPage | AppianLocator
```

Application code should prefer `AppianPage` whenever the operation is page-level. Use `AppianLocator` only when an operation must be restricted to a dialog, region, or other subtree.
