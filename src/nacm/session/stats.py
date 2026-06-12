from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from nacm.utils.paths import agent_dir


@dataclass(frozen=True)
class EfficiencyStats:
    indexed_files: int
    skipped_files: int
    context_files: int
    context_chars: int
    file_reduction_percent: float
    selected_file_paths: list[str]
    max_file_budget: int
    context_budget_usage_percent: float
    task: dict[str, str]


def collect_stats(root: Path) -> EfficiencyStats:
    local_agent = agent_dir(root)
    index_meta = read_json(local_agent / "index" / "index_meta.json")
    context_pack = local_agent / "sessions" / "context_pack.md"
    context_text = context_pack.read_text(encoding="utf-8") if context_pack.exists() else ""

    indexed_files = int(index_meta.get("scanned_files", 0))
    selected_file_paths = selected_paths(context_text)
    context_files = len(selected_file_paths)
    max_file_budget = read_max_file_budget(context_text)
    reduction = file_reduction(indexed_files, context_files)
    return EfficiencyStats(
        indexed_files=indexed_files,
        skipped_files=int(index_meta.get("skipped_files", 0)),
        context_files=context_files,
        context_chars=len(context_text),
        file_reduction_percent=reduction,
        selected_file_paths=selected_file_paths,
        max_file_budget=max_file_budget,
        context_budget_usage_percent=context_budget_usage(context_files, max_file_budget),
        task=read_task(root),
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
            f"Context budget usage: {stats.context_budget_usage_percent:.1f}%",
            "",
        ]
    )


def stats_to_dict(stats: EfficiencyStats) -> dict[str, int | float]:
    return {
        "indexed_files": stats.indexed_files,
        "skipped_files": stats.skipped_files,
        "context_files": stats.context_files,
        "context_chars": stats.context_chars,
        "file_reduction_percent": stats.file_reduction_percent,
        "selected_file_paths": stats.selected_file_paths,
        "max_file_budget": stats.max_file_budget,
        "context_budget_usage_percent": stats.context_budget_usage_percent,
        "task": stats.task,
    }


def append_stats_history(root: Path) -> Path:
    history_path = stats_history_path(root)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    payload = stats_to_dict(collect_stats(root))
    payload["recorded_at"] = datetime.now(timezone.utc).isoformat()
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return history_path


def stats_history(root: Path, limit: int = 20) -> list[dict]:
    path = stats_history_path(root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows[-limit:]


def render_history(history: list[dict]) -> str:
    if not history:
        return "No stats history found.\n"
    reductions = [float(item.get("file_reduction_percent", 0.0)) for item in history]
    context_files = [int(item.get("context_files", 0)) for item in history]
    latest = history[-1]
    return "\n".join(
        [
            "NACM Stats History",
            f"Recent task count: {len(history)}",
            f"Average file reduction: {sum(reductions) / len(reductions):.1f}%",
            f"Average context files: {sum(context_files) / len(context_files):.1f}",
            f"Latest task: {latest.get('task', {}).get('text', '')}",
            f"Latest file reduction: {float(latest.get('file_reduction_percent', 0.0)):.1f}%",
            "",
        ]
    )


def stats_history_path(root: Path) -> Path:
    return agent_dir(root) / "reports" / "history" / "stats.jsonl"


def count_context_files(context_text: str) -> int:
    return len(selected_paths(context_text))


def selected_paths(context_text: str) -> list[str]:
    paths: set[str] = set()
    for line in context_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- `") and "` (score:" in stripped:
            paths.add(stripped.split("`", 2)[1])
        elif stripped.startswith("### `") and stripped.endswith("`"):
            paths.add(stripped.removeprefix("### `").removesuffix("`"))
    return sorted(paths)


def read_max_file_budget(context_text: str) -> int:
    for line in context_text.splitlines():
        if line.startswith("Included file budget: "):
            value = line.removeprefix("Included file budget: ").strip()
            try:
                return int(value)
            except ValueError:
                return 0
    return 0


def context_budget_usage(context_files: int, max_file_budget: int) -> float:
    if max_file_budget <= 0:
        return 0.0
    return (min(context_files, max_file_budget) / max_file_budget) * 100


def read_task(root: Path) -> dict[str, str]:
    current_task = agent_dir(root) / "sessions" / "current_task.md"
    task = {"id": "", "text": ""}
    if not current_task.exists():
        return task
    for line in current_task.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task ID: "):
            task["id"] = line.removeprefix("Task ID: ").strip()
        elif line.startswith("Task: "):
            task["text"] = line.removeprefix("Task: ").strip()
    return task


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
