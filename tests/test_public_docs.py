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
    assert "Do not implement MCP, plugins, background services, embeddings, vector databases, or GUI/TUI" in doc


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


def test_release_checklist_documents_tagging_and_verification():
    doc = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "py -3.11 -m pytest tests -q" in doc
    assert "py -3.11 -m ruff check ." in doc
    assert "py -3.11 -m nacm validate smoke" in doc
    assert ".\\scripts\\validate-hooks.ps1" in doc
    assert "py -3.11 -m pip wheel . -w $env:TEMP\\nacm-wheel-check" in doc
    assert "git tag v0.1.0-alpha.X" in doc
    assert "Release Checklist" in readme


def test_hook_validation_script_covers_codex_and_claude_payloads():
    script = (ROOT / "scripts" / "validate-hooks.ps1").read_text(encoding="utf-8")

    assert "nacm hook install --target $Target" in script
    assert '-Target "codex"' in script
    assert '-Target "claude-code"' in script
    assert "gpt-5-codex" in script
    assert "permission_mode" in script
    assert "context_pack.md" in script


def test_hooks_doc_describes_local_project_hook_workflow():
    doc = (ROOT / "docs" / "hooks.md").read_text(encoding="utf-8")
    compatibility = (ROOT / "docs" / "hook-compatibility.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert "nacm hook install --target codex" in doc
    assert "nacm hook install --target claude-code" in doc
    assert "UserPromptSubmit" in doc
    assert "does not upload source code" in doc
    assert "Claude Code `2.1.174`" in compatibility
    assert "Access is denied" in compatibility
    assert "commandWindows" in compatibility
    assert "Hooks" in readme
