# API Reference

The public API has two layers: framework wrappers for browser/resource ownership, and reusable Appian components for control-specific interaction behavior.

## Framework API

Prefer package-root imports:

```python
from robo_appian import RoboBrowser, RoboContext, RoboPage, RoboLocator
```

| Class | Responsibility |
| --- | --- |
| [`RoboBrowser`](robo-browser.md) | Browser-level wrapper; creates `RoboContext` |
| [`RoboContext`](robo-context.md) | Context-level wrapper; creates and tracks `RoboPage` |
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

- [Pytest Plugin](pytest-plugin.md) — fixture ownership and extension points
- [Command-Line Interface](cli.md) — browser binary provisioning

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

Many current component signatures still expose [`Scope`](scope.md), defined as Playwright `Page | Locator`. This reflects the current component implementation boundary. New consumer browser/resource code should use the Robo* wrapper chain and the robo-appian pytest plugin.

## Relationship to Playwright

```text
consumer project
      ↓
robo-appian pytest plugin / Robo* wrappers / components
      ↓
Playwright implementation dependency
      ↓
Appian
```

Playwright is installed as a robo-appian dependency. Consumer projects using the standard wrapper/fixture stack do not need to declare Playwright directly.
