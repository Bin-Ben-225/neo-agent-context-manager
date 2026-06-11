from __future__ import annotations

from pathlib import Path
import sys

import typer
from rich.console import Console

from nacm.adapters.codex import copy_codex_prompt, write_codex_prompt
from nacm.indexer.matcher import match_files
from nacm.indexer.scanner import build_index
from nacm.session.finalizer import finalize
from nacm.session.packer import build_context_pack
from nacm.session.planner import create_batch_plan
from nacm.session.status import inspect_workspace, render_status
from nacm.session.task import latest_task, list_tasks, save_task
from nacm.validation import run_smoke_validation
from nacm.workspace import init_workspace

app = typer.Typer(no_args_is_help=True)
index_app = typer.Typer(no_args_is_help=True)
validate_app = typer.Typer(no_args_is_help=True)
match_app = typer.Typer(no_args_is_help=True)
task_app = typer.Typer(no_args_is_help=True)
app.add_typer(index_app, name="index")
app.add_typer(validate_app, name="validate")
app.add_typer(match_app, name="match")
app.add_typer(task_app, name="task")
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


@task_app.command("set")
def task_command(text: str) -> None:
    require_initialized(Path.cwd())
    task = save_task(Path.cwd(), text)
    console.print(f"Saved task {task['id']}")


@task_app.command("list")
def task_list_command(limit: int = typer.Option(20, "--limit")) -> None:
    require_initialized(Path.cwd())
    tasks = list_tasks(Path.cwd(), limit=limit)
    if not tasks:
        console.print("No task history found.")
        return
    for task in tasks:
        console.print(f"{task['id']}  {task['text']}")


@task_app.command("show")
def task_show_command(task_id: str = typer.Argument("latest")) -> None:
    require_initialized(Path.cwd())
    if task_id != "latest":
        fail("Only `latest` is supported for task show in the current version.")
    task = latest_task(Path.cwd())
    if not task:
        fail("No task history found.")
    console.print(f"Task ID: {task['id']}")
    console.print(f"Task: {task['text']}")
    console.print(f"Keywords: {', '.join(task['keywords'])}")


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
        prompt_path = write_codex_prompt(Path.cwd())
        console.print(f"Wrote Codex prompt: {prompt_path}")


@app.command("copy")
def copy_command(target: str) -> None:
    require_initialized(Path.cwd())
    if target != "codex":
        raise typer.BadParameter("Only `codex` is supported in the current version.")
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
    write_codex_prompt(Path.cwd())
    ok, prompt_path, error = copy_codex_prompt(Path.cwd())
    if ok:
        console.print("Generated context pack and copied Codex prompt.")
    else:
        console.print(f"Generated context pack. Clipboard copy failed: {error}")
        console.print(f"Prompt file: {prompt_path}")


@app.command("plan")
def plan_command(text: str) -> None:
    require_initialized(Path.cwd())
    plan_path = create_batch_plan(Path.cwd(), text)
    console.print(f"Wrote batch plan: {plan_path}")


@match_app.command("explain")
def match_explain_command(text: str, limit: int = typer.Option(8, "--limit")) -> None:
    require_initialized(Path.cwd())
    require_index(Path.cwd())
    matches = match_files(Path.cwd(), text, limit=limit)
    if not matches:
        console.print("No matches found.")
        return
    for item in matches:
        console.print(f"{item['path']} [{item['confidence']}, score {item['score']}]")
        for explanation in item.get("explanations", []):
            console.print(
                f"  - {explanation['signal']}: {explanation['detail']} "
                f"({explanation['weight']:+d})"
            )


@app.command("done")
def done_command() -> None:
    require_initialized(Path.cwd())
    report = finalize(Path.cwd())
    console.print(f"Wrote report: {report}")


@app.command("status")
def status_command() -> None:
    console.print(render_status(inspect_workspace(Path.cwd())))


@app.command("doctor")
def doctor_command() -> None:
    status = inspect_workspace(Path.cwd())
    if not status.workspace_ready:
        console.print("NACM workspace not found.")
        console.print("Run `nacm init --profile low-memory` first.")
        raise typer.Exit(code=1)
    if not status.index_ready:
        console.print("NACM index not found.")
        console.print("Run `nacm index build` first.")
        raise typer.Exit(code=1)
    console.print("NACM doctor passed.")


@validate_app.command("smoke")
def validate_smoke_command() -> None:
    try:
        smoke_path = run_smoke_validation()
    except RuntimeError as exc:
        fail(str(exc))
    console.print(f"Smoke passed: {smoke_path}")


@app.command("finalize")
def finalize_command() -> None:
    done_command()


def main() -> None:
    normalize_legacy_task_args()
    app()


def normalize_legacy_task_args() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "task" and sys.argv[2] not in {"set", "list", "show"}:
        sys.argv.insert(2, "set")


def require_initialized(root: Path) -> None:
    if not (root / ".agent").is_dir():
        fail("NACM workspace not found. Run `nacm init` first.")


def require_index(root: Path) -> None:
    if not (root / ".agent" / "index" / "file_summary.json").is_file():
        fail("NACM index not found. Run `nacm index build` first.")


def fail(message: str) -> None:
    console.print(message)
    raise typer.Exit(code=1)
