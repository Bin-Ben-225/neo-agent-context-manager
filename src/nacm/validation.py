from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from nacm.adapters.codex import copy_codex_prompt, write_codex_prompt
from nacm.indexer.scanner import build_index
from nacm.session.finalizer import finalize
from nacm.session.packer import build_context_pack
from nacm.session.task import save_task
from nacm.workspace import init_workspace


def run_smoke_validation() -> Path:
    root = Path(tempfile.mkdtemp(prefix="nacm-smoke-"))
    _run_git(root, ["init"])
    _run_git(root, ["config", "user.name", "Smoke Test"])
    _run_git(root, ["config", "user.email", "smoke@example.com"])

    src = root / "src"
    src.mkdir()
    (src / "images.py").write_text("def load_image(path):\n    return path\n", encoding="utf-8")
    _run_git(root, ["add", "src/images.py"])
    _run_git(root, ["commit", "-m", "add image loader"])

    init_workspace(root, profile="low-memory")
    build_index(root, profile="low-memory")
    save_task(root, "fix src/images.py image loading failure")
    build_context_pack(root, target="codex")
    write_codex_prompt(root)
    copy_codex_prompt(root)

    (src / "new_feature.py").write_text("def feature():\n    return True\n", encoding="utf-8")
    finalize(root)

    _assert_smoke_outputs(root)
    return root


def _run_git(root: Path, args: list[str]) -> None:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {details}")


def _assert_smoke_outputs(root: Path) -> None:
    required_paths = [
        root / ".agent" / "config.toml",
        root / ".agent" / "index" / "file_summary.json",
        root / ".agent" / "sessions" / "context_pack.md",
        root / ".agent" / "codex" / "codex_prompt.md",
        root / ".agent" / "reports" / "latest_report.md",
    ]
    missing = [path for path in required_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"smoke validation missing output: {missing[0]}")

    context = (root / ".agent" / "sessions" / "context_pack.md").read_text(encoding="utf-8")
    prompt = (root / ".agent" / "codex" / "codex_prompt.md").read_text(encoding="utf-8")
    report = (root / ".agent" / "reports" / "latest_report.md").read_text(encoding="utf-8")
    exclude = (root / ".git" / "info" / "exclude").read_text(encoding="utf-8")

    checks = [
        ".agent/" in exclude,
        "Functions: load_image" in context,
        "First read `.agent/sessions/context_pack.md`." in prompt,
        "Changed file count: 1" in report,
    ]
    if not all(checks):
        raise RuntimeError("smoke validation output checks failed")
