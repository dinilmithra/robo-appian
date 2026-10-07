# API Reference

`robo-appian`'s public API is the Appian component/utility layer. Generic browser/resource wrappers are provided by the dependency `robo-automation` and are shown here only as integration context.

## Appian resource API

Prefer package-root Appian imports in consumers:

```python
from robo_appian import AppianBrowserContext, AppianLocator, AppianPage, AppianScope
```

| Type | Responsibility |
| --- | --- |
| `AppianBrowserContext` | Appian context specialization that creates/tracks `AppianPage` |
| [`AppianPage`](appian-page.md) | Appian page abstraction and fluent component entry point |
| `AppianLocator` | Appian locator specialization used for scoped/subtree operations |
| [`AppianScope`](appian-scope.md) | `AppianPage | AppianLocator` for APIs that intentionally accept both |

The generic Robo* inheritance layer belongs to `robo-automation` and is not the preferred consumer API for Appian projects.

## Pytest and CLI

- [Pytest Integration](../guides/pytest-integration.md) — `robo-automation` fixture ownership and extension points
- [Command-Line Interface](cli.md) — `robo-appian` browser binary provisioning

## Component API

The package also exposes reusable Appian component helpers:

```python
from robo_appian import AppianPage, Dropdown, InputText, Table
```

Component pages are generated from current source signatures/docstrings.

| Component | Use it for |
| --- | --- |
| [`AppianButton`](appian-button.md) | Appian button interactions through `AppianPage.button(...)` |
| [`CheckBox`](checkbox.md) | Checkbox state/actions |
| [`Dropdown`](dropdown.md) | Standard dropdowns |
| [`InputDate`](input-date.md) | Date fields |
| [`InputText`](input-text.md) | Text/paragraph fields |
| [`Link`](link.md) | Links |
| [`MenuButton`](menu-button.md) | Menu-button actions |
| [`RadioSelect`](radio-select.md) | Radio options |
| [`RecordList`](record-list.md) | Repeated record content |
| [`Region`](region.md) | Named regions/scoping |
| [`SearchDropdown`](search-dropdown.md) | Searchable dropdowns |
| [`SearchInput`](search-input.md) | Search suggestions |
| [`Tab`](tab.md) | Tabs |
| [`Table`](table.md) | Tables/grids |
| [`Text`](text.md) | Visible text queries/waits |
| [`ComponentUtils`](component-utils.md) | Shared lower-level component utilities |

## Compatibility note

Some older non-button component helpers still expose the lower-layer generic `Scope` type in generated signatures. New Appian APIs should use `AppianPage`, `AppianLocator`, or `AppianScope`.

## Relationship to Playwright

```text
consumer project
      ↓
robo-appian components
      ↓
robo-automation pytest plugin / Robo* wrappers
      ↓
Playwright implementation dependency
      ↓
Appian
```

The generic wrapper/fixture stack is owned by `robo-automation`. `robo-appian` currently also declares Playwright directly because its Appian implementation and tooling use Playwright APIs.
