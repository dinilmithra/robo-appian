# robo-appian

`robo-appian` provides reusable Appian-specific UI components and interaction utilities. Generic Playwright resource ownership, wrappers, and pytest fixtures live in `robo-automation`.

## Architecture

```text
Consumer / CORE application code
        ↓
robo-appian AppianPage / AppianLocator / components
        ↓
robo-automation generic wrappers
Browser → RoboBrowserContext → RoboPage → RoboLocator
        ↓
Playwright
        ↓
Appian
```

For Appian consumers, `robo-appian` provides `AppianPage(RoboPage)` and `AppianLocator(RoboLocator)`. Both `robo-automation` and `robo-appian` are pytest plugins discovered through installed `pytest11` entry points. The fixture layering is automatic:

```text
robo-automation: robo_page -> RoboPage
                         ↓
robo-appian:     appian_page -> AppianPage
                         ↓
                 page -> AppianPage
```

No consumer wrapper-selector fixture is required. A normal Appian test simply requests `page`:

```python
from robo_appian import AppianPage, Button, InputText


def test_example(page: AppianPage) -> None:
    InputText.fill_by_label(page, "Request Name", "Example Request")
    page.button(name="Submit").click()
```

A consuming application such as CORE may override only the public `page` fixture to add application-specific navigation/login while depending on `appian_page`; the underlying Playwright page is still created and closed by `robo-automation`.

## Install

```bash
pip install robo-appian
```

Python 3.12 is required. The package depends on `robo-automation` and currently also declares Playwright/pytest directly because its Appian implementation and development tooling use those APIs.

Install Playwright-managed browser binaries with the robo-appian CLI:

```bash
robo-appian install-browser
robo-appian install-browser firefox
robo-appian install-browser chromium
robo-appian install-browser webkit
```

`robo-appian install-browser all` is equivalent to the no-argument full install. The command uses the current Python interpreter (`sys.executable -m playwright install ...`) and is platform independent.

## Component APIs and Scope

Reusable components such as `Button`, `InputText`, `Dropdown`, and `Table` expose Appian-specific interaction behavior. Many current component signatures still use the generic `Scope = Playwright Page | Locator` compatibility/search-boundary type from `robo-automation`.

Generic lifecycle/resource code should use `RoboBrowserContext`, `RoboPage`, and `RoboLocator` from `robo_automation`; those types are not owned or exported by `robo_appian`.

## Documentation

Full documentation and component API reference:

**https://dinilmithra.github.io/robo-appian/**

## Developer

**Dinil Mithra** — developer and maintainer of `robo-appian`.

- Repository: https://github.com/dinilmithra/robo-appian
- Issues: https://github.com/dinilmithra/robo-appian/issues

## License

`robo-appian` is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Dinil Mithra.
