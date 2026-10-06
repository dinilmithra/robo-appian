# robo-appian

`robo-appian` is a Python automation framework for Appian built on Playwright. It owns the browser/runtime wrapper layer and provides reusable Appian interaction components so consuming projects can focus on application workflows, data, and assertions.

## Architecture

```text
Consumer pytest project
        ↓
RoboBrowser → RoboContext → RoboPage → RoboLocator
        ↓
Reusable Appian components
        ↓
Playwright implementation
        ↓
Appian
```

The public framework wrappers are:

```python
from robo_appian import RoboBrowser, RoboContext, RoboPage, RoboLocator
```

With the pytest plugin enabled, tests normally receive `RoboPage` directly:

```python
# robo-appian is discovered automatically by pytest via the pytest11 entry point
```

```python
from robo_appian import RoboPage


def test_example(page: RoboPage) -> None:
    user_options = page.get_by_attributes(
        attributes={
            "role": "button",
            "aria-label": "User options",
        }
    )
    user_options.to_be_visible()
    user_options.click()
```

## Install

```bash
pip install robo-appian
```

Python 3.12 is required. Playwright is installed automatically as a robo-appian dependency.

Install all Playwright-managed browser binaries:

```bash
robo-appian install-browser
```

or one engine:

```bash
robo-appian install-browser firefox
robo-appian install-browser chromium
robo-appian install-browser webkit
```

`robo-appian install-browser all` is equivalent to the no-argument full install. The command uses the current Python interpreter (`sys.executable -m playwright install ...`) and is platform independent.

## Component APIs and Scope

Existing reusable components such as `Button`, `InputText`, `Dropdown`, and `Table` still expose the internal `Scope = Playwright Page | Locator` compatibility boundary in many generated signatures. New browser lifecycle/resource ownership should use the Robo* wrappers; `Scope` remains documented because it is still part of the current component implementation.

## Documentation

Full documentation, guides, framework reference, and component API reference:

**https://dinilmithra.github.io/robo-appian/**

## Developer

**Dinil Mithra** — developer and maintainer of `robo-appian`.

- Repository: https://github.com/dinilmithra/robo-appian
- Issues: https://github.com/dinilmithra/robo-appian/issues

## License

`robo-appian` is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Dinil Mithra.
