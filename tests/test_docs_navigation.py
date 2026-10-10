from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_appian_page_and_locator_are_separate_api_entries() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    page_doc = (ROOT / "docs" / "api" / "appian-page.md").read_text(encoding="utf-8")
    locator_doc = (ROOT / "docs" / "api" / "appian-locator.md").read_text(
        encoding="utf-8"
    )

    assert "- Appian Page: api/appian-page.md" in mkdocs
    assert "- Appian Locator: api/appian-locator.md" in mkdocs
    assert "Appian Page and Locator" not in mkdocs
    assert page_doc.startswith("# Appian Page\n")
    assert locator_doc.startswith("# Appian Locator\n")


def test_docs_publish_workflow_is_present_and_targets_gh_pages() -> None:
    workflow = ROOT / ".github" / "workflows" / "publish-robo-appian-docs.yml"
    content = workflow.read_text(encoding="utf-8")

    assert workflow.is_file()
    assert "name: Publish robo-appian docs" in content
    assert "workflow_dispatch:" in content
    assert "branches:" in content
    assert "- main" in content
    assert "permissions:" in content
    assert "contents: write" in content
    assert "mkdocs build --strict" in content
    assert "mkdocs gh-deploy --force --clean" in content


def test_appian_tab_is_exposed_as_appian_api_entry() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    tab_doc = (ROOT / "docs" / "api" / "appian-tab.md").read_text(encoding="utf-8")

    assert "- Appian Tab: api/appian-tab.md" in mkdocs
    assert tab_doc.startswith("# AppianTab\n")
    assert "page.tab" in tab_doc
    assert "Selected Tab." in tab_doc
    assert "Unselected Tab." in tab_doc


def test_appian_link_is_exposed_as_appian_api_entry() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    link_doc = (ROOT / "docs" / "api" / "appian-link.md").read_text(encoding="utf-8")

    assert "- Appian Link: api/appian-link.md" in mkdocs
    assert link_doc.startswith("# AppianLink\n")
    assert "page.link" in link_doc
    assert "Create a New Request" in link_doc
    assert "RETURN TO DASHBOARD" in link_doc


def test_appian_table_is_exposed_as_appian_api_entry() -> None:
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    mkdocs = (project_root / "mkdocs.yml").read_text(encoding="utf-8")
    doc = project_root / "docs" / "api" / "appian-table.md"

    assert "Appian Table: api/appian-table.md" in mkdocs
    assert doc.exists()
    text = doc.read_text(encoding="utf-8")
    assert "visible=None" in text
    assert "label" in text
    assert "header_name" in text
    assert "row_name" in text
    assert "column_name" in text
