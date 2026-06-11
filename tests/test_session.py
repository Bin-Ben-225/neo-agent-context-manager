from pathlib import Path
import subprocess

from typer.testing import CliRunner

from nacm.cli import app
from nacm.session.packer import build_context_pack


runner = CliRunner()


def test_quick_generates_context_pack_and_codex_prompt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "images.py").write_text("def load_image(path):\n    return path\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])

    result = runner.invoke(app, ["quick", "fix image loading failure"])

    assert result.exit_code == 0
    context_pack = (tmp_path / ".agent" / "sessions" / "context_pack.md").read_text(encoding="utf-8")
    prompt = (tmp_path / ".agent" / "codex" / "codex_prompt.md").read_text(encoding="utf-8")
    assert "fix image loading failure" in context_pack
    assert "src/images.py" in context_pack
    assert ".agent/sessions/context_pack.md" in prompt
    assert "Do not scan the whole repository" in prompt
    assert "Do not create or modify the repository root AGENTS.md" in prompt
    assert "Functions: load_image" in context_pack


def test_task_history_lists_and_shows_latest_task(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    first = runner.invoke(app, ["task", "set", "fix image loading"])
    second = runner.invoke(app, ["task", "set", "update report output"])
    listed = runner.invoke(app, ["task", "list"])
    shown = runner.invoke(app, ["task", "show", "latest"])

    assert first.exit_code == 0
    assert second.exit_code == 0
    assert listed.exit_code == 0
    assert "fix image loading" in listed.stdout
    assert "update report output" in listed.stdout
    assert shown.exit_code == 0
    assert "update report output" in shown.stdout
    assert "fix image loading" not in shown.stdout


def test_context_pack_gives_scoped_search_guidance_when_no_files_match(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "images.py").write_text("def load_image(path):\n    return path\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])

    result = runner.invoke(app, ["quick", "repair billing webhook retry"])

    assert result.exit_code == 0
    context_pack = (tmp_path / ".agent" / "sessions" / "context_pack.md").read_text(encoding="utf-8")
    assert "No relevant files matched this task." in context_pack
    assert "Use a scoped search before reading additional files." in context_pack


def test_build_context_pack_does_not_write_codex_prompt(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])
    runner.invoke(app, ["task", "set", "fix src/app.py"])

    result = build_context_pack(tmp_path)

    assert result == {"context_pack": tmp_path / ".agent" / "sessions" / "context_pack.md"}
    assert not (tmp_path / ".agent" / "codex" / "codex_prompt.md").exists()


def test_pack_respects_max_files_and_can_include_explanations(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "one.py").write_text("def target_one():\n    return True\n", encoding="utf-8")
    (tmp_path / "src" / "two.py").write_text("def target_two():\n    return True\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])
    runner.invoke(app, ["task", "set", "target one two"])

    result = runner.invoke(app, ["pack", "--max-files", "1", "--explain"])

    assert result.exit_code == 0
    context_pack = (tmp_path / ".agent" / "sessions" / "context_pack.md").read_text(encoding="utf-8")
    relevant_lines = [line for line in context_pack.splitlines() if line.startswith("- `src/")]
    assert len(relevant_lines) == 1
    assert "## Match Explanations" in context_pack
    assert "Included file budget: 1" in context_pack


def test_done_generates_report_with_forbidden_path_warning(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    runner.invoke(app, ["init"])
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "leak.txt").write_text("generated output", encoding="utf-8")

    result = runner.invoke(app, ["done"])

    assert result.exit_code == 0
    report = (tmp_path / ".agent" / "reports" / "latest_report.md").read_text(encoding="utf-8")
    assert "Forbidden Path Check" in report
    assert "build/leak.txt" in report
