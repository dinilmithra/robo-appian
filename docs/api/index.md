# API Reference

`robo-appian`'s public API is the Appian component/utility layer. Generic browser/resource wrappers are provided by the dependency `robo-automation` and are shown here only as integration context.

## Generic framework dependency (`robo-automation`)

Prefer package-root imports:

```python
from playwright.sync_api import Browser
from robo_automation import RoboBrowserContext, RoboPage, RoboLocator
```

| Class | Responsibility |
| --- | --- |
| Playwright `Browser` | Used directly by the public `browser` fixture |
| [`RoboBrowserContext`](robo-browser-context.md) | Context-level wrapper; creates and tracks `RoboPage` |
| [`RoboPage`](robo-page.md) | Page-level wrapper; navigation and page-level element lookup |
| [`RoboLocator`](robo-locator.md) | Element wrapper; actions, visibility filtering, attribute waits, nested selection |

Typical flow:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    },
    excat_match=True,
)
user_options.to_be_visible()
user_options.click()
```

## Pytest and CLI

- [Pytest Integration](../guides/pytest-integration.md) — `robo-automation` fixture ownership and extension points
- [Command-Line Interface](cli.md) — `robo-appian` browser binary provisioning

## Component API

The package also exposes reusable Appian component helpers:

```python
from robo_appian import Button, Dropdown, InputText, Table
```

Component pages are generated from current source signatures/docstrings.

| Component | Use it for |
| --- | --- |
| [`Button`](button.md) | Appian button interactions |
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

## `Scope` compatibility boundary

Many current component signatures still expose [`Scope`](scope.md), defined as Playwright `Page | Locator`. `Scope` and the Robo* wrapper chain are owned by `robo-automation`; robo-appian components consume them.

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
