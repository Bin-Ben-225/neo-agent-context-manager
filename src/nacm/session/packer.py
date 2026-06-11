from __future__ import annotations

from pathlib import Path

from nacm.constants import FORBIDDEN_PATHS
from nacm.config import load_profile
from nacm.indexer.matcher import match_files
from nacm.session.task import read_current_task
from nacm.templates.renderer import render_template
from nacm.utils.paths import agent_dir


def build_context_pack(
    root: Path,
    target: str = "codex",
    profile_name: str = "low-memory",
    max_files: int | None = None,
    include_explanations: bool = False,
) -> dict:
    task = read_current_task(root)
    if not task:
        raise ValueError("No current task. Run `nacm task \"...\"` first.")
    profile = load_profile(root, profile_name)
    matched = match_files(root, task, limit=max_files or profile.max_files_in_context)
    local_agent = agent_dir(root)
    sessions = local_agent / "sessions"
    codex_dir = local_agent / "codex"
    sessions.mkdir(parents=True, exist_ok=True)
    codex_dir.mkdir(parents=True, exist_ok=True)

    context = render_context_pack(
        task,
        matched,
        max_chars=profile.max_context_chars,
        max_files=max_files or profile.max_files_in_context,
        include_explanations=include_explanations,
    )
    (sessions / "context_pack.md").write_text(context, encoding="utf-8")
    return {"context_pack": sessions / "context_pack.md"}


def render_context_pack(
    task: str,
    matched: list[dict],
    max_chars: int = 30000,
    max_files: int = 8,
    include_explanations: bool = False,
) -> str:
    prepared = prepare_matched_files(matched)
    content = render_template(
        "context_pack.md.j2",
        {
            "task": task,
            "matched": prepared,
            "confidence_groups": group_by_confidence(prepared),
            "forbidden_paths": FORBIDDEN_PATHS,
            "max_files": max_files,
            "include_explanations": include_explanations,
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
    methods = _join_limited(item.get("methods", []), 8)
    test_functions = _join_limited(item.get("test_functions", []), 8)
    exports = _join_limited(item.get("exports", []), 8)
    keywords = _join_limited(item.get("keywords", []), 10)
    reasons = _join_limited(item.get("reasons", []), 6)
    if imports:
        lines.append(f"  - Imports: {imports}")
    if classes:
        lines.append(f"  - Classes: {classes}")
    if functions:
        lines.append(f"  - Functions: {functions}")
    if methods:
        lines.append(f"  - Methods: {methods}")
    if test_functions:
        lines.append(f"  - Tests: {test_functions}")
    if exports:
        lines.append(f"  - Exports: {exports}")
    if keywords:
        lines.append(f"  - Keywords: {keywords}")
    if reasons:
        lines.append(f"  - Match reasons: {reasons}")
    return lines


def _join_limited(values: list[str], limit: int) -> str:
    clean = [str(value) for value in values if value]
    return ", ".join(clean[:limit])
