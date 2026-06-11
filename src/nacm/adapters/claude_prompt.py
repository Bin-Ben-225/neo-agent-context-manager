from __future__ import annotations

from pathlib import Path

from nacm.templates.renderer import render_template
from nacm.utils.paths import agent_dir


def render_claude_prompt() -> str:
    return render_template("claude_prompt.md.j2", {})


def write_claude_prompt(root: Path) -> Path:
    prompt_path = agent_dir(root) / "claude" / "claude_prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(render_claude_prompt(), encoding="utf-8")
    return prompt_path
