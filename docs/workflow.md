# NACM Workflow

## First Use

```bash
nacm init --profile low-memory
nacm index build
nacm doctor
```

`init` creates the local `.agent/` workspace. `index build` creates a lightweight project map and file summary.

`doctor` checks whether the local workspace and lightweight index are ready.

## Daily Small Task

```bash
nacm quick "fix image loading path issue"
```

This command stores the task, generates `.agent/sessions/context_pack.md`, renders `.agent/codex/codex_prompt.md`, and tries to copy the prompt to the clipboard.

Paste the prompt into Codex and let Codex work inside the same project.

For a prompt-only Claude-style workflow:

```bash
nacm quick "fix image loading path issue" --target claude-prompt
```

This writes `.agent/claude/claude_prompt.md`. To prepare this prompt automatically when a task is submitted, install the project-local Claude Code hook. NACM does not run Claude Code or start background services.

To inspect local NACM state at any time:

```bash
nacm status
nacm stats
```

`nacm stats` reports indexed files, selected context files, context size, and file reduction percentage for the latest context pack.
Use `nacm stats --json` when benchmark or reporting scripts need task metadata, selected file paths, and context budget usage.
After `nacm done`, NACM appends a local stats snapshot. Use `nacm stats --history` to review recent average file reduction and context file counts.

To inspect why files would be selected for a task:

```bash
nacm match explain "fix image loading path issue"
```

The explain output lists ranked files, confidence, score, and the signals that contributed to the match.

To review recent tasks:

```bash
nacm task list
nacm task show latest
```

To keep a context pack small or include detailed match explanations:

```bash
nacm pack --max-files 5 --explain
nacm quick "fix image loading path issue" --max-files 5 --explain
```

## Finish A Task

```bash
nacm done
```

`done` reads lightweight Git status and diff metadata, generates `.agent/reports/latest_report.md`, updates `.agent/sessions/recent_changes.md`, and warns if changes touched forbidden paths or look too large for the low-memory workflow.

The report includes:

- changed file count
- modified files
- added or untracked files
- deleted files
- renamed files
- forbidden path checks
- large-change risk
- index dirty state
- efficiency summary
- stats history snapshot
- next action guidance

If project files changed after the last index build, NACM writes `.agent/cache/index_state.json` and recommends rebuilding the index when useful.

## Large Tasks

Large tasks should be planned before implementation:

```bash
nacm plan "refactor matcher and add tests"
```

The plan is written under `.agent/sessions/batches/`. NACM does not execute the plan automatically.
