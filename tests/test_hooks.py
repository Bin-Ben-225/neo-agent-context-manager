import json
from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app
from nacm.hooks import (
    hook_status,
    install_hook,
    process_user_prompt_hook,
    uninstall_hook,
)


runner = CliRunner()


def test_process_user_prompt_hook_generates_context_and_json_output(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

    output = process_user_prompt_hook(
        {
            "cwd": str(tmp_path),
            "hook_event_name": "UserPromptSubmit",
            "prompt": "fix src/app.py",
        },
        target="codex",
    )

    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "Read `.agent/sessions/context_pack.md` first." in output["hookSpecificOutput"][
        "additionalContext"
    ]
    assert (tmp_path / ".agent" / "sessions" / "context_pack.md").exists()
    assert (tmp_path / ".agent" / "codex" / "codex_prompt.md").exists()


def test_process_user_prompt_hook_writes_claude_prompt_target(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

    output = process_user_prompt_hook(
        {
            "cwd": str(tmp_path),
            "hook_event_name": "UserPromptSubmit",
            "prompt": "fix src/app.py",
        },
        target="claude-code",
    )

    assert "NACM prepared context" in output["hookSpecificOutput"]["additionalContext"]
    assert (tmp_path / ".agent" / "claude" / "claude_prompt.md").exists()


def test_install_status_and_uninstall_project_hooks(tmp_path: Path):
    install_hook(tmp_path, target="claude-code")
    install_hook(tmp_path, target="codex")

    claude_settings = json.loads(
        (tmp_path / ".claude" / "settings.local.json").read_text(encoding="utf-8")
    )
    codex_hooks = json.loads((tmp_path / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    status = hook_status(tmp_path)

    assert "UserPromptSubmit" in claude_settings["hooks"]
    assert "UserPromptSubmit" in codex_hooks["hooks"]
    assert status["claude-code"] is True
    assert status["codex"] is True

    uninstall_hook(tmp_path, target="claude-code")
    uninstall_hook(tmp_path, target="codex")
    status = hook_status(tmp_path)

    assert status["claude-code"] is False
    assert status["codex"] is False


def test_hook_run_cli_reads_stdin_json(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")
    payload = json.dumps(
        {
            "cwd": str(tmp_path),
            "hook_event_name": "UserPromptSubmit",
            "prompt": "fix src/app.py",
        }
    )

    result = runner.invoke(app, ["hook", "run", "--target", "codex"], input=payload)

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "NACM prepared context" in output["hookSpecificOutput"]["additionalContext"]


def test_hook_run_cli_returns_json_for_invalid_input():
    result = runner.invoke(app, ["hook", "run", "--target", "codex"], input="not-json")

    assert result.exit_code == 0
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert "NACM hook skipped" in output["hookSpecificOutput"]["additionalContext"]
