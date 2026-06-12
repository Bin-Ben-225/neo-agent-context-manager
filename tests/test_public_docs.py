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


def test_contributing_doc_lists_required_development_checks():
    doc = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    assert "py -3.11 -m pytest tests -q" in doc
    assert "py -3.11 -m ruff check ." in doc
    assert "py -3.11 -m nacm validate smoke" in doc
    assert "Do not commit `.agent/`" in doc
    assert "Do not implement hooks, MCP, plugins, background services, embeddings, vector databases, or GUI/TUI" in doc


def test_github_templates_cover_expected_feedback_paths():
    bug = (ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.md").read_text(encoding="utf-8")
    matcher = (ROOT / ".github" / "ISSUE_TEMPLATE" / "matcher_quality_report.md").read_text(
        encoding="utf-8"
    )
    target = (ROOT / ".github" / "ISSUE_TEMPLATE" / "target_prompt_request.md").read_text(
        encoding="utf-8"
    )
    pr = (ROOT / ".github" / "pull_request_template.md").read_text(encoding="utf-8")

    assert "NACM command" in bug
    assert "Expected top files" in matcher
    assert "Prompt target" in target
    assert "py -3.11 -m pytest tests -q" in pr
    assert "py -3.11 -m ruff check ." in pr
