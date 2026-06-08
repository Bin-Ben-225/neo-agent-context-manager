# NACM MVP Design

NACM is a local CLI that prepares small, task-focused context packs for AI coding agents on low-memory machines. The MVP is Codex-first and prompt-only: it does not run an agent, contact cloud services, start a background process, or upload project code.

## Scope

The first release supports one daily workflow:

```bash
nacm init --profile low-memory
nacm index build
nacm quick "fix image loading path issue"
nacm done
```

Claude Code, MCP, plugins, hooks, semantic indexing, embeddings, GUI/TUI, and background watchers are outside the MVP.

## Local Workspace

`nacm init` creates a local `.agent/` directory in the target project. This directory stores configuration, profiles, lightweight indexes, task state, generated Codex prompts, cache files, and reports.

NACM writes `.agent/` to `.git/info/exclude` when the target project is a Git repository. It does not modify the target project's `.gitignore` by default.

## Core Modules

- `workspace`: initializes `.agent/`, default profiles, local config, and Git exclude rules.
- `indexer`: scans paths, skips ignored directories, reads only small file headers, and writes lightweight index files.
- `session`: stores the current task, builds context packs, and generates completion reports.
- `adapters.codex`: renders Codex prompt files and copies them to the clipboard.
- `utils`: isolates path, Git, platform, and clipboard behavior.

## Indexing

The MVP uses only lightweight signals:

- L0 path metadata: relative POSIX path, size, mtime, extension, and directory depth.
- L1 file header summary: imports, class/function names, and keywords from the first file header chunk.
- Task matching: filename, path, and summary keyword scoring.

The index never performs full semantic indexing, embedding, vector search, full-file hashing, or realtime watching.

## Context Pack

The low-memory profile defaults to:

```text
max_context_chars = 30000
max_files_in_context = 8
max_file_head_kb = 16
max_tree_depth = 3
```

`context_pack.md` includes the task, mode, relevant files grouped by confidence, forbidden paths, suggested scoped searches, device constraints, and completion criteria.

## Codex Prompt

The generated Codex prompt tells Codex to read `.agent/sessions/context_pack.md` first, prioritize High Confidence files, avoid full-repository scanning, avoid forbidden paths, avoid `.agent/`, avoid creating or editing root `AGENTS.md`, provide a plan before changes, and remind the user to run `nacm done`.

## Safety

NACM is local-only. The MVP does not read credentials, upload code, proxy Codex login, run heavy build commands, commit changes, push changes, or start another agent.
