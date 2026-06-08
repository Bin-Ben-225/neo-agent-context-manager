from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def test_index_build_requires_init(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 1
    assert "Run `nacm init` first." in result.stdout


def test_quick_requires_index(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["quick", "fix image loading failure"])

    assert result.exit_code == 1
    assert "Run `nacm index build` first." in result.stdout


def test_pack_requires_current_task(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])

    result = runner.invoke(app, ["pack", "--target", "codex"])

    assert result.exit_code == 1
    assert "Run `nacm task" in result.stdout
