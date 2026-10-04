# Development

## Local environment

From the parent workspace, create the standalone Python 3.12 environment:

```powershell
python .\robo-appian\tools\setup_venv.py
```

Open the standalone VS Code workspace:

```powershell
code .\robo-appian\robo-appian.code-workspace
```

## Run tests

```powershell
pytest
```

## Build documentation locally

Install the optional Poetry documentation group:

```powershell
poetry install --with docs
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
