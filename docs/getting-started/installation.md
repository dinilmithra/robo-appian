# Installation

## Requirements

`robo-appian` targets Python 3.12 and uses Playwright for browser automation.

Install the package:

```bash
pip install robo-appian
```

Install the browser used by your test environment, for example Chromium:

```bash
playwright install chromium
```

For CI or Linux environments, Playwright system dependencies may also need to be
installed by an administrator or by the runner image.

## Verify the installation

```python
from robo_appian import Button, InputText, Table

print(Button, InputText, Table)
```
