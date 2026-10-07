# robo-appian

`robo-appian` provides reusable Appian-specific UI components and interaction utilities. Generic Playwright resource ownership, wrappers, and pytest fixtures live in `robo-automation`.

## Architecture

```text
Consumer / CORE application code
        ↓
robo-appian AppianPage / AppianLocator / components
        ↓
robo-automation generic resource lifecycle
        ↓
Appian
```

For Appian consumers, `robo-appian` provides `AppianPage` and `AppianLocator`. Both `robo-automation` and `robo-appian` are pytest plugins discovered through installed `pytest11` entry points. The fixture layering is automatic:

```text
robo-automation: generic page lifecycle
                         ↓
robo-appian:     appian_page -> AppianPage
                         ↓
                 page -> AppianPage
```

No consumer wrapper-selector fixture is required. A normal Appian test simply requests `page`:

```python
from robo_appian import AppianPage


def test_example(page: AppianPage) -> None:
    page.textbox(label="Request Name").fill("Example Request")
    page.button(name="Submit").click()
```

A consuming application such as CORE may override only the public `page` fixture to add application-specific navigation/login while depending on `appian_page`; generic resource creation and cleanup remain owned by `robo-automation`.

## Install

```bash
pip install robo-appian
```

Python 3.12 is required. The package depends on `robo-automation` for generic automation lifecycle support.

Install Playwright-managed browser binaries with the robo-appian CLI:

```bash
robo-appian install-browser
robo-appian install-browser firefox
robo-appian install-browser chromium
robo-appian install-browser webkit
```

`robo-appian install-browser all` is equivalent to the no-argument full install. The command uses the current Python interpreter (`sys.executable -m playwright install ...`) and is platform independent.

## Component APIs and Scope

The preferred Appian-facing API uses `AppianPage`, `AppianLocator`, and `AppianScope`. `AppianScope` is `AppianPage | AppianLocator`; use `AppianPage` for page-wide operations and `AppianLocator` only when a dialog or subtree must constrain the search.

`AppianButton`, `AppianTextbox`, and `AppianDate` are implemented inside `robo_appian.appian` and are created through `page.button(name="...")`, `page.textbox(...)`, and `page.date(...)`. The legacy component APIs remain compatibility surfaces while fluent Appian components are the preferred consumer model.

## Documentation

Full documentation and component API reference:

**https://dinilmithra.github.io/robo-appian/**

## Developer

**Dinil Mithra** — developer and maintainer of `robo-appian`.

- Repository: https://github.com/dinilmithra/robo-appian
- Issues: https://github.com/dinilmithra/robo-appian/issues

## License

`robo-appian` is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Dinil Mithra.
