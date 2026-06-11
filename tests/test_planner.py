from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def test_plan_generates_prompt_only_batch_plan(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["plan", "refactor matcher and add tests"])

    assert result.exit_code == 0
    assert "Wrote batch plan:" in result.stdout
    plan = (tmp_path / ".agent" / "sessions" / "batches" / "latest_plan.md").read_text(
        encoding="utf-8"
    )
    assert "refactor matcher and add tests" in plan
    assert "## Suggested Tasks" in plan
    assert "nacm quick" in plan
    assert "NACM will not execute these tasks automatically." in plan
