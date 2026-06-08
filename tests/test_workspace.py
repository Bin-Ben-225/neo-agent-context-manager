from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app


runner = CliRunner()


def test_init_creates_local_workspace_and_git_exclude(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init", "--profile", "low-memory"])

    assert result.exit_code == 0
    assert (tmp_path / ".agent" / "config.toml").exists()
    assert (tmp_path / ".agent" / "profiles" / "low-memory.toml").exists()
    assert (tmp_path / ".agent" / "profiles" / "workstation.toml").exists()
    assert (tmp_path / ".agent" / "codex" / "AGENTS.local.md").exists()
    assert (tmp_path / ".agent" / "claude").exists() is False


def test_init_writes_git_info_exclude_when_git_repo(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    git_info = tmp_path / ".git" / "info"
    git_info.mkdir(parents=True)
    (git_info / "exclude").write_text("# local excludes\n", encoding="utf-8")

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert ".agent/" in (git_info / "exclude").read_text(encoding="utf-8")


def test_init_is_idempotent_and_preserves_existing_config(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    config = tmp_path / ".agent" / "config.toml"
    config.write_text("active_profile = \"custom\"\n", encoding="utf-8")

    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert config.read_text(encoding="utf-8") == "active_profile = \"custom\"\n"
