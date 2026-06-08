from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib

from nacm.utils.paths import agent_dir


@dataclass(frozen=True)
class Profile:
    name: str
    max_context_chars: int = 30000
    max_files_in_context: int = 8
    max_file_head_kb: int = 16
    max_tree_depth: int = 3


def load_profile(root: Path, name: str = "low-memory") -> Profile:
    path = agent_dir(root) / "profiles" / f"{name}.toml"
    if not path.exists():
        return Profile(name=name)

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return Profile(
        name=name,
        max_context_chars=_int_value(data, "max_context_chars", 30000),
        max_files_in_context=_int_value(data, "max_files_in_context", 8),
        max_file_head_kb=_int_value(data, "max_file_head_kb", 16),
        max_tree_depth=_int_value(data, "max_tree_depth", 3),
    )


def _int_value(data: dict, key: str, default: int) -> int:
    value = data.get(key, default)
    if isinstance(value, int):
        return value
    return default
