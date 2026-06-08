from __future__ import annotations

from pathlib import Path

from nacm.constants import FORBIDDEN_PATHS
from nacm.utils.git import run_git
from nacm.utils.paths import agent_dir


def finalize(root: Path) -> Path:
    local_agent = agent_dir(root)
    reports = local_agent / "reports"
    sessions = local_agent / "sessions"
    reports.mkdir(parents=True, exist_ok=True)
    sessions.mkdir(parents=True, exist_ok=True)

    status = run_git(root, ["status", "--short", "--untracked-files=all"])
    diff_stat = run_git(root, ["diff", "--stat"])
    diff_names = run_git(root, ["diff", "--name-only"])
    changed_paths = _changed_paths_from_status(status) | set(diff_names.splitlines())
    touched_forbidden = sorted(path for path in changed_paths if _is_forbidden(path))

    report = render_report(status, diff_stat, changed_paths, touched_forbidden)
    latest = reports / "latest_report.md"
    latest.write_text(report, encoding="utf-8")
    (sessions / "recent_changes.md").write_text(report, encoding="utf-8")
    return latest


def render_report(
    status: str,
    diff_stat: str,
    changed_paths: set[str],
    touched_forbidden: list[str],
) -> str:
    lines = [
        "# NACM Task Report",
        "",
        "## Git Status",
        "",
        "```text",
        status or "No Git status output.",
        "```",
        "",
        "## Diff Stat",
        "",
        "```text",
        diff_stat or "No diff stat output.",
        "```",
        "",
        "## Changed Files",
        "",
    ]
    if changed_paths:
        lines.extend(f"- `{path}`" for path in sorted(changed_paths))
    else:
        lines.append("- None detected")
    lines.extend(["", "## Forbidden Path Check", ""])
    if touched_forbidden:
        lines.extend(f"- Warning: `{path}`" for path in touched_forbidden)
    else:
        lines.append("- No forbidden paths detected.")
    lines.extend(["", "## Review Recommendation", ""])
    lines.append("- Review manually if this task changed more files than expected.")
    lines.append("")
    return "\n".join(lines)


def _changed_paths_from_status(status: str) -> set[str]:
    paths: set[str] = set()
    for line in status.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.add(path.replace("\\", "/"))
    return paths


def _is_forbidden(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized == item.rstrip("/") or normalized.startswith(item) for item in FORBIDDEN_PATHS)
