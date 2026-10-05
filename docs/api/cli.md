# Command-Line Interface

The `robo-appian` executable is installed with the package.

## `install-browser`

```text
robo-appian install-browser [firefox|chromium|webkit|all]
```

The browser argument is optional.

| Command | Result |
| --- | --- |
| `robo-appian install-browser` | Install the full Playwright-managed browser set |
| `robo-appian install-browser all` | Install the full Playwright-managed browser set |
| `robo-appian install-browser firefox` | Install Firefox |
| `robo-appian install-browser chromium` | Install Chromium |
| `robo-appian install-browser webkit` | Install WebKit |

The implementation invokes Playwright through the current Python interpreter, making the command independent of shell and operating-system executable lookup.

See [Browser Management](../guides/browser-management.md) for runtime selection guidance.
