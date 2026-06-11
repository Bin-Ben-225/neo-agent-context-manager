# NACM Design

NACM is a local CLI that prepares small, task-focused context packs for AI coding agents on low-memory machines. The current version is Codex-first and prompt-only, with a prompt-only secondary target for Claude-style workflows: it does not run an agent, contact cloud services, start a background process, or upload project code.

## Scope

The current release supports one daily workflow:

```bash
nacm init --profile low-memory
nacm index build
nacm quick "fix image loading path issue"
nacm done
```

Claude Code hooks, MCP, plugins, semantic indexing, embeddings, GUI/TUI, and background watchers are outside the current scope.

## Local Workspace

`nacm init` creates a local `.agent/` directory in the target project. This directory stores configuration, profiles, lightweight indexes, task state, generated Codex prompts, cache files, and reports.

NACM writes `.agent/` to `.git/info/exclude` when the target project is a Git repository. It does not modify the target project's `.gitignore` by default.

## Core Modules

- `workspace`: initializes `.agent/`, default profiles, local config, and Git exclude rules.
- `indexer`: scans paths, skips ignored directories, reads only small file headers, and writes lightweight index files.
- `session`: stores the current task, builds context packs, and generates completion reports.
- `adapters`: renders prompt files for supported targets and copies prompts when a target supports clipboard copy.
- `utils`: isolates path, Git, platform, and clipboard behavior.

## Indexing And Matching

NACM uses only lightweight signals:

- L0 path metadata: relative POSIX path, size, mtime, extension, and directory depth.
- L1 file header summary: imports, class/function names, methods, test functions, exports, doc keywords, and general keywords from the first file header chunk.
- Workstation relation index: optional Python module, import, and source-test links generated for the `workstation` profile.
- Task matching: explicit path mentions, filename stems, path keywords, Python symbols, summary keyword scoring, relation-aware boosts, and low-value file demotion.
- Match explanations: ranked files include the signals and weights that contributed to selection.

The index never performs full semantic indexing, embedding, vector search, full-file hashing, or realtime watching.

## Context Pack

The low-memory profile defaults to:

```text
max_context_chars = 30000
max_files_in_context = 8
max_file_head_kb = 16
max_tree_depth = 3
```

`context_pack.md` includes the task, mode, relevant files grouped by confidence, short file summaries, match reasons, forbidden paths, suggested scoped searches, device constraints, and completion criteria.

When no file matches the task, NACM adds guidance for scoped search instead of encouraging broad repository reads.

## Done Report

`nacm done` generates `.agent/reports/latest_report.md`. The report includes:

- Git status and diff stat
- Changed file count
- Modified, added/untracked, deleted, and renamed file groups
- Forbidden path checks
- Large-change risk based on the active profile
- Index dirty state and next-action guidance

If project files changed after the last index build, NACM writes `.agent/cache/index_state.json` with a dirty marker.

## Codex Prompt

The generated Codex prompt tells Codex to read `.agent/sessions/context_pack.md` first, prioritize High Confidence files, avoid full-repository scanning, avoid forbidden paths, avoid `.agent/`, avoid creating or editing root `AGENTS.md`, provide a plan before changes, and remind the user to run `nacm done`.

## Prompt Targets

Supported prompt targets are:

- `codex`: writes `.agent/codex/codex_prompt.md` and supports clipboard copy.
- `claude-prompt`: writes `.agent/claude/claude_prompt.md` for prompt-only Claude-style use. It does not install hooks, use MCP, run plugins, or start background services.

Prompt templates receive lightweight metadata when available: the current task, confidence file counts, and whether a workstation relation index exists.

## Safety

NACM is local-only. It does not read credentials, upload code, proxy Codex login, run heavy build commands, commit changes, push changes, or start another agent.
