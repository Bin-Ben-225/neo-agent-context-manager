from __future__ import annotations

import subprocess
from pathlib import Path


def is_git_repo(root: Path) -> bool:
    return (root / ".git").exists()


def ensure_info_exclude(root: Path, line: str = ".agent/") -> bool:
    info_dir = root / ".git" / "info"
    if not info_dir.exists():
        return False
    exclude_file = info_dir / "exclude"
    existing = exclude_file.read_text(encoding="utf-8") if exclude_file.exists() else ""
    if line in existing.splitlines():
        return True
    suffix = "" if existing.endswith("\n") or not existing else "\n"
    exclude_file.write_text(f"{existing}{suffix}{line}\n", encoding="utf-8")
    return True


def run_git(root: Path, args: list[str]) -> str:
    if not is_git_repo(root):
        return ""
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.rstrip()
