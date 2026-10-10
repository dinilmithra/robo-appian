# AppianTab

`AppianTab` represents an Appian linked-card tab. Create it from `AppianPage` with `page.tab(...)`.

```python
details = page.tab(name="Details")

assert details.is_selected()

page.tab(name="Contacts").select()
```

## Semantics

The component is based on the accessible DOM contract rendered by Appian rather than generated CSS classes:

- the tab container has `role="link"`;
- the visible tab name identifies the tab;
- the selected tab contains accessibility text `Selected Tab.`;
- an inactive tab contains accessibility text beginning `Unselected Tab.`.

`select()` is idempotent. If the requested tab is already selected, it performs no click. After selecting an inactive tab, the component re-resolves the live tab locator because Appian can rerender the complete tab strip.

`is_selected(timeout=...)` waits only for the tab to exist and become visible, then returns its current state. It does not wait for an inactive tab to become selected.

::: robo_appian.appian.appian_tab.AppianTab
    options:
      show_root_heading: true
      members_order: source
      members:
        - is_visible
        - is_selected
        - select

## Exact matching and visibility

Semantic component lookup defaults to `exact=True` and `visible=True`. Use `exact=False` for intentional partial label/name matching. Use `visible=False` for hidden matches, or `visible=None` (also blank/whitespace) to apply no visibility filter.


## Timeout

Component `timeout` values are expressed in seconds. `timeout=None` preserves the framework timeout configured from `WAIT_TIME`; a positive finite value overrides that timeout for waits/actions performed by the semantic component.
