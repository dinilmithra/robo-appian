# API Reference

`robo-appian`'s public API is the Appian component/utility layer. Generic browser/resource wrappers are provided by the dependency `robo-automation` and are shown here only as integration context.

## Appian resource API

Prefer package-root Appian imports in consumers:

```python
from robo_appian import AppianLocator, AppianPage, AppianScope
```

| Type | Responsibility |
| --- | --- |
| [`AppianPage`](appian-page.md) | Appian page abstraction and fluent component entry point |
| `AppianLocator` | Appian locator specialization used for scoped/subtree operations |
| [`AppianScope`](appian-scope.md) | `AppianPage | AppianLocator` for APIs that intentionally accept both |

The generic Robo* inheritance layer belongs to `robo-automation` and is not the preferred consumer API for Appian projects.

## Pytest Integration

- [Pytest Integration](../guides/pytest-integration.md) — `robo-automation` fixture ownership and extension points

## Component API

The package also exposes reusable Appian component helpers:

```python
from robo_appian import AppianPage, Dropdown, Table
```

Component pages are generated from current source signatures/docstrings.

| Component | Use it for |
| --- | --- |
| [`AppianButton`](appian-button.md) | Appian button interactions through `AppianPage.button(...)` |
| [`CheckBox`](checkbox.md) | Checkbox state/actions |
| [`Dropdown`](dropdown.md) | Standard dropdowns |
| [`AppianDate`](appian-date.md) | Appian date fields |
| [`Link`](link.md) | Links |
| [`MenuButton`](menu-button.md) | Menu-button actions |
| `AppianPage.checkbox(...)` | Checkboxes and labeled radio groups |
| [`RecordList`](record-list.md) | Repeated record content |
| [`Region`](region.md) | Named regions/scoping |
| [`SearchDropdown`](search-dropdown.md) | Searchable dropdowns |
| [`SearchInput`](search-input.md) | Search suggestions |
| [`Tab`](tab.md) | Tabs |
| [`Table`](table.md) | Tables/grids |
| [`ComponentUtils`](component-utils.md) | Shared lower-level component utilities |

## Compatibility note

Some older non-button component helpers still expose the lower-layer generic `Scope` type in generated signatures. New Appian APIs should use `AppianPage`, `AppianLocator`, or `AppianScope`.

## Appian input textbox

Create a text field from `AppianPage` by label, placeholder, or nearby header text:

```python
page.textbox(label="Title").fill("Example request")
page.textbox(placeholder="example@example.com").fill("user@example.com")
page.textbox(header="Conference Description").fill("General conference details")
page.date(label="Required Award Date").fill("10/07/2026")
```

See [Appian Textbox](appian-textbox.md).
