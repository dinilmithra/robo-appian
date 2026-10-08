# Development

## Local environment

`robo-appian` uses its own project-local `.venv`. From the parent workspace, create or refresh it with Python 3.12:

```powershell
python .\robo-appian\tools\setup_venv.py
```

The setup script first reuses Poetry **2.5.1** from your PATH (or from the bootstrap Python installation) without performing network access. It validates that `poetry.lock` matches `pyproject.toml`, automatically runs `poetry lock` when the lock file is missing or stale, and lets Poetry create and synchronize the project-local `.venv`. Poetry itself is **not** installed into `robo-appian/.venv`. The script then verifies that the installed `robo-appian` version matches `pyproject.toml` and that `import robo_appian` resolves from the local source tree.

Before running setup, verify the pinned Poetry version is available:

```powershell
poetry --version
```

If Poetry must be installed through an agency/corporate package source, install it there once and rerun setup. Normal setup intentionally does **not** download Poetry, which avoids indefinite waits behind restricted package indexes or proxies.

After setup, activate the environment from the `robo-appian` project directory:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
source ./.venv/bin/activate
```


### Poetry availability and optional bootstrap

Normal setup does not install Poetry from the network. It reuses an existing Poetry **2.5.1** installation and fails immediately with a clear message when that version is unavailable. This prevents environment setup from appearing to hang during a `pip install poetry` request behind a restricted proxy or package index.

If direct package-index access is known to work, network bootstrap can be requested explicitly:

```powershell
python .\robo-appian\tools\setup_venv.py --bootstrap-poetry
```

The optional bootstrap uses a temporary virtual environment outside `robo-appian/.venv`, applies bounded pip retries/timeouts, and is deleted after synchronization. You can adjust the pip network timeout when needed:

```powershell
python .\robo-appian\tools\setup_venv.py --bootstrap-poetry --bootstrap-timeout 60
```

The script resolves Poetry successfully **before** removing an existing project `.venv`, so a missing or blocked Poetry installation cannot destroy a previously usable environment.

### Browser binaries

Browser binaries are optional during environment creation. Install one engine while setting up the environment:

```powershell
python .\robo-appian\tools\setup_venv.py --browser firefox
```

Supported values are `firefox`, `chromium`, `webkit`, and `all`.

To install the full Playwright-managed browser set:

```powershell
python .\robo-appian\tools\setup_venv.py --browser all
```

If the environment already exists, browser binaries can be provisioned later through the platform-independent robo-appian CLI:

```powershell
robo-appian install-browser firefox
```

### Documentation dependencies

Install the documentation dependency group during setup with:

```powershell
python .\robo-appian\tools\setup_venv.py --with-docs
```

Options can be combined:

```powershell
python .\robo-appian\tools\setup_venv.py --with-docs --browser firefox
```

### Why `robo_appian-*.dist-info` appears in `.venv`

Poetry installs the current project into its development environment. A directory such as `robo_appian-0.1.19.dist-info` under `.venv/Lib/site-packages` is normal package metadata; it does not mean a second source copy should be edited there. The setup script verifies that `robo_appian.__file__` resolves to the local `robo_appian/` source directory.

## Run tests

```powershell
poetry run pytest
```

## Build documentation locally

If the docs group was not installed during setup, synchronize it first:

```powershell
poetry sync --with docs
```

Build with strict validation:

```powershell
poetry run mkdocs build --strict
```

Preview locally:

```powershell
poetry run mkdocs serve
```

The generated `site/` directory is intentionally ignored by Git.
