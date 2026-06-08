from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from nacm.indexer.matcher import extract_keywords
from nacm.utils.paths import agent_dir


def save_task(root: Path, text: str) -> dict:
    sessions = agent_dir(root) / "sessions"
    sessions.mkdir(parents=True, exist_ok=True)
    task = {
        "id": datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S"),
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
    return task


def read_current_task(root: Path) -> str:
    path = agent_dir(root) / "sessions" / "current_task.md"
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Task: "):
            return line.removeprefix("Task: ").strip()
    return ""
