from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from nacm.config import load_profile
from nacm.session.task import read_current_task
from nacm.utils.paths import agent_dir


@dataclass(frozen=True)
class WorkspaceStatus:
    workspace_ready: bool
    profile: str
    index_ready: bool
    current_task: str | None
    index_dirty: bool


def inspect_workspace(root: Path) -> WorkspaceStatus:
    local_agent = agent_dir(root)
    if not local_agent.is_dir():
        return WorkspaceStatus(
            workspace_ready=False,
            profile="unknown",
            index_ready=False,
            current_task=None,
            index_dirty=False,
        )

    profile = load_profile(root).name
    current_task = read_current_task(root) or None
    index_state = _read_index_state(local_agent / "cache" / "index_state.json")
    return WorkspaceStatus(
        workspace_ready=True,
        profile=profile,
        index_ready=(local_agent / "index" / "file_summary.json").is_file(),
        current_task=current_task,
        index_dirty=bool(index_state.get("dirty", False)),
    )


def render_status(status: WorkspaceStatus) -> str:
    if not status.workspace_ready:
        return "\n".join(
            [
                "Workspace: missing",
                "Profile: unknown",
                "Index: missing",
                "Current task: none",
                "Index dirty: no",
                "Next: run `nacm init --profile low-memory`",
                "",
            ]
        )

    lines = [
        "Workspace: ready",
        f"Profile: {status.profile}",
        f"Index: {'ready' if status.index_ready else 'missing'}",
        f"Current task: {status.current_task or 'none'}",
        f"Index dirty: {'yes' if status.index_dirty else 'no'}",
    ]
    if not status.index_ready:
        lines.append("Next: run `nacm index build`")
    elif status.index_dirty:
        lines.append("Next: run `nacm index build` if project structure or symbols changed")
    else:
        lines.append("Next: ready for `nacm quick` or `nacm task`")
    lines.append("")
    return "\n".join(lines)


def _read_index_state(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
