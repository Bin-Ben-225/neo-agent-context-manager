# Hooks

NACM can install project-local prompt submission hooks for Codex and Claude Code. A hook lets the agent trigger NACM as you send a task, so you do not need to run `nacm quick` and paste a prompt manually.

The hook remains local-first:

- It reads hook input from stdin.
- It writes `.agent/sessions/context_pack.md`.
- It writes the selected local prompt target under `.agent/`.
- It returns a short `additionalContext` message telling the agent to read the generated context pack.
- It does not upload source code, read credentials, run a background service, or make Git commits.

## Install

Run these commands inside the project where you want NACM enabled:

```bash
nacm hook install --target codex
nacm hook install --target claude-code
nacm hook status
```

Project-local config files are written to:

- Codex: `.codex/hooks.json`
- Claude Code: `.claude/settings.local.json`

When the project is a Git repository, NACM adds these local files and `.agent/` to `.git/info/exclude`.

## Runtime Behavior

When the agent sends a `UserPromptSubmit` hook event, NACM:

1. Reads the submitted prompt and working directory from stdin JSON.
2. Initializes `.agent/` if needed.
3. Builds the local index if needed.
4. Saves the submitted prompt as the current task.
5. Generates `.agent/sessions/context_pack.md`.
6. Writes the target prompt file.
7. Returns hook JSON containing `hookSpecificOutput.additionalContext`.

## Commands

```bash
nacm hook install --target codex
nacm hook install --target claude-code
nacm hook status
nacm hook uninstall --target codex
nacm hook uninstall --target claude-code
```

Advanced manual run:

```bash
echo '{"cwd":"/path/to/project","prompt":"fix image loading"}' | nacm hook run --target codex
```

`hook run` prints JSON only, which keeps it suitable for agent hook execution.
