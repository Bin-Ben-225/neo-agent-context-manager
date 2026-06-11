from pathlib import Path

import pytest

from nacm.adapters.registry import copy_prompt, supported_targets, write_prompt


def test_registry_keeps_codex_prompt_path_compatible(tmp_path: Path):
    prompt_path = write_prompt(tmp_path, "codex")

    assert prompt_path == tmp_path / ".agent" / "codex" / "codex_prompt.md"
    assert "First read `.agent/sessions/context_pack.md`." in prompt_path.read_text(encoding="utf-8")
    assert "codex" in supported_targets()


def test_registry_writes_claude_prompt_only_target(tmp_path: Path):
    prompt_path = write_prompt(tmp_path, "claude-prompt")

    assert prompt_path == tmp_path / ".agent" / "claude" / "claude_prompt.md"
    prompt = prompt_path.read_text(encoding="utf-8")
    assert "Read `.agent/sessions/context_pack.md` before editing." in prompt
    assert "Do not use hooks, MCP, plugins, or background services." in prompt
    assert "claude-prompt" in supported_targets()


def test_registry_rejects_unknown_target(tmp_path: Path):
    with pytest.raises(ValueError, match="Unsupported target"):
        write_prompt(tmp_path, "unknown")


def test_registry_copy_reports_target_without_clipboard_support(tmp_path: Path):
    write_prompt(tmp_path, "claude-prompt")

    ok, prompt_path, error = copy_prompt(tmp_path, "claude-prompt")

    assert ok is False
    assert prompt_path == tmp_path / ".agent" / "claude" / "claude_prompt.md"
    assert "does not support clipboard copy" in str(error)


def test_registry_prompts_include_task_and_relation_metadata(tmp_path: Path):
    sessions = tmp_path / ".agent" / "sessions"
    index = tmp_path / ".agent" / "index"
    sessions.mkdir(parents=True)
    index.mkdir(parents=True)
    (sessions / "current_task.md").write_text(
        "# Current Task\n\nTask ID: 1\nTask: fix relation aware matching\n",
        encoding="utf-8",
    )
    (sessions / "context_pack.md").write_text(
        "### High Confidence\n- `src/matcher.py` (score: 10)\n"
        "### Medium Confidence\n- None\n"
        "### Low Confidence\n- None\n",
        encoding="utf-8",
    )
    (index / "relation_index.json").write_text("{}", encoding="utf-8")

    codex_prompt = write_prompt(tmp_path, "codex").read_text(encoding="utf-8")
    claude_prompt = write_prompt(tmp_path, "claude-prompt").read_text(encoding="utf-8")

    assert "Current task: fix relation aware matching" in codex_prompt
    assert "Relation index: available" in codex_prompt
    assert "High confidence files: 1" in codex_prompt
    assert "Current task: fix relation aware matching" in claude_prompt
    assert "Use relation index hints as navigation aids." in claude_prompt
