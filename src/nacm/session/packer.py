from __future__ import annotations

from pathlib import Path

from nacm.constants import FORBIDDEN_PATHS
from nacm.config import load_profile
from nacm.indexer.matcher import match_files
from nacm.session.task import read_current_task
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
    lines = [
        "# NACM Context Pack",
        "",
        "## Current Task",
        "",
        task,
        "",
        "## Task Mode",
        "",
        "Small Change Mode unless the work clearly needs a plan first.",
        "",
        "## Relevant Files",
        "",
    ]
    for confidence in ("High", "Medium", "Low"):
        group = [item for item in matched if item["confidence"] == confidence]
        lines.append(f"### {confidence} Confidence")
        if group:
            for item in group:
                lines.append(f"- `{item['path']}` (score: {item['score']})")
                lines.extend(render_file_summary(item))
        else:
            lines.append("- None")
        lines.append("")
    if not matched:
        lines.extend(
            [
                "## No Match Guidance",
                "",
                "No relevant files matched this task.",
                "Use a scoped search before reading additional files.",
                "Start from likely filenames, module names, or task keywords.",
                "Do not scan the whole repository unless the user approves.",
                "",
            ]
        )
    lines.extend(
        [
            "## Forbidden Paths",
            "",
            *[f"- `{path}`" for path in FORBIDDEN_PATHS],
            "",
            "## Suggested Scoped Search",
            "",
            "- Start with High Confidence files.",
            "- If needed, search only related directories from the relevant file list.",
            "- Avoid full repository scans by default.",
            "",
            "## Suggested Commands",
            "",
            "```bash",
            "rg \"<keyword>\" <high-confidence-file-or-directory>",
            "```",
            "",
            "## Device Constraints",
            "",
            "- Keep reads small and task-focused.",
            "- Avoid heavy builds, long tests, and broad scans unless the user approves.",
            "",
            "## Completion Criteria",
            "",
            "- Implement the requested task.",
            "- Keep changes scoped to relevant files.",
            "- Remind the user to run `nacm done`.",
            "",
        ]
    )
    content = "\n".join(lines)
    return content[:max_chars]


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
    return "\n".join(
        [
            "You are working in a project prepared by NACM.",
            "",
            "First read `.agent/sessions/context_pack.md`.",
            "Prioritize High Confidence files from the context pack.",
            "Do not scan the whole repository by default.",
            "Do not read forbidden paths listed in the context pack.",
            "Do not commit `.agent/`.",
            "Do not create or modify the repository root AGENTS.md.",
            "Before editing, provide a short plan.",
            "If the task requires broad changes, enter Plan Mode first.",
            "When finished, remind the user to run `nacm done`.",
            "",
        ]
    )
