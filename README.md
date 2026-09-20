# robo-appian

Reusable Playwright component helpers for Appian applications.

This package intentionally contains only generic Appian interaction behavior.
Application-specific labels, workflows, waits, and business rules belong in the
consuming application's facade layer.

For local CORE development the sibling `core-automation` project references this
package with a Poetry path dependency:

```toml
robo-appian = { path = "../robo-appian", develop = true }
```
