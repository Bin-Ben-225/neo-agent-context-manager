import json
from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def test_index_build_skips_ignored_dirs_and_uses_posix_paths(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        "import os\n\nclass App:\n    pass\n\ndef run():\n    return True\n",
        encoding="utf-8",
    )
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "ignored.py").write_text("def ignored(): pass\n", encoding="utf-8")
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    paths = {item["path"] for item in summary["files"]}
    assert "src/app.py" in paths
    assert "node_modules/ignored.py" not in paths
    app_summary = next(item for item in summary["files"] if item["path"] == "src/app.py")
    assert "os" in app_summary["imports"]
    assert "App" in app_summary["classes"]
    assert "run" in app_summary["functions"]


def test_index_build_skips_large_file_content_summary(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "large.txt").write_text("x" * 200_000, encoding="utf-8")
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["index", "build"])

    assert result.exit_code == 0
    summary = json.loads((tmp_path / ".agent" / "index" / "file_summary.json").read_text(encoding="utf-8"))
    large = next(item for item in summary["files"] if item["path"] == "large.txt")
    assert large["summary_skipped"] is True
