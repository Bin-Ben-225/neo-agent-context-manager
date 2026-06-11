from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from nacm.indexer.matcher import extract_keywords
from nacm.utils.paths import agent_dir


def create_batch_plan(root: Path, goal: str) -> Path:
    batches = agent_dir(root) / "sessions" / "batches"
    batches.mkdir(parents=True, exist_ok=True)
    plan = render_batch_plan(goal)
    latest = batches / "latest_plan.md"
    latest.write_text(plan, encoding="utf-8")
    stamped = batches / f"plan-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.md"
    stamped.write_text(plan, encoding="utf-8")
    return latest


def render_batch_plan(goal: str) -> str:
    keywords = extract_keywords(goal)
    focus = ", ".join(keywords[:6]) or "the requested change"
    suggested = [
        f"Inspect current behavior around {focus}.",
        f"Implement the smallest safe change for {focus}.",
        f"Run focused tests and then `nacm done` for {focus}.",
    ]
    lines = [
        "# NACM Batch Plan",
        "",
        "## Goal",
        "",
        goal,
        "",
        "## Suggested Tasks",
        "",
    ]
    lines.extend(f"{index}. {task}" for index, task in enumerate(suggested, start=1))
    lines.extend(
        [
            "",
            "## How To Execute",
            "",
            "Run one task at a time with `nacm quick \"<task>\"`.",
            "Paste the generated Codex prompt before moving to the next task.",
            "Run `nacm done` after each completed task.",
            "",
            "## Safety",
            "",
            "NACM will not execute these tasks automatically.",
            "Keep changes scoped and rebuild the index when source structure changes.",
            "",
        ]
    )
    return "\n".join(lines)
