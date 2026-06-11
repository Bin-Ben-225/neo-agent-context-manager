from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_real_project_validation_docs_and_script_are_public_safe():
    doc = (ROOT / "docs" / "real-project-validation.md").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "validate-real-projects.ps1").read_text(encoding="utf-8")

    for project in ("humanize", "click", "uuid"):
        assert project in doc
        assert project in script
    assert "nacm match explain" in doc
    assert "nacm quick" in script
    assert ("private" + "_docs") not in doc
    assert ("Pha" + "se") not in doc
