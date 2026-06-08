from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from nacm.adapters.codex import copy_codex_prompt
from nacm.indexer.scanner import build_index
from nacm.session.finalizer import finalize
from nacm.session.packer import build_context_pack
from nacm.session.task import save_task
from nacm.workspace import init_workspace

app = typer.Typer(no_args_is_help=True)
index_app = typer.Typer(no_args_is_help=True)
app.add_typer(index_app, name="index")
console = Console()


@app.command("init")
def init_command(profile: str = typer.Option("low-memory", "--profile")) -> None:
    result = init_workspace(Path.cwd(), profile=profile)
    console.print(f"Initialized NACM workspace at {result.agent_path}")
    if result.wrote_git_exclude:
        console.print("Ensured .agent/ is listed in .git/info/exclude")


@index_app.command("build")
def index_build(profile: str = typer.Option("low-memory", "--profile")) -> None:
    require_initialized(Path.cwd())
    result = build_index(Path.cwd(), profile=profile)
    console.print(
        f"Indexed {result['meta']['scanned_files']} files; skipped {result['meta']['skipped_files']} files."
    )


@app.command("task")
def task_command(text: str) -> None:
    require_initialized(Path.cwd())
    task = save_task(Path.cwd(), text)
    console.print(f"Saved task {task['id']}")


@app.command("pack")
def pack_command(target: str = typer.Option("codex", "--target")) -> None:
    require_initialized(Path.cwd())
    require_index(Path.cwd())
    try:
        result = build_context_pack(Path.cwd(), target=target)
    except ValueError as exc:
        fail(str(exc))
    console.print(f"Wrote context pack: {result['context_pack']}")
    if target == "codex":
        console.print(f"Wrote Codex prompt: {result['codex_prompt']}")


@app.command("copy")
def copy_command(target: str) -> None:
    require_initialized(Path.cwd())
    if target != "codex":
        raise typer.BadParameter("Only `codex` is supported in Phase 1.")
    try:
        ok, prompt_path, error = copy_codex_prompt(Path.cwd())
    except FileNotFoundError as exc:
        fail(str(exc))
    if ok:
        console.print("Copied Codex prompt to clipboard.")
    else:
        console.print(f"Could not copy prompt: {error}")
        console.print(f"Prompt file: {prompt_path}")


@app.command("quick")
def quick_command(text: str) -> None:
    require_initialized(Path.cwd())
    require_index(Path.cwd())
    save_task(Path.cwd(), text)
    build_context_pack(Path.cwd(), target="codex")
    ok, prompt_path, error = copy_codex_prompt(Path.cwd())
    if ok:
        console.print("Generated context pack and copied Codex prompt.")
    else:
        console.print(f"Generated context pack. Clipboard copy failed: {error}")
        console.print(f"Prompt file: {prompt_path}")


@app.command("done")
def done_command() -> None:
    require_initialized(Path.cwd())
    report = finalize(Path.cwd())
    console.print(f"Wrote report: {report}")


@app.command("finalize")
def finalize_command() -> None:
    done_command()


def main() -> None:
    app()


def require_initialized(root: Path) -> None:
    if not (root / ".agent").is_dir():
        fail("NACM workspace not found. Run `nacm init` first.")


def require_index(root: Path) -> None:
    if not (root / ".agent" / "index" / "file_summary.json").is_file():
        fail("NACM index not found. Run `nacm index build` first.")


def fail(message: str) -> None:
    console.print(message)
    raise typer.Exit(code=1)
