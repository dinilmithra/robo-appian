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
playwright install chromium
```

With Poetry:

```bash
poetry add robo-appian
poetry run playwright install chromium
```

Python 3.12 is required.

## Documentation

The MkDocs site is the primary user documentation. It includes installation, architecture and label-oriented concepts, a first-test walkthrough, component-selection guidance, troubleshooting, and generated API reference pages.

For local documentation development:

```bash
poetry install --with docs
poetry run mkdocs build --strict
poetry run mkdocs serve
```

Generated `site/` output is not source and should not be edited manually.
