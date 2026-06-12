from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from nacm.utils.paths import agent_dir


@dataclass(frozen=True)
class EfficiencyStats:
    indexed_files: int
    skipped_files: int
    context_files: int
    context_chars: int
    file_reduction_percent: float


def collect_stats(root: Path) -> EfficiencyStats:
    local_agent = agent_dir(root)
    index_meta = read_json(local_agent / "index" / "index_meta.json")
    context_pack = local_agent / "sessions" / "context_pack.md"
    context_text = context_pack.read_text(encoding="utf-8") if context_pack.exists() else ""

    indexed_files = int(index_meta.get("scanned_files", 0))
    context_files = count_context_files(context_text)
    reduction = file_reduction(indexed_files, context_files)
    return EfficiencyStats(
        indexed_files=indexed_files,
        skipped_files=int(index_meta.get("skipped_files", 0)),
        context_files=context_files,
        context_chars=len(context_text),
        file_reduction_percent=reduction,
    )


def render_stats(stats: EfficiencyStats) -> str:
    return "\n".join(
        [
            "NACM Efficiency Stats",
            f"Indexed files: {stats.indexed_files}",
            f"Skipped files: {stats.skipped_files}",
            f"Context files: {stats.context_files}",
            f"Context chars: {stats.context_chars}",
            f"File reduction: {stats.file_reduction_percent:.1f}%",
            "",
        ]
    )


def count_context_files(context_text: str) -> int:
    return sum(1 for line in context_text.splitlines() if line.startswith("### `"))


def file_reduction(indexed_files: int, context_files: int) -> float:
    if indexed_files <= 0:
        return 0.0
    selected = min(context_files, indexed_files)
    return ((indexed_files - selected) / indexed_files) * 100


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}
