# robo-appian

Reusable Playwright component helpers for Appian applications.

This package intentionally contains only generic Appian interaction behavior.
Application-specific labels, workflows, waits, and business rules belong in the
consuming application's facade layer.

For local CORE development the sibling `core-automation` project references this
package with a Poetry path dependency:

```toml
robo-appian = { path = "../robo-appian", develop = true }
```

## Local virtual environment

Create a dedicated Python 3.12 environment inside `robo-appian/.venv` from the parent workspace:

```powershell
python .\robo-appian\tools\setup_venv.py
```

The setup script recreates `robo-appian/.venv`, installs Poetry 2.5.1 into that environment, installs the project and development dependencies, and verifies both pytest and Poetry. The `.venv` directory is ignored by Git and is not packaged.

### VS Code automatic activation

Open the tracked standalone workspace file instead of opening the parent CORE workspace:

```powershell
code .\robo-appian\robo-appian.code-workspace
```

The workspace selects `robo-appian/.venv` as the default Python environment and enables terminal environment activation. New VS Code terminals opened in this workspace automatically activate the standalone `robo-appian` environment. This intentionally does not change CORE's parent `.venv-core`.

If you are using an existing terminal, activate it manually once:

```powershell
.\robo-appian\.venv\Scripts\Activate.ps1
```

## Publishing

Publishing tooling is kept under `robo-appian/tools/` but excluded from the published package. After opening the standalone workspace or activating `robo-appian/.venv`, run from `core-automation-project`:

```powershell
python .\robo-appian\tools\publish_robo_appian.py
```

Use `--build-only` to validate and build without uploading. The command reads `PYPI_TOKEN` (or `POETRY_PYPI_TOKEN_PYPI`) for PyPI authentication.

### PyPI token

The publisher reads the PyPI token from the process environment. The preferred variable is `POETRY_PYPI_TOKEN_PYPI`; `PYPI_TOKEN` and `PYPI_API_TOKEN` are also accepted and are mapped only into the child Poetry process. The token is never printed or written into the workspace.

PowerShell example:

```powershell
$env:POETRY_PYPI_TOKEN_PYPI = "<token>"
python .\tools\publish_robo_appian.py
```
