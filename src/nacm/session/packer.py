from __future__ import annotations

from pathlib import Path

from nacm.constants import FORBIDDEN_PATHS
from nacm.config import load_profile
from nacm.indexer.matcher import match_files
from nacm.session.task import read_current_task
from nacm.templates.renderer import render_template
from nacm.utils.paths import agent_dir


def build_context_pack(root: Path, target: str = "codex", profile_name: str = "low-memory") -> dict:
    task = read_current_task(root)
    if not task:
        raise ValueError("No current task. Run `nacm task \"...\"` first.")
    profile = load_profile(root, profile_name)
    matched = match_files(root, task)
    local_agent = agent_dir(root)
    sessions = local_agent / "sessions"
    codex_dir = local_agent / "codex"
    sessions.mkdir(parents=True, exist_ok=True)
    codex_dir.mkdir(parents=True, exist_ok=True)

    context = render_context_pack(task, matched, max_chars=profile.max_context_chars)
    prompt = render_codex_prompt()
    (sessions / "context_pack.md").write_text(context, encoding="utf-8")
    if target == "codex":
        (codex_dir / "codex_prompt.md").write_text(prompt, encoding="utf-8")
    return {"context_pack": sessions / "context_pack.md", "codex_prompt": codex_dir / "codex_prompt.md"}


def render_context_pack(task: str, matched: list[dict], max_chars: int = 30000) -> str:
    prepared = prepare_matched_files(matched)
    content = render_template(
        "context_pack.md.j2",
        {
            "task": task,
            "matched": prepared,
            "confidence_groups": group_by_confidence(prepared),
            "forbidden_paths": FORBIDDEN_PATHS,
        },
    )
    return content[:max_chars]


def prepare_matched_files(matched: list[dict]) -> list[dict]:
    return [{**item, "summary_lines": render_file_summary(item)} for item in matched]


def group_by_confidence(matched: list[dict]) -> dict[str, list[dict]]:
    return {
        confidence: [item for item in matched if item["confidence"] == confidence]
        for confidence in ("High", "Medium", "Low")
    }


def render_file_summary(item: dict) -> list[str]:
    lines = []
    imports = _join_limited(item.get("imports", []), 6)
    classes = _join_limited(item.get("classes", []), 6)
    functions = _join_limited(item.get("functions", []), 8)
    keywords = _join_limited(item.get("keywords", []), 10)
    reasons = _join_limited(item.get("reasons", []), 6)
    if imports:
        lines.append(f"  - Imports: {imports}")
    if classes:
        lines.append(f"  - Classes: {classes}")
    if functions:
        lines.append(f"  - Functions: {functions}")
    if keywords:
        lines.append(f"  - Keywords: {keywords}")
    if reasons:
        lines.append(f"  - Match reasons: {reasons}")
    return lines


def _join_limited(values: list[str], limit: int) -> str:
    clean = [str(value) for value in values if value]
    return ", ".join(clean[:limit])


def render_codex_prompt() -> str:
    return render_template("codex_prompt.md.j2", {})
