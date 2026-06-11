from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from nacm.adapters import claude_prompt, codex


@dataclass(frozen=True)
class PromptAdapter:
    target: str
    write: Callable[[Path], Path]
    copy: Callable[[Path], tuple[bool, Path, str | None]] | None = None


ADAPTERS: dict[str, PromptAdapter] = {
    "codex": PromptAdapter("codex", codex.write_codex_prompt, codex.copy_codex_prompt),
    "claude-prompt": PromptAdapter("claude-prompt", claude_prompt.write_claude_prompt),
}


def supported_targets() -> list[str]:
    return sorted(ADAPTERS)


def write_prompt(root: Path, target: str) -> Path:
    return adapter_for(target).write(root)


def copy_prompt(root: Path, target: str) -> tuple[bool, Path, str | None]:
    adapter = adapter_for(target)
    if adapter.copy:
        return adapter.copy(root)
    prompt_path = write_prompt(root, target)
    return False, prompt_path, f"Target `{target}` does not support clipboard copy."


def adapter_for(target: str) -> PromptAdapter:
    if target not in ADAPTERS:
        raise ValueError(f"Unsupported target `{target}`. Supported targets: {', '.join(supported_targets())}.")
    return ADAPTERS[target]
