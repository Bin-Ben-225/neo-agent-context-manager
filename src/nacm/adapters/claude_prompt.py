from __future__ import annotations

from pathlib import Path

from nacm.templates.renderer import render_template
from nacm.utils.paths import agent_dir
from nacm.adapters.metadata import prompt_metadata


def render_claude_prompt(root: Path | None = None) -> str:
    context = prompt_metadata(root, "claude-prompt") if root else {}
    return render_template("claude_prompt.md.j2", context)


def write_claude_prompt(root: Path) -> Path:
    prompt_path = agent_dir(root) / "claude" / "claude_prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(render_claude_prompt(root), encoding="utf-8")
    return prompt_path
