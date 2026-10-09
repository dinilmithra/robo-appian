# robo-appian

`robo-appian` makes Appian pages easier to automate with readable Python.

It is designed for people who know their web application and only need basic Python to start writing automation.

## Quick example

```python
from robo_appian import AppianPage


def test_create_request(page: AppianPage) -> None:
    page.appian_textbox(label="Request Name").fill("Example Request")
    page.appian_date(label="Required Award Date").fill("10/15/2026")
    page.appian_radio(label="Is this request for a conference?").select("Yes")
    page.appian_button(name="Submit").click()
```

The goal is to describe the page using the same text a user sees.

## Install

```bash
pip install robo-appian
robo-appian install-browser firefox
```

Python 3.12 is required. `robo-appian` uses `robo-automation` for generic browser and pytest infrastructure.

## Common controls

```python
page.appian_textbox(label="Request Name").fill("Example Request")
page.appian_textbox(placeholder="example@example.com").fill("user@example.com")
page.appian_date(label="Required Award Date").fill("10/15/2026")
page.appian_radio(label="Is this request for a conference?").select("Yes")
page.appian_button(name="Next").click()
```

Textboxes, dates, and selection components automatically move focus out after a value changes so Appian can process it.

## What belongs where?

```text
Your application tests
        ↓
robo-appian       Appian controls and Appian behavior
        ↓
robo-automation   Browser and pytest infrastructure
        ↓
Playwright
```

Your application project should own application URLs, login policy, business workflows, assertions, and test data.

## Documentation

Start with the beginner guides:

- Installation
- Quick Start
- Your First Test
- Choosing a Component
- Troubleshooting

Advanced architecture and pytest integration are documented separately for framework maintainers.

Full documentation:

**https://dinilmithra.github.io/robo-appian/**

## License

`robo-appian` is licensed under the [MIT License](LICENSE).
## Error handling

Appian-specific library failures use `RoboAppianError`, which is also a `RoboAutomationError`. Normal tests should usually let pytest report these errors. If you need recovery or diagnostic handling, see **[How to use RoboAppianError](docs/getting-started/error-handling.md)** for examples using `code`, `details`, `to_dict()`, and exception chaining.


## Runtime boundary for application projects

Application projects should normally import automation APIs only from
`robo_appian`.

```python
from robo_appian import AppianPage, AppianRuntime, RoboAppianError
```

`AppianRuntime` provides the Appian-facing browser/session lifecycle used by
advanced consumer fixtures. It intentionally hides lower browser and
performance implementation classes. Normal test authors usually only need the
`page` fixture and component APIs shown above.
