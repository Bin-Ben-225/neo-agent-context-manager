import json
from pathlib import Path

from typer.testing import CliRunner

from nacm.cli import app
from nacm.hooks import (
    hook_status,
    install_hook,
    hook_command_for,
    process_user_prompt_hook,
    uninstall_hook,
    windows_hook_command_for,
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


def test_process_user_prompt_hook_accepts_codex_payload_extras(tmp_path: Path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def run():\n    return True\n", encoding="utf-8")

    output = process_user_prompt_hook(
        {
            "cwd": str(tmp_path),
            "hook_event_name": "UserPromptSubmit",
            "prompt": "fix src/app.py",
            "model": "gpt-5-codex",
            "turn_id": "turn-validation",
        },
        target="codex",
    )

    assert "NACM prepared context" in output["hookSpecificOutput"]["additionalContext"]
    assert (tmp_path / ".agent" / "sessions" / "current_task.md").read_text(
        encoding="utf-8"
    ).count("fix src/app.py")


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


def test_hook_status_verbose_cli_shows_paths_and_timeout(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    install_hook(tmp_path, target="codex")

    result = runner.invoke(app, ["hook", "status", "--verbose"])

    assert result.exit_code == 0
    assert ".codex" in result.stdout
    assert "timeout: 120" in result.stdout
    assert "command:" in result.stdout


def test_hook_doctor_cli_reports_ready_and_missing_targets(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    install_hook(tmp_path, target="claude-code")

    result = runner.invoke(app, ["hook", "doctor"])

    assert result.exit_code == 1
    assert "claude-code: ready" in result.stdout
    assert "codex: not installed" in result.stdout


def test_install_codex_hook_writes_windows_command_and_longer_timeout(tmp_path: Path):
    install_hook(tmp_path, target="codex")

    codex_hooks = json.loads((tmp_path / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    command_hook = codex_hooks["hooks"]["UserPromptSubmit"][0]["hooks"][0]

    assert command_hook["command"] == hook_command_for("codex")
    assert command_hook["commandWindows"] == windows_hook_command_for("codex")
    assert command_hook["timeout"] == 120


def test_process_hook_skips_non_prompt_events_without_writing_workspace(tmp_path: Path):
    output = process_user_prompt_hook(
        {
            "cwd": str(tmp_path),
            "hook_event_name": "PostToolUse",
            "prompt": "fix src/app.py",
        },
        target="codex",
    )

    assert "skipped" in output["hookSpecificOutput"]["additionalContext"]
    assert not (tmp_path / ".agent").exists()


def test_uninstall_removes_legacy_and_current_commands(tmp_path: Path):
    path = tmp_path / ".codex" / "hooks.json"
    path.parent.mkdir()
    path.write_text(
        json.dumps(
            {
                "hooks": {
                    "UserPromptSubmit": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "python3 -m nacm hook run --target codex",
                                },
                                {
                                    "type": "command",
                                    "command": hook_command_for("codex"),
                                },
                            ]
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )

    uninstall_hook(tmp_path, target="codex")

    assert hook_status(tmp_path)["codex"] is False
    assert "nacm hook run --target codex" not in path.read_text(encoding="utf-8")


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
