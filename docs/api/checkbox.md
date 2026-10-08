# Checkbox and radio groups

`AppianPage.checkbox(...)` provides Appian-aware selection semantics without relying on Appian CSS classes.

## Radio groups

Appian radio groups are identified from the field label and its accessibility relationship to the group: the label element has an `id`, and the corresponding `role="radiogroup"` references that id through `aria-labelledby`. The requested option is resolved only inside that group by its native `input[type="radio"]` `value`.

```python
conference = page.checkbox(label="Is this request for a conference?")
conference.select("Yes")
assert conference.is_selected("Yes")

page.checkbox(
    label="How many people are you submitting in this travel request?"
).select("More than one")
```

`select(value)` is idempotent: it checks the native `checked` state before interacting. If the requested option is already selected, no click/check action is sent. This also avoids accidentally selecting another `Yes` or `No` option elsewhere on the page.

## Native checkboxes

The same abstraction preserves native Appian checkbox behavior when no radio value is supplied:

```python
field = page.checkbox(label="Select All Rows")
field.select()
assert field.is_selected()
field.select(selected=False)
```

Native checkboxes are resolved using semantic `label[for]` or `role="group"` / `aria-labelledby` relationships. Component identity does not depend on Appian CSS classes.

::: robo_appian.appian.appian_radio_select.AppianRadioSelect
    options:
      heading_level: 2
      members_order: source
      show_source: false
