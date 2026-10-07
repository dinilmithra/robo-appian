# Publishing Documentation

Documentation source lives on `main` with the robo-appian source code. GitHub
Actions builds the MkDocs site and publishes the generated HTML to `gh-pages`.

## Automatic publishing

Every push to `main` triggers the **Publish robo-appian docs** workflow:

```text
git push origin main
        |
        v
Publish robo-appian docs
        |
        +-- mkdocs build --strict
        |
        v
gh-pages
        |
        v
GitHub Pages
```

The workflow is defined in:

```text
.github/workflows/publish-robo-appian-docs.yml
```

It can also be started manually from **Actions > Publish robo-appian docs > Run
workflow**.

Do not manually edit `gh-pages`. It contains generated site files and is
replaced by the workflow when documentation is published.

## GitHub Pages setting

In the repository, open **Settings > Pages** and configure:

- **Source:** Deploy from a branch
- **Branch:** `gh-pages`
- **Folder:** `/ (root)`

After the workflow updates `gh-pages`, GitHub's **pages build and deployment**
job publishes the site.

## Local validation

Before pushing documentation changes, you can validate the site locally:

```powershell
poetry install --with docs
poetry run mkdocs build --strict
```

For an interactive local preview:

```powershell
poetry run mkdocs serve
```

Normal publishing does not require running `mkdocs gh-deploy` locally; pushing
to `main` starts the publishing workflow automatically.
