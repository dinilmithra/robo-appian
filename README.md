# robo-appian

Reusable Playwright component helpers for Appian applications.

This package intentionally contains only generic Appian interaction behavior.
Application-specific labels, workflows, waits, and business rules belong in the
consuming application's facade layer.

## Installation

```bash
pip install robo-appian
playwright install chromium
```

## Documentation

The public documentation is built with MkDocs Material and generated API pages
from the Python source/docstrings.

After GitHub Pages is enabled for the repository, the project site will normally
be available at:

```text
https://<github-owner>.github.io/robo-appian/
```

Documentation source is maintained under `docs/` on `main`. GitHub Actions
validates documentation on pull requests and publishes generated HTML to the
`gh-pages` branch after documentation-related changes are merged to `main`.

Build and preview the documentation locally:

```powershell
poetry install --with docs
poetry run mkdocs build --strict
poetry run mkdocs serve
```

See `docs/guides/publishing-docs.md` for the GitHub Pages branch configuration.

## Local CORE development

CORE pins the published package in its dependency configuration. For local
development, install the sibling reusable-library checkouts in editable mode
without changing the committed dependency configuration. From `core-automation`:

```powershell
.\.venv-core\Scripts\python.exe .\tools\install_local_libraries.py
```

## Local virtual environment

Create a dedicated Python 3.12 environment inside `robo-appian/.venv` from the parent workspace:

```powershell
python .\robo-appian\tools\setup_venv.py
```

The setup script recreates `robo-appian/.venv`, installs Poetry 2.5.1 into that environment, installs the project and development dependencies, and verifies Poetry. The `.venv` directory is ignored by Git and is not packaged.

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

## Publishing to PyPI

Publishing tooling is kept under `robo-appian/tools/` but excluded from the published package. After opening the standalone workspace or activating `robo-appian/.venv`, run from `core-automation-project`:

```powershell
python .\robo-appian\tools\publish_robo_appian.py
```

The publisher always increments the patch version, removes the existing `dist/`
directory, builds, and uploads to PyPI. It does not support `--build-only` or
version override arguments. A build or upload failure restores the previous
version. To build without uploading or incrementing the version, run
`poetry build` from the `robo-appian` directory instead. The publisher reads
`PYPI_TOKEN` (or `POETRY_PYPI_TOKEN_PYPI`) for PyPI authentication.

### PyPI token

The publisher reads the PyPI token from the process environment. The preferred variable is `POETRY_PYPI_TOKEN_PYPI`; `PYPI_TOKEN` and `PYPI_API_TOKEN` are also accepted and are mapped only into the child Poetry process. The token is never printed or written into the workspace.

PowerShell example:

```powershell
$env:POETRY_PYPI_TOKEN_PYPI = "<token>"
python .\tools\publish_robo_appian.py
```
