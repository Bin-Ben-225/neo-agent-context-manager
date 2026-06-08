from __future__ import annotations

from pathlib import Path

from nacm.constants import FORBIDDEN_PATHS
from nacm.indexer.matcher import match_files
from nacm.session.task import read_current_task
from nacm.utils.paths import agent_dir


def build_context_pack(root: Path, target: str = "codex") -> dict:
    task = read_current_task(root)
    if not task:
        raise ValueError("No current task. Run `nacm task \"...\"` first.")
    matched = match_files(root, task)
    local_agent = agent_dir(root)
    sessions = local_agent / "sessions"
    codex_dir = local_agent / "codex"
    sessions.mkdir(parents=True, exist_ok=True)
    codex_dir.mkdir(parents=True, exist_ok=True)

    context = render_context_pack(task, matched)
    prompt = render_codex_prompt()
    (sessions / "context_pack.md").write_text(context, encoding="utf-8")
    if target == "codex":
        (codex_dir / "codex_prompt.md").write_text(prompt, encoding="utf-8")
    return {"context_pack": sessions / "context_pack.md", "codex_prompt": codex_dir / "codex_prompt.md"}


def render_context_pack(task: str, matched: list[dict]) -> str:
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
        else:
            lines.append("- None")
        lines.append("")
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
    return content[:30_000]


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
