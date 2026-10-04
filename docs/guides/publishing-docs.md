# Publishing Documentation

Documentation source lives on the normal development branch with the Python
source. Generated HTML is published to the automation-owned `gh-pages` branch.

## Branch model

```text
main
  Python source
  docs/ Markdown source
  mkdocs.yml
  GitHub Actions workflow

        | automated publish
        v

gh-pages
  generated HTML only
```

Do not manually edit `gh-pages`. The repository workflow
`.github/workflows/publish-robo-appian-docs.yml` rebuilds and replaces the
generated site automatically.

The workflow runs when a commit is pushed to `main` and changes any of these
robo-appian documentation inputs:

- `robo-appian/docs/**`
- `robo-appian/robo_appian/**`
- `robo-appian/mkdocs.yml`
- `robo-appian/pyproject.toml`
- `robo-appian/poetry.lock`

It can also be started manually from **Actions > Publish robo-appian docs > Run
workflow**. The job first runs `mkdocs build --strict`; only a successful build
is published to `gh-pages`.

## GitHub Pages setting

In the repository, open **Settings > Pages** and select:

- **Source:** Deploy from a branch
- **Branch:** `gh-pages`
- **Folder:** `/ (root)`

The first successful publish creates the `gh-pages` branch automatically.

## Manual local validation

Before pushing documentation changes:

```powershell
poetry install --with docs
poetry run mkdocs build --strict
```

To publish manually from an authenticated clone (normally GitHub Actions does this):

```powershell
poetry run mkdocs gh-deploy --force --clean
```
