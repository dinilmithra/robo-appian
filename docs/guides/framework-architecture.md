# Framework Architecture

`robo-appian` is the Appian-specific layer between generic browser automation and application tests.

```text
consumer application / tests
        ↓
robo-appian
AppianPage → AppianLocator → Appian components
        ↓
robo-automation
generic browser and page lifecycle
```

## Appian resource model

### `AppianPage`

`AppianPage` is the primary page abstraction for Appian consumers. It provides the page-level API used by tests and reusable components.

### `AppianLocator`

`AppianLocator` represents a scoped Appian element or subtree and is used when an interaction must be constrained to part of a page.

### `AppianScope`

`AppianScope = AppianPage | AppianLocator` is available for reusable Appian APIs that genuinely accept either a whole page or a scoped subtree. Prefer `AppianPage` when locator scoping is not needed.

## Ownership

`robo-automation` owns generic browser/context/page lifecycle. `robo-appian` owns Appian-specific page, locator, and component behavior. Consumer projects own application-specific authentication, navigation, test data, and business workflows.
