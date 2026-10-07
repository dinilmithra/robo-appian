# Choosing a Component

Start from the Appian control you want to interact with. Prefer the most specific public component available instead of starting with low-level selectors or `ComponentUtils`.

| I need to… | Start with |
| --- | --- |
| Click or wait for a button | [`AppianButton`](../api/appian-button.md) |
| Fill a text field | [`AppianTextbox`](../api/appian-textbox.md) |
| Select or inspect a checkbox | [`CheckBox`](../api/checkbox.md) |
| Select a standard dropdown value | [`Dropdown`](../api/dropdown.md) |
| Enter or inspect a date | [`InputDate`](../api/input-date.md) |
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
| Locate by arbitrary HTML attributes | [`AppianLocator`](../api/appian-page.md) |

## Framework lookup or component helper?

Use `AppianPage` / `AppianLocator` when the control is best described by generic DOM/accessibility attributes:

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
from robo_appian import AppianPage

page.textbox(label="Request Name").fill("Example Request")
page.button(name="Submit").click()
```

## `Dropdown` or `SearchDropdown`?

Use `Dropdown` for the standard Appian dropdown interaction. Use `SearchDropdown` when the control requires typing search text and selecting from dynamic results.

## Fluent input textbox

Use the page-level API for text fields:

```python
page.textbox(label="Request Name").fill("Example Request")
page.textbox(placeholder="example@example.com").fill("user@example.com")
```

## Understanding `Scope`

Many existing component signatures still expose [`Scope`](../api/scope.md), which is the internal Playwright `Page | Locator` search boundary used by the component layer.

New consuming projects should use the Robo* fixture/wrapper model for browser ownership. The `Scope` type remains documented because the current component APIs and internals still depend on it.

## When to use `ComponentUtils`

[`ComponentUtils`](../api/component-utils.md) contains shared lower-level operations. Application tests should normally prefer `AppianPage`, `AppianLocator`, or a component-specific API because those express intent more clearly.

## Arbitrary attribute lookup

`AppianLocator` accepts arbitrary HTML attributes, including standard, ARIA, `data-*`, and application-specific attributes:

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
