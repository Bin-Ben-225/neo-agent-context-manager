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
