from __future__ import annotations

from pathlib import Path

from nacm.session.task import read_current_task
from nacm.utils.paths import agent_dir


def prompt_metadata(root: Path, target: str) -> dict:
    local_agent = agent_dir(root)
    context = read_context_pack(local_agent)
    return {
        "target": target,
        "task": read_current_task(root),
        "relation_index_available": (local_agent / "index" / "relation_index.json").exists(),
        "high_confidence_count": count_confidence_items(context, "High"),
        "medium_confidence_count": count_confidence_items(context, "Medium"),
        "low_confidence_count": count_confidence_items(context, "Low"),
    }


def read_context_pack(local_agent: Path) -> str:
    path = local_agent / "sessions" / "context_pack.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def count_confidence_items(context: str, confidence: str) -> int:
    marker = f"### {confidence} Confidence"
    if marker not in context:
        marker = f"### {confidence}"
    if marker not in context:
        return 0
    section = context.split(marker, 1)[1].split("### ", 1)[0]
    return sum(1 for line in section.splitlines() if line.startswith("- `"))
