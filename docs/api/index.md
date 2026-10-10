# API Reference

The public API is grouped by what an automation developer needs to do. Start with the fluent Appian component APIs. Runtime and lower-level scoping APIs are available when you need framework integration or advanced control.

## Page and scoping

| API | Use it for |
| --- | --- |
| [`AppianPage`](appian-page.md) | Main Appian page and fluent component entry point |
| [`AppianLocator`](appian-locator.md) | Scope work to a dialog, region, row, or subtree |
| [`AppianScope`](appian-scope.md) | Type alias for APIs that intentionally accept either page or locator |

Prefer `AppianPage` for normal application tests.

## Fluent Appian input components

| API | Use it for |
| --- | --- |
| [`AppianButton`](appian-button.md) | Buttons through `page.button(...)` |
| [`AppianTextbox`](appian-textbox.md) | Text inputs through `page.textbox(...)` |
| [`AppianDate`](appian-date.md) | Date inputs through `page.date(...)` |
| [`AppianCheckbox`](appian-checkbox.md) | Native Appian checkboxes through `page.checkbox(...)` |
| [`AppianRadioSelect`](appian-radio-select.md) | Labeled radio groups through `page.radio(...)` |
| [`AppianTab`](appian-tab.md) | Linked-card tabs through `page.tab(...)` |
| [`AppianInputComponent`](appian-input-component.md) | Shared input lifecycle; mainly for framework/component authors |

Example:

```python
page.textbox(label="Description").fill("Example")
page.date(label="Start Date").fill("10/15/2026")
page.radio(label="Priority").select("High")
page.button(name="Next").click()
```

## Reusable components

| Component | Use it for |
| --- | --- |
| [`MenuButton`](menu-button.md) | Menu-button actions |
| [`RecordList`](record-list.md) | Repeated record content |
| [`Region`](region.md) | Named regions/scoping |
| [`SearchInput`](search-input.md) | Search suggestions |
| [`ComponentUtils`](component-utils.md) | Shared lower-level component utilities |

## Runtime and framework integration

- [Appian Runtime](runtime.md) — `AppianRuntime`, `AppianContext`, `AutomationContext`, and correlation/runtime helpers
- [Assertion Helpers](assertions.md) — Appian-facing visibility/text assertions
- [Errors](errors.md) — `RoboAppianError` and `RoboAppianNavigationError`
- [Pytest Integration](../guides/pytest-integration.md) — fixtures and plugin integration

## Compatibility

Some older component helpers still expose compatibility signatures inherited from earlier layers. New Appian code should prefer `AppianPage`, `AppianLocator`, `AppianScope`, and the fluent component APIs above.
