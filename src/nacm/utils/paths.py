from __future__ import annotations

from pathlib import Path


def agent_dir(root: Path) -> Path:
    return root / ".agent"


def to_posix_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def has_ignored_part(relative_posix: str, ignored_dirs: set[str], ignored_prefixes: tuple[str, ...]) -> bool:
    parts = relative_posix.split("/")
    if any(part in ignored_dirs for part in parts):
        return True
    return any(relative_posix == prefix or relative_posix.startswith(f"{prefix}/") for prefix in ignored_prefixes)
