# Browser Management

`robo-appian` depends on the browser automation runtime and provides a platform-independent command for provisioning framework-managed browser binaries.

## Install all browsers

```bash
robo-appian install-browser
```

Equivalent explicit form:

```bash
robo-appian install-browser all
```

## Install one browser

```bash
robo-appian install-browser firefox
robo-appian install-browser chromium
robo-appian install-browser webkit
```

Internally, the command runs the equivalent of:

```text
<current-python> -m playwright install [browser]
```

It does not rely on a platform-specific `playwright` executable being on `PATH`.

## Runtime browser selection

Browser installation and browser execution are separate decisions.

The generic lifecycle selects a browser from the automation configuration. The common setting is:

```text
BROWSER=firefox
```

Supported browser engine names are:

- `chromium`
- `firefox`
- `webkit`

If no value is configured, the generic lifecycle defaults to Chromium.

For a visible local browser session:

```text
HEAD_LESS=false
```

## CI guidance

Install the browser during environment/bootstrap setup, not inside individual tests. For example:

```bash
pip install robo-appian
robo-appian install-browser firefox
pytest
```

On Linux, the selected browser may also require operating-system libraries provided by the runner/container image.
