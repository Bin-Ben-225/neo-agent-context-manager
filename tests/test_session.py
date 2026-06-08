from pathlib import Path
import subprocess

from typer.testing import CliRunner

from nacm.cli import app


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
