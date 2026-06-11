from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from nacm.indexer.matcher import extract_keywords
from nacm.utils.paths import agent_dir


def save_task(root: Path, text: str) -> dict:
    sessions = agent_dir(root) / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    task = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"),
        "text": text,
        "keywords": extract_keywords(text),
    }
    lines = [
        "# Current Task",
        "",
        f"Task ID: {task['id']}",
        f"Task: {task['text']}",
        f"Keywords: {', '.join(task['keywords'])}",
        "",
    ]
    (sessions / "current_task.md").write_text("\n".join(lines), encoding="utf-8")
    append_task_history(root, task)
    return task


def read_current_task(root: Path) -> str:
    path = agent_dir(root) / "sessions" / "current_task.md"
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task: "):
            return line.removeprefix("Task: ").strip()
    return ""


def append_task_history(root: Path, task: dict) -> None:
    history = task_history_path(root)
    history.parent.mkdir(parents=True, exist_ok=True)
    with history.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(task, ensure_ascii=False) + "\n")


def list_tasks(root: Path, limit: int = 20) -> list[dict]:
    history = task_history_path(root)
    if not history.exists():
        return []
    tasks = []
    for line in history.read_text(encoding="utf-8").splitlines():
        if line.strip():
            tasks.append(json.loads(line))
    return tasks[-limit:]


def latest_task(root: Path) -> dict | None:
    tasks = list_tasks(root, limit=1)
    return tasks[-1] if tasks else None


def task_history_path(root: Path) -> Path:
    return agent_dir(root) / "sessions" / "history" / "tasks.jsonl"
