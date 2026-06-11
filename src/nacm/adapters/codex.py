from __future__ import annotations

from pathlib import Path

from nacm.templates.renderer import render_template
from nacm.utils.clipboard import copy_text
from nacm.utils.paths import agent_dir
from nacm.adapters.metadata import prompt_metadata


def render_codex_prompt(root: Path | None = None) -> str:
    context = prompt_metadata(root, "codex") if root else {}
    return render_template("codex_prompt.md.j2", context)


def write_codex_prompt(root: Path) -> Path:
    prompt_path = agent_dir(root) / "codex" / "codex_prompt.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(render_codex_prompt(root), encoding="utf-8")
    return prompt_path


def copy_codex_prompt(root: Path) -> tuple[bool, Path, str | None]:
    prompt_path = agent_dir(root) / "codex" / "codex_prompt.md"
    if not prompt_path.exists():
        raise FileNotFoundError("Codex prompt not found. Run `nacm pack --target codex` first.")
    ok, error = copy_text(prompt_path.read_text(encoding="utf-8"))
    return ok, prompt_path, error
