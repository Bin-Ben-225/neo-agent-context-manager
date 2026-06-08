# NACM Workflow

## First Use

```bash
nacm init --profile low-memory
nacm index build
```

`init` creates the local `.agent/` workspace. `index build` creates a lightweight project map and file summary.

## Daily Small Task

```bash
nacm quick "fix image loading path issue"
```

This command stores the task, generates `.agent/sessions/context_pack.md`, renders `.agent/codex/codex_prompt.md`, and tries to copy the prompt to the clipboard.

Paste the prompt into Codex and let Codex work inside the same project.

## Finish A Task

```bash
nacm done
```

`done` reads lightweight Git status and diff metadata, generates `.agent/reports/latest_report.md`, updates `.agent/sessions/recent_changes.md`, and warns if changes touched forbidden paths or look too large for the low-memory workflow.

## Large Tasks

Large tasks should be planned before implementation. The MVP prompt instructs Codex to enter plan mode when a task appears to require broad changes.
