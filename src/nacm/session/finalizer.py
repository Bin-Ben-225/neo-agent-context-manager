from __future__ import annotations

import json
from pathlib import Path

from nacm.config import load_profile
from nacm.constants import FORBIDDEN_PATHS, SOURCE_EXTENSIONS
from nacm.session.stats import collect_stats, render_stats
from nacm.utils.git import is_git_repo, run_git
from nacm.utils.paths import agent_dir


def finalize(root: Path) -> Path:
    local_agent = agent_dir(root)
    reports = local_agent / "reports"
    sessions = local_agent / "sessions"
    cache = local_agent / "cache"
    reports.mkdir(parents=True, exist_ok=True)
    sessions.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)

    status = run_git(root, ["status", "--short", "--untracked-files=all"])
    diff_stat = run_git(root, ["diff", "--stat"])
    diff_names = run_git(root, ["diff", "--name-only"])
    classified = _classify_status(status)
    changed_paths = _all_changed_paths(classified) | {path for path in diff_names.splitlines() if path}
    touched_forbidden = sorted(path for path in changed_paths if _is_forbidden(path))
    profile = load_profile(root)
    large_change = len(changed_paths) > profile.max_files_in_context
    git_available = is_git_repo(root)
    index_dirty = _is_index_dirty(changed_paths)

    if index_dirty:
        (cache / "index_state.json").write_text(
            json.dumps(
                {
                    "dirty": True,
                    "reason": "Project files changed after last index build",
                    "changed_files": sorted(changed_paths),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    report = render_report(
        status=status,
        diff_stat=diff_stat,
        classified=classified,
        changed_paths=changed_paths,
        touched_forbidden=touched_forbidden,
        large_change=large_change,
        git_available=git_available,
        index_dirty=index_dirty,
        efficiency_summary=render_stats(collect_stats(root)),
    )
    latest = reports / "latest_report.md"
    latest.write_text(report, encoding="utf-8")
    (sessions / "recent_changes.md").write_text(report, encoding="utf-8")
    return latest


def render_report(
    status: str,
    diff_stat: str,
    classified: dict[str, list[str]],
    changed_paths: set[str],
    touched_forbidden: list[str],
    large_change: bool,
    git_available: bool,
    index_dirty: bool,
    efficiency_summary: str = "",
) -> str:
    lines = [
        "# NACM Task Report",
        "",
        "## Summary",
        "",
        f"Changed file count: {len(changed_paths)}",
        f"Large Change Risk: {'yes' if large_change else 'no'}",
        f"Index Dirty: {'yes' if index_dirty else 'no'}",
        "",
        "## Efficiency Summary",
        "",
        efficiency_summary.strip() or "No context pack stats available.",
        "",
        "## Git Status",
        "",
        "```text",
        status or ("No Git status output." if git_available else "Git metadata unavailable."),
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
    lines.extend(_render_file_group("Modified Files", classified["modified"]))
    lines.extend(_render_file_group("Added Or Untracked Files", classified["added"]))
    lines.extend(_render_file_group("Deleted Files", classified["deleted"]))
    lines.extend(_render_file_group("Renamed Files", classified["renamed"]))
    lines.extend(["", "## Forbidden Path Check", ""])
    if touched_forbidden:
        lines.append("Forbidden paths touched:")
        lines.extend(f"- `{path}`" for path in touched_forbidden)
    else:
        lines.append("- No forbidden paths detected.")
    lines.extend(["", "## Review Recommendation", ""])
    if large_change:
        lines.append("- Recommendation: enter review-large-change before continuing.")
    else:
        lines.append("- Review changed files manually before continuing.")
    lines.extend(["", "## Next Action", ""])
    if not git_available:
        lines.append("- Initialize Git if you want NACM to inspect changed files.")
    elif index_dirty:
        lines.append("- Run `nacm index build` if project structure or symbols changed.")
    else:
        lines.append("- Continue with the next task when the changes look correct.")
    lines.append("")
    return "\n".join(lines)


def _classify_status(status: str) -> dict[str, list[str]]:
    classified: dict[str, list[str]] = {
        "modified": [],
        "added": [],
        "deleted": [],
        "renamed": [],
    }
    for line in status.splitlines():
        if not line.strip():
            continue
        code = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            classified["renamed"].append(path.split(" -> ", 1)[1].replace("\\", "/"))
            continue
        normalized = path.replace("\\", "/")
        if code == "??" or "A" in code:
            classified["added"].append(normalized)
        elif "D" in code:
            classified["deleted"].append(normalized)
        elif "M" in code:
            classified["modified"].append(normalized)
    return {key: sorted(set(paths)) for key, paths in classified.items()}


def _all_changed_paths(classified: dict[str, list[str]]) -> set[str]:
    paths: set[str] = set()
    for group in classified.values():
        paths.update(group)
    return paths


def _render_file_group(title: str, paths: list[str]) -> list[str]:
    lines = [f"### {title}"]
    if paths:
        lines.extend(f"- `{path}`" for path in paths)
    else:
        lines.append("- None")
    lines.append("")
    return lines


def _is_index_dirty(changed_paths: set[str]) -> bool:
    return any(
        (not _is_forbidden(path)) and Path(path).suffix.lower() in SOURCE_EXTENSIONS
        for path in changed_paths
    )


def _is_forbidden(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return any(normalized == item.rstrip("/") or normalized.startswith(item) for item in FORBIDDEN_PATHS)
