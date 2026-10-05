# robo-appian

`robo-appian` is a reusable Python component library built on top of Playwright for automating Appian web applications. It provides Appian-focused operations that identify controls primarily through user-facing labels, accessible semantics, text, and meaningful scopes where supported, while consumer projects keep ownership of application workflows, assertions, business rules, credentials, waits, and test data.

## Architecture

```text
Consumer tests → robo-appian → Playwright → Appian web application
```

The first argument to scope-aware component methods is a `Scope`. **A `Scope` is either a Playwright `Page` or a Playwright `Locator`.** Pass a `Page` to search the whole document, or a `Locator` to restrict the search to a particular container. `robo-appian` does not create a separate scope object.

The project favors readable component calls such as:

```python
from robo_appian import Button, Dropdown, InputText

InputText.fill_by_label(scope, "Request Name", "Example Request")
Dropdown.select(scope, "Request Type", "Travel")
Button.click(scope, "Submit")
```

This keeps reusable Appian lookup mechanics in the library instead of repeating them throughout consumer workflows.

## Install

With pip:

```bash
pip install robo-appian
```

With Poetry:

```bash
poetry add robo-appian
```

Python 3.12 is required. `robo-appian` does **not** require Chromium specifically and does not provision browsers. Use the Playwright-supported browser configured by your consumer test project. If a Playwright-managed browser is not already available, install the engine your project uses separately, for example `playwright install chromium`, `playwright install firefox`, or `playwright install webkit`.

## Documentation

Full documentation, guides, and API reference are published at:

**https://dinilmithra.github.io/robo-appian/**

## Developer

**Dinil Mithra** — developer and maintainer of `robo-appian`.

- Repository: https://github.com/dinilmithra/robo-appian
- Issues: https://github.com/dinilmithra/robo-appian/issues

## License

`robo-appian` is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Dinil Mithra.
