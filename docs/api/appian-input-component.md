# AppianInputComponent

`AppianInputComponent` is the shared base class for Appian controls that change input state.

Most application developers will not use this class directly. It exists so input components share the same post-change behavior without duplicating it.

Current examples include:

- `AppianTextbox`
- `AppianDate`
- `AppianRadioSelect`

After a value actually changes, the shared lifecycle moves focus out of the control so Appian can process the new value. Application tests normally should not add their own Tab press or manual blur.

## API

::: robo_appian.appian.appian_input_component.AppianInputComponent
    options:
      show_root_heading: true
      members_order: source
