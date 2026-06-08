import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)


def commit_file(path: Path, relative_path: str, content: str = "content\n") -> None:
    file_path = path / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", relative_path], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", f"add {relative_path}"], cwd=path, check=True, capture_output=True)


def test_done_report_classifies_changed_files_and_marks_index_dirty(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)
    commit_file(tmp_path, "src/app.py", "def run():\n    return True\n")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["index", "build"])
    (tmp_path / "src" / "app.py").write_text("def run():\n    return False\n", encoding="utf-8")
    (tmp_path / "src" / "new_feature.py").write_text("def feature():\n    return True\n", encoding="utf-8")

    result = runner.invoke(app, ["done"])

    assert result.exit_code == 0
    report = (tmp_path / ".agent" / "reports" / "latest_report.md").read_text(encoding="utf-8")
    assert "Changed file count: 2" in report
    assert "### Modified Files" in report
    assert "`src/app.py`" in report
    assert "### Added Or Untracked Files" in report
    assert "`src/new_feature.py`" in report
    assert "Large Change Risk: no" in report
    index_state = json.loads((tmp_path / ".agent" / "cache" / "index_state.json").read_text(encoding="utf-8"))
    assert index_state["dirty"] is True
    assert "src/app.py" in index_state["changed_files"]
    assert "src/new_feature.py" in index_state["changed_files"]


def test_done_report_recommends_large_change_review_when_change_count_exceeds_profile(
    tmp_path: Path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)
    runner.invoke(app, ["init"])
    for index in range(9):
        path = tmp_path / "src" / f"file_{index}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"VALUE = {index}\n", encoding="utf-8")

    result = runner.invoke(app, ["done"])

    assert result.exit_code == 0
    report = (tmp_path / ".agent" / "reports" / "latest_report.md").read_text(encoding="utf-8")
    assert "Changed file count: 9" in report
    assert "Large Change Risk: yes" in report
    assert "Recommendation: enter review-large-change before continuing." in report


def test_done_report_lists_deleted_files_and_forbidden_paths(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_git_repo(tmp_path)
    commit_file(tmp_path, "src/old.py", "OLD = True\n")
    runner.invoke(app, ["init"])
    (tmp_path / "src" / "old.py").unlink()
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "bundle.js").write_text("generated", encoding="utf-8")

    result = runner.invoke(app, ["done"])

    assert result.exit_code == 0
    report = (tmp_path / ".agent" / "reports" / "latest_report.md").read_text(encoding="utf-8")
    assert "### Deleted Files" in report
    assert "`src/old.py`" in report
    assert "Forbidden paths touched:" in report
    assert "`dist/bundle.js`" in report


def test_done_report_handles_non_git_workspace(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["done"])

    assert result.exit_code == 0
    report = (tmp_path / ".agent" / "reports" / "latest_report.md").read_text(encoding="utf-8")
    assert "Git metadata unavailable." in report
    assert "Changed file count: 0" in report
