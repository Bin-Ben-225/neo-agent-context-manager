from __future__ import annotations

from pathlib import Path

from nacm.utils.clipboard import copy_text
from nacm.utils.paths import agent_dir


def copy_codex_prompt(root: Path) -> tuple[bool, Path, str | None]:
    prompt_path = agent_dir(root) / "codex" / "codex_prompt.md"
    if not prompt_path.exists():
        raise FileNotFoundError("Codex prompt not found. Run `nacm pack --target codex` first.")
    ok, error = copy_text(prompt_path.read_text(encoding="utf-8"))
    return ok, prompt_path, error
