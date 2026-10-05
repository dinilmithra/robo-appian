# Choosing a Component

Start from the Appian control you want to interact with. Prefer the most specific public component available instead of starting with low-level selectors or `ComponentUtils`.

| I need to… | Start with |
| --- | --- |
| Click or wait for a button | [`Button`](../api/button.md) |
| Select or inspect a checkbox | [`CheckBox`](../api/checkbox.md) |
| Select a standard dropdown value | [`Dropdown`](../api/dropdown.md) |
| Enter or inspect a date | [`InputDate`](../api/input-date.md) |
| Fill or inspect text input | [`InputText`](../api/input-text.md) |
| Find or activate a link | [`Link`](../api/link.md) |
| Choose an item from a menu button | [`MenuButton`](../api/menu-button.md) |
| Select a radio option | [`RadioSelect`](../api/radio-select.md) |
| Work with repeated record content | [`RecordList`](../api/record-list.md) |
| Restrict interaction to a named region | [`Region`](../api/region.md) |
| Search and select from a searchable dropdown | [`SearchDropdown`](../api/search-dropdown.md) |
| Work with search suggestions | [`SearchInput`](../api/search-input.md) |
| Select or inspect a tab | [`Tab`](../api/tab.md) |
| Read or interact with table/grid content | [`Table`](../api/table.md) |
| Read or wait for visible text | [`Text`](../api/text.md) |
| Locate by arbitrary HTML attributes | [`RoboLocator`](../api/robo-locator.md) |

## Framework lookup or component helper?

Use `RoboPage` / `RoboLocator` when the control is best described by generic DOM/accessibility attributes:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    }
)
user_options.to_be_visible()
user_options.click()
```

Use a component helper when robo-appian has reusable Appian-specific behavior for that control:

```python
from robo_appian import InputText, Button

InputText.fill_by_label(page, "Request Name", "Example Request")
Button.click(page, "Submit")
```

## `Dropdown` or `SearchDropdown`?

Use `Dropdown` for the standard Appian dropdown interaction. Use `SearchDropdown` when the control requires typing search text and selecting from dynamic results.

## `InputText` methods

Start with `InputText.fill_by_label` when the field has a usable accessible label. Specialized methods exist for placeholders, ids, locators, and visible-label structures. Use the generated [InputText API](../api/input-text.md) as the signature authority.

## Understanding `Scope`

Many existing component signatures still expose [`Scope`](../api/scope.md), which is the internal Playwright `Page | Locator` search boundary used by the component layer.

New consuming projects should use the Robo* fixture/wrapper model for browser ownership. The `Scope` type remains documented because the current component APIs and internals still depend on it.

## When to use `ComponentUtils`

[`ComponentUtils`](../api/component-utils.md) contains shared lower-level operations. Application tests should normally prefer `RoboPage`, `RoboLocator`, or a component-specific API because those express intent more clearly.

## Arbitrary attribute lookup

`RoboLocator` accepts arbitrary HTML attributes, including standard, ARIA, `data-*`, and application-specific attributes:

```python
user_options = page.get_by_attributes(
    attributes={
        "role": "button",
        "aria-label": "User options",
    },
    excat_match=True,
)
```

For a stable HTML id:

```python
agree_button = page.get_by_id("jsAcceptButton")
agree_button.to_be_visible()
agree_button.click()
```

## Duplicate visible matches

`to_be_visible()` filters the current locator set by visibility. If multiple visible matches remain and using the first is intentional:

```python
user_options.to_be_visible()
user_options = user_options.first()
user_options.click()
```

Keep explicit selection in test/application code instead of silently choosing the first element inside generic lookup.
