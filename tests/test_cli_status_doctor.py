from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def test_status_reports_missing_workspace(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Workspace: missing" in result.stdout
    assert "Next: run `nacm init --profile low-memory`" in result.stdout


def test_status_reports_workspace_index_task_and_dirty_state(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])
    runner.invoke(app, ["task", "fix src/app.py"])
    (tmp_path / ".agent" / "cache" / "index_state.json").write_text(
        '{"dirty": true, "reason": "changed", "changed_files": ["src/app.py"]}',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    assert "Workspace: ready" in result.stdout
    assert "Profile: low-memory" in result.stdout
    assert "Index: ready" in result.stdout
    assert "Current task: fix src/app.py" in result.stdout
    assert "Index dirty: yes" in result.stdout


def test_doctor_fails_before_init_with_actionable_message(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "NACM workspace not found." in result.stdout
    assert "Run `nacm init --profile low-memory` first." in result.stdout


def test_doctor_fails_before_index_with_actionable_message(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 1
    assert "NACM index not found." in result.stdout
    assert "Run `nacm index build` first." in result.stdout


def test_doctor_passes_after_init_and_index(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])

    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "NACM doctor passed." in result.stdout
