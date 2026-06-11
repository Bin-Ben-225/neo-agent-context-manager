from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from nacm.constants import DEFAULT_PROFILE, IGNORED_DIRS, IGNORED_PREFIXES
from nacm.config import load_profile
from nacm.indexer.summary import summarize_file
from nacm.indexer.relations import build_relation_index, render_relation_index
from nacm.utils.paths import agent_dir, has_ignored_part, to_posix_relative


def build_index(root: Path, profile: str = DEFAULT_PROFILE) -> dict:
    local_agent = agent_dir(root)
    index_dir = local_agent / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    loaded_profile = load_profile(root, profile)

    files: list[dict] = []
    skipped = 0
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relative = to_posix_relative(path, root)
        if has_ignored_part(relative, IGNORED_DIRS, IGNORED_PREFIXES):
            skipped += 1
            continue
        summary = summarize_file(path, max_head_kb=loaded_profile.max_file_head_kb)
        files.append(
            {
                "path": relative,
                "mtime": path.stat().st_mtime,
                "depth": len(Path(relative).parts) - 1,
                **summary,
            }
        )

    payload = {"files": files}
    meta = {
        "indexed_at": datetime.now(timezone.utc).isoformat(),
        "profile": loaded_profile.name,
        "scanned_files": len(files),
        "skipped_files": skipped,
    }
    (index_dir / "file_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (index_dir / "index_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    (index_dir / "project_map.md").write_text(render_project_map(files), encoding="utf-8")
    (index_dir / "module_index.md").write_text(render_module_index(files), encoding="utf-8")
    if loaded_profile.name == "workstation":
        relations = build_relation_index(files)
        (index_dir / "relation_index.json").write_text(
            json.dumps(relations, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (index_dir / "relation_index.md").write_text(render_relation_index(relations), encoding="utf-8")
    return {"files": files, "meta": meta}


def render_project_map(files: list[dict]) -> str:
    lines = ["# Project Map", ""]
    for item in files:
        lines.append(f"- `{item['path']}`")
    return "\n".join(lines) + "\n"


def render_module_index(files: list[dict]) -> str:
    lines = ["# Module Index", ""]
    for item in files:
        symbols = ", ".join(
            item["classes"]
            + item["functions"]
            + item.get("methods", [])
            + item.get("test_functions", [])
        ) or "no symbols"
        lines.append(f"- `{item['path']}`: {symbols}")
    return "\n".join(lines) + "\n"
