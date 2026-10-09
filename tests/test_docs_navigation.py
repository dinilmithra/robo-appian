from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_appian_page_and_locator_are_separate_api_entries() -> None:
    mkdocs = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    page_doc = (ROOT / "docs" / "api" / "appian-page.md").read_text(encoding="utf-8")
    locator_doc = (ROOT / "docs" / "api" / "appian-locator.md").read_text(encoding="utf-8")

    assert "- Appian Page: api/appian-page.md" in mkdocs
    assert "- Appian Locator: api/appian-locator.md" in mkdocs
    assert "Appian Page and Locator" not in mkdocs
    assert page_doc.startswith("# Appian Page\n")
    assert locator_doc.startswith("# Appian Locator\n")
