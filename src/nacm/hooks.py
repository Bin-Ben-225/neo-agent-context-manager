from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from nacm.adapters.registry import write_prompt
from nacm.indexer.scanner import build_index
from nacm.session.packer import build_context_pack
from nacm.session.task import save_task
from nacm.utils.git import ensure_info_exclude
from nacm.utils.paths import agent_dir
from nacm.workspace import init_workspace

HOOK_EVENT = "UserPromptSubmit"
DEFAULT_HOOK_TIMEOUT_SECONDS = 120
POSIX_HOOK_COMMANDS = {
    "claude-code": "python3 -m nacm hook run --target claude-code",
    "codex": "python3 -m nacm hook run --target codex",
}
WINDOWS_HOOK_COMMANDS = {
    "claude-code": "py -3.11 -m nacm hook run --target claude-code",
    "codex": "py -3.11 -m nacm hook run --target codex",
}
PROMPT_TARGETS = {
    "claude-code": "claude-prompt",
    "codex": "codex",
}


def process_user_prompt_hook(payload: dict[str, Any], target: str = "codex") -> dict[str, Any]:
    prompt_target = prompt_target_for(target)
    event_name = str(payload.get("hook_event_name") or HOOK_EVENT)
    if event_name != HOOK_EVENT:
        return hook_output(f"NACM hook skipped unsupported event `{event_name}`.")

    root = Path(str(payload.get("cwd") or Path.cwd())).expanduser()
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt:
        return hook_output("NACM did not receive prompt text; continue with normal repository context.")

    ensure_workspace_ready(root)
    save_task(root, prompt)
    build_context_pack(root, target=prompt_target, max_files=5, include_explanations=True)
    prompt_path = write_prompt(root, prompt_target)

    return hook_output(
        "\n".join(
            [
                "NACM prepared context for this prompt.",
                "Read `.agent/sessions/context_pack.md` first.",
                f"Prompt target: `{prompt_target}`.",
                f"Prompt file: `{relative_posix(root, prompt_path)}`.",
                "Start with High Confidence files and avoid broad repository scans unless needed.",
            ]
        )
    )


def install_hook(root: Path, target: str) -> Path:
    config_path = hook_config_path(root, target)
    config = read_json_object(config_path)
    command = hook_command_for(target)
    entry: dict[str, Any] = {
        "type": "command",
        "command": command,
        "commandWindows": windows_hook_command_for(target),
        "timeout": DEFAULT_HOOK_TIMEOUT_SECONDS,
    }
    if target == "codex":
        entry["statusMessage"] = "Preparing NACM context"

    config["hooks"] = add_command_hook(config.get("hooks"), command, entry)
    write_json_object(config_path, config)
    exclude_local_hook_files(root)
    return config_path


def uninstall_hook(root: Path, target: str) -> Path:
    config_path = hook_config_path(root, target)
    config = read_json_object(config_path)
    hooks = config.get("hooks")
    for command in known_hook_commands_for(target):
        hooks = remove_command_hook(hooks, command)
    config["hooks"] = hooks
    if not config["hooks"]:
        config.pop("hooks")
    write_json_object(config_path, config)
    return config_path


def hook_status(root: Path) -> dict[str, bool]:
    return {
        target: any(
            command in hook_config_path(root, target).read_text(encoding="utf-8")
            for command in known_hook_commands_for(target)
        )
        if hook_config_path(root, target).exists()
        else False
        for target in sorted(PROMPT_TARGETS)
    }


def ensure_workspace_ready(root: Path) -> None:
    if not agent_dir(root).is_dir():
        init_workspace(root)
    if not (agent_dir(root) / "index" / "file_summary.json").is_file():
        build_index(root)


def hook_output(additional_context: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": HOOK_EVENT,
            "additionalContext": additional_context,
        },
        "systemMessage": "NACM context prepared.",
    }


def hook_config_path(root: Path, target: str) -> Path:
    if target == "claude-code":
        return root / ".claude" / "settings.local.json"
    if target == "codex":
        return root / ".codex" / "hooks.json"
    raise ValueError(f"Unsupported hook target `{target}`. Supported targets: {supported_targets()}.")


def prompt_target_for(target: str) -> str:
    if target not in PROMPT_TARGETS:
        raise ValueError(f"Unsupported hook target `{target}`. Supported targets: {supported_targets()}.")
    return PROMPT_TARGETS[target]


def hook_command_for(target: str) -> str:
    if os.name == "nt":
        return windows_hook_command_for(target)
    if target not in POSIX_HOOK_COMMANDS:
        raise ValueError(f"Unsupported hook target `{target}`. Supported targets: {supported_targets()}.")
    return POSIX_HOOK_COMMANDS[target]


def windows_hook_command_for(target: str) -> str:
    if target not in WINDOWS_HOOK_COMMANDS:
        raise ValueError(f"Unsupported hook target `{target}`. Supported targets: {supported_targets()}.")
    return WINDOWS_HOOK_COMMANDS[target]


def known_hook_commands_for(target: str) -> list[str]:
    commands = [hook_command_for(target), windows_hook_command_for(target)]
    if target in POSIX_HOOK_COMMANDS:
        commands.append(POSIX_HOOK_COMMANDS[target])
    return list(dict.fromkeys(commands))


def supported_targets() -> str:
    return ", ".join(sorted(PROMPT_TARGETS))


def read_json_object(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Hook config must be a JSON object: {path}")
    return data


def write_json_object(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def add_command_hook(existing_hooks: Any, command: str, entry: dict[str, Any]) -> dict[str, Any]:
    hooks = existing_hooks if isinstance(existing_hooks, dict) else {}
    event_entries = hooks.get(HOOK_EVENT) if isinstance(hooks.get(HOOK_EVENT), list) else []
    clean_entries = remove_command_from_entries(event_entries, command)
    clean_entries.append({"hooks": [entry]})
    hooks[HOOK_EVENT] = clean_entries
    return hooks


def remove_command_hook(existing_hooks: Any, command: str) -> dict[str, Any]:
    hooks = existing_hooks if isinstance(existing_hooks, dict) else {}
    event_entries = hooks.get(HOOK_EVENT) if isinstance(hooks.get(HOOK_EVENT), list) else []
    remaining = remove_command_from_entries(event_entries, command)
    if remaining:
        hooks[HOOK_EVENT] = remaining
    else:
        hooks.pop(HOOK_EVENT, None)
    return hooks


def remove_command_from_entries(entries: list[Any], command: str) -> list[Any]:
    remaining_entries: list[Any] = []
    for item in entries:
        if not isinstance(item, dict):
            remaining_entries.append(item)
            continue
        item_hooks = item.get("hooks")
        if not isinstance(item_hooks, list):
            remaining_entries.append(item)
            continue
        filtered_hooks = [
            hook
            for hook in item_hooks
            if not (isinstance(hook, dict) and hook.get("command") == command)
        ]
        if filtered_hooks:
            remaining_entries.append({**item, "hooks": filtered_hooks})
    return remaining_entries


def exclude_local_hook_files(root: Path) -> None:
    ensure_info_exclude(root, ".agent/")
    ensure_info_exclude(root, ".claude/settings.local.json")
    ensure_info_exclude(root, ".codex/hooks.json")


def relative_posix(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
