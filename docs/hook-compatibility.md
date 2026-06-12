# Hook Compatibility Notes

This document records observed hook behavior for supported local targets. It is intentionally practical: the goal is to keep NACM hook execution predictable across agent surfaces without adding background services or remote dependencies.

## Shared Contract

NACM expects prompt submission hooks to provide stdin JSON with:

- `cwd`: project working directory
- `hook_event_name`: `UserPromptSubmit`
- `prompt`: submitted user prompt

Extra fields are ignored. NACM returns JSON with `hookSpecificOutput.hookEventName` and `hookSpecificOutput.additionalContext`.

## Claude Code Terminal

Observed on Windows with Claude Code `2.1.174`.

Captured `UserPromptSubmit` stdin shape:

```json
{
  "session_id": "...",
  "transcript_path": "...",
  "cwd": "C:\\path\\to\\project",
  "permission_mode": "default",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "NACM payload capture: say ok"
}
```

Observed behavior:

- `.claude/settings.local.json` is loaded in non-interactive `claude -p` mode.
- `--include-hook-events --output-format stream-json` emits `hook_started` and `hook_response` system messages.
- Claude Code validates NACM's JSON output and accepts `additionalContext`.
- A later authentication failure still leaves the hook result intact; NACM had already generated `.agent/sessions/context_pack.md`.
- `--max-budget-usd 0` is rejected before hooks run; use a positive value for hook validation.

## Codex Desktop

Observed on Windows with the installed Codex desktop package.

- `Get-Command codex` resolves to a WindowsApps packaged `codex.exe`.
- Direct terminal invocation of `codex --help` returned `Access is denied`, so this environment could not drive an end-to-end Codex desktop prompt submission from automation.
- NACM writes `.codex/hooks.json` with both `command` and `commandWindows` fields, plus a longer timeout for first-run index creation.
- NACM's runner was validated with a Codex-shaped payload containing `cwd`, `hook_event_name`, `prompt`, `model`, and `turn_id`; extra fields are ignored.

Simulated Codex-shaped payload:

```json
{
  "cwd": "C:\\path\\to\\project",
  "hook_event_name": "UserPromptSubmit",
  "prompt": "Codex payload validation: inspect src/app.py",
  "model": "gpt-5-codex",
  "turn_id": "turn-validation"
}
```

## Timeout And Errors

Installed hooks use a 120 second timeout. This gives first-run index creation room to finish while still bounding agent startup delay.

`nacm hook run` prints JSON only. If it receives invalid JSON or hits a runtime error, it returns a skipped `additionalContext` message instead of printing a Python traceback.
