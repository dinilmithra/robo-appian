# Choosing a Component

Start from the Appian control you want to interact with. Prefer the most specific public component available instead of starting with low-level selectors or `ComponentUtils`. Where a component exposes a label- or accessibility-oriented method, prefer that readable interface before a specialized fallback.

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

## `Dropdown` or `SearchDropdown`?

Use `Dropdown` for the standard Appian dropdown interaction represented by that component's API. Use `SearchDropdown` when the Appian control requires entering search text and choosing from search results. Do not choose based only on the field's business meaning; choose based on the rendered control behavior.

## `InputText` methods

Start with `InputText.fill_by_label` when the field has a usable accessible label. The class also provides specialized methods for other reusable Appian structures, such as placeholder-, id-, locator-, or visible-label-based interaction. Use the [InputText API](../api/input-text.md) to select the narrowest method that matches the actual control.

## Which `scope` should I use?

When a method accepts [`Scope`](../api/scope.md), `scope` can be **either a Playwright `Page` or a Playwright `Locator`**. Pass a `Page` for a page-wide search. Pass a `Locator` when the lookup should be restricted to a specific container, especially when duplicate labels exist in different regions.

```python
scope = scope.get_by_role("region", name="Contact Information")
InputText.fill_by_label(scope, "Name", "Alex Example")
```

Public component methods use `scope` for the interaction boundary. A small number of lower-level helpers intentionally accept a more specific locator type; follow the generated signature in the API reference.

## When to use `ComponentUtils`

[`ComponentUtils`](../api/component-utils.md) contains shared lower-level operations. Application tests should normally prefer a component-specific API because it expresses intent more clearly. Reach for `ComponentUtils` only when its documented generic behavior is actually what your reusable code needs.

## When robo-appian does not have a component

Use normal Playwright in your consumer project when there is no suitable reusable helper:

```python
scope.get_by_role("heading", name="Request Summary").wait_for()
```

If the behavior is truly generic across Appian applications, it may be a candidate for the library. Do not move application-specific selectors or workflows into `robo-appian` simply to avoid writing Playwright in a test project.
