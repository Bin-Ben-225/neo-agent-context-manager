from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app
from nacm.indexer.scanner import build_index
from nacm.session.packer import build_context_pack
from nacm.session.stats import collect_stats, render_stats
from nacm.session.task import save_task
from nacm.workspace import init_workspace


runner = CliRunner()


def test_collect_stats_reports_file_reduction(tmp_path: Path):
    (tmp_path / "src").mkdir()
    for index in range(6):
        (tmp_path / "src" / f"module_{index}.py").write_text(
            f"def target_{index}():\n    return {index}\n",
            encoding="utf-8",
        )

    init_workspace(tmp_path)
    build_index(tmp_path)
    save_task(tmp_path, "inspect target_1")
    build_context_pack(tmp_path, max_files=2)

    stats = collect_stats(tmp_path)

    assert stats.indexed_files == 6
    assert stats.context_files <= 2
    assert stats.file_reduction_percent > 0
    assert stats.context_chars > 0


def test_render_stats_includes_reduction_summary(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    init_workspace(tmp_path)
    build_index(tmp_path)
    save_task(tmp_path, "inspect app")
    build_context_pack(tmp_path, max_files=1)

    output = render_stats(collect_stats(tmp_path))

    assert "Indexed files:" in output
    assert "Context files:" in output
    assert "File reduction:" in output


def test_stats_cli_prints_efficiency_metrics(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    init_workspace(tmp_path)
    build_index(tmp_path)
    save_task(tmp_path, "inspect app")
    build_context_pack(tmp_path, max_files=1)

    result = runner.invoke(app, ["stats"])

    assert result.exit_code == 0
    assert "File reduction:" in result.stdout


def test_stats_cli_can_print_json(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    init_workspace(tmp_path)
    build_index(tmp_path)
    save_task(tmp_path, "inspect app")
    build_context_pack(tmp_path, max_files=1)

    result = runner.invoke(app, ["stats", "--json"])

    assert result.exit_code == 0
    payload = __import__("json").loads(result.stdout)
    assert payload["indexed_files"] == 1
    assert payload["context_files"] == 1
    assert "file_reduction_percent" in payload


def test_stats_json_includes_task_and_selected_paths(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    init_workspace(tmp_path)
    build_index(tmp_path)
    save_task(tmp_path, "inspect app")
    build_context_pack(tmp_path, max_files=1)

    result = runner.invoke(app, ["stats", "--json"])

    assert result.exit_code == 0
    payload = __import__("json").loads(result.stdout)
    assert payload["task"]["text"] == "inspect app"
    assert payload["task"]["id"]
    assert payload["selected_file_paths"] == ["src/app.py"]
    assert payload["max_file_budget"] == 1
    assert payload["context_budget_usage_percent"] == 100.0
