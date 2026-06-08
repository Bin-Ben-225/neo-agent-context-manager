from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nacm.constants import DEFAULT_PROFILE
from nacm.utils.git import ensure_info_exclude
from nacm.utils.paths import agent_dir


@dataclass(frozen=True)
class InitResult:
    root: Path
    agent_path: Path
    wrote_git_exclude: bool


def init_workspace(root: Path, profile: str = DEFAULT_PROFILE) -> InitResult:
    local_agent = agent_dir(root)
    directories = [
        local_agent,
        local_agent / "profiles",
        local_agent / "index",
        local_agent / "sessions",
        local_agent / "sessions" / "batches",
        local_agent / "codex",
        local_agent / "cache",
        local_agent / "reports",
        local_agent / "reports" / "history",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    write_if_missing(local_agent / "config.toml", f'active_profile = "{profile}"\n')
    write_if_missing(local_agent / "device.toml", 'device_profile = "local"\n')
    write_if_missing(
        local_agent / "profiles" / "low-memory.toml",
        "\n".join(
            [
                "max_context_chars = 30000",
                "max_files_in_context = 8",
                "max_file_head_kb = 16",
                "max_tree_depth = 3",
                "",
            ]
        ),
    )
    write_if_missing(
        local_agent / "profiles" / "workstation.toml",
        "\n".join(
            [
                "max_context_chars = 60000",
                "max_files_in_context = 16",
                "max_file_head_kb = 32",
                "max_tree_depth = 5",
                "",
            ]
        ),
    )
    write_if_missing(
        local_agent / "codex" / "AGENTS.local.md",
        "\n".join(
            [
                "# NACM Codex Local Instructions",
                "",
                "Read `.agent/sessions/context_pack.md` before editing.",
                "Do not scan the whole repository unless the context pack asks for it.",
                "Do not commit `.agent/`.",
                "",
            ]
        ),
    )

    return InitResult(root=root, agent_path=local_agent, wrote_git_exclude=ensure_info_exclude(root))


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")
