# Appian Input Components

Input components represent fields where a user can enter, select, or change information in an Appian application.

Common input components include:

| Component | Use it for |
| --- | --- |
| Textbox | Entering text or numbers |
| Date | Entering a date |
| Dropdown | Choosing one value from a list |
| Checkbox | Turning an option on or off |
| Radio | Choosing one value from a small set of choices |

Most tests use the specific component directly:

```python
page.textbox(label="Description").fill("Example description")
page.dropdown(label="Category").select(value="General")
page.checkbox(label="Include Details").check()
```

## Finding a field

By default, component matching is exact and targets visible fields:

```python
page.textbox(label="Description")
```

Use `exact=False` when a partial label is intentional:

```python
page.textbox(label="Description", exact=False)
```

Use `visible=None` when both visible and hidden matches should be considered:

```python
page.textbox(label="Description", visible=None)
```

## Checking whether a field is ready

`is_enabled()` checks the current state immediately:

```python
field = page.dropdown(label="Subcategory")

if field.is_enabled():
    field.select(value="Standard")
```

Some Appian fields become available only after another field changes. Supply a timeout when the test should wait for that field to become enabled:

```python
page.dropdown(label="Category").select(value="General")

subcategory = page.dropdown(label="Subcategory")
if subcategory.is_enabled(timeout=8):
    subcategory.select(value="Standard")
```

`timeout` is measured in seconds. `is_enabled()` without a timeout does not wait.

## API

::: robo_appian.appian.appian_input_component.AppianInputComponent
    options:
      show_root_heading: true
      members_order: source

## Focus-out after changes

Input components that change a value perform the framework's focus-out behavior after the change so Appian can process dependent updates. Tests should not add a Tab keystroke just to validate a changed value.
