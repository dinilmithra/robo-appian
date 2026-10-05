# API Reference

The API reference documents the public `robo-appian` building blocks you can use from a consumer test project. Component pages are generated from the library's public source signatures and docstrings, so parameter types, defaults, descriptions, and return information stay aligned with the implementation. Implementation source bodies are intentionally not rendered.

## Start with the package-level API

Prefer imports from `robo_appian`:

```python
from robo_appian import RoboBrowser, RoboContext, RoboPage, RoboLocator, Button, Dropdown, InputText, Table
```

The package root exposes the supported public components plus `ComponentUtils` and `Scope`.

## The interaction pattern

A typical call combines three ideas:

```python
InputText.fill_by_label(scope, "Request Name", "Example Request")
```

1. **Component** — `InputText` identifies the kind of Appian control.
2. **Scope** — `scope` is the interaction boundary that defines where robo-appian searches.
3. **User-facing identifier** — `"Request Name"` identifies the control by a label/accessibility concept supported by that method.

`robo-appian` then applies the reusable Appian component mechanics and uses Playwright for the browser interaction.

## Common conventions

| Convention | What it means |
| --- | --- |
| `scope` | A Playwright `Page` or `Locator`. `Page` searches the whole document; `Locator` restricts lookup to that locator. See [Scope](scope.md). |
| `RoboBrowser` | Browser-level wrapper around Playwright `Browser`. `new_context(...)` returns `RoboContext`. |
| `RoboContext` | Context-level wrapper around Playwright `BrowserContext`. `new_page()` returns `RoboPage`. |
| `RoboPage` | Page-level wrapper around Playwright `Page`. `get_by_attributes(...)` and `get_by_id(...)` return `RoboLocator` objects. |
| `RoboLocator` | Generic attribute-based element wrapper. Define any HTML attributes in `attributes` (for example `role`, `aria-label`, `data-testid`, `title`, or custom `data-*` attributes); robo-appian builds a scoped XPath locator. `excat_match` remains a separate matching option. Includes wrapped actions and assertions such as `click()`, `to_be_visible()`, `first()`, and generic `wait_for_attribute()` support. |
| label / text / accessible name | User-facing information used to identify an Appian control. Exact parameter names differ by component. |
| `excat_match` | Controls exact versus partial text matching when supported. Defaults to `False`. |
| waits | Generic component synchronization can live in `robo-appian`; workflow-specific timing stays in the consumer project. |
| return values | Queries return documented values such as `bool`, `str`, lists, or Playwright locators. Pure actions normally return nothing. |

!!! tip "Treat the signature as authoritative"
    Similar methods can intentionally have different defaults. Use the generated component reference for the exact signature rather than assuming all components behave identically.

## Choose a component

<div class="grid cards" markdown>

-   **[RoboBrowser](robo-browser.md)**  
    Playwright `Browser` wrapper that creates `RoboContext` objects.

-   **[RoboContext](robo-context.md)**  
    Playwright `BrowserContext` wrapper that creates `RoboPage` objects.

-   **[RoboPage](robo-page.md)**  
    Playwright `Page` wrapper for creating `RoboLocator` objects.

-   **[RoboLocator](robo-locator.md)**  
    Generic XPath-backed wrapper for Appian elements using arbitrary HTML attributes.

-   **[Button](button.md)**  
    Reusable operations for Appian button controls.

-   **[CheckBox](checkbox.md)**  
    Select and inspect Appian checkbox controls.

-   **[Dropdown](dropdown.md)**  
    Select and inspect values in Appian dropdown controls.

-   **[InputDate](input-date.md)**  
    Enter and read values from Appian date controls.

-   **[InputText](input-text.md)**  
    Fill and inspect Appian text input and paragraph controls.

-   **[Link](link.md)**  
    Find, read, wait for, and activate Appian links.

-   **[MenuButton](menu-button.md)**  
    Open Appian menu buttons and choose menu actions.

-   **[RadioSelect](radio-select.md)**  
    Select and inspect Appian radio options.

-   **[RecordList](record-list.md)**  
    Locate and select records from repeated Appian record content.

-   **[Region](region.md)**  
    Scope interactions to named Appian regions.

-   **[SearchDropdown](search-dropdown.md)**  
    Search, select, and inspect Appian searchable dropdowns.

-   **[SearchInput](search-input.md)**  
    Work with dynamic Appian search-input suggestions.

-   **[Tab](tab.md)**  
    Select and inspect Appian tab controls.

-   **[Table](table.md)**  
    Read and interact with Appian tables and editable grids.

-   **[Text](text.md)**  
    Read and synchronize on visible Appian text.

-   **[ComponentUtils](component-utils.md)**  
    Shared lower-level operations used by reusable Appian components.

-   **[Scope](scope.md)**  
    Common interaction-boundary type used across component APIs.

</div>

## Which component should I use?

Start from the rendered Appian control, not the business meaning of the field.

- standard list selection → [`Dropdown`](dropdown.md)
- type-to-search selection → [`SearchDropdown`](search-dropdown.md)
- ordinary text/paragraph input → [`InputText`](input-text.md)
- repeated row/grid content → [`Table`](table.md) or [`RecordList`](record-list.md)
- repeated labels in different UI regions → narrow the `scope` with [`Region`](region.md) or a locator-backed scope when supported

For a fuller decision guide, see [Choosing a Component](../getting-started/component-basics.md).

## Relationship to Playwright and your test project

```text
Consumer test project
        ↓
RoboBrowser → RoboContext → RoboPage → RoboLocator/components
        ↓
Playwright implementation
        ↓
Appian web application
```

Your **consumer project** owns application workflows, credentials, business rules, assertions, test data, application-specific labels, navigation, and workflow-specific waits.

**robo-appian** owns generic Appian component interaction behavior and reusable locator mechanics.

**Playwright** remains the underlying browser engine, but browser, context, and page objects are private implementation details behind the robo-appian framework wrappers.

New to the library? Start with [Installation](../getting-started/installation.md), then read [Core Concepts](../getting-started/concepts.md) and [Your First Test](../getting-started/first-test.md).
