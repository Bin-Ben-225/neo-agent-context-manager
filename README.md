# NACM - NeoAgent Context Manager

A lightweight local context manager for AI coding agents on low-memory devices.

NACM prepares small, task-focused context packs so Codex can work with fewer broad scans and less local I/O. The current MVP is Codex-first and prompt-only.

## Current Scope

Phase 1 focuses on:

- Local `.agent/` workspace
- Low-memory and workstation profiles
- Lightweight path and file-header index
- Task-level context pack generation
- Codex prompt generation
- Clipboard copy for Codex prompts
- Lightweight task finalization report

Phase 1 does not implement Claude Code, MCP, plugins, hooks, embeddings, vector databases, GUI/TUI, background services, or automatic Git commits.

## Install For Development

```bash
python -m pip install -e .[dev]
```

On Windows, if `python` points to an environment without `pip`, use the Python launcher:

```bash
py -3.11 -m pip install -e .[dev]
```

## Basic Workflow

Run these commands inside the project you want Codex to work on:

```bash
nacm init --profile low-memory
nacm index build
nacm quick "fix image loading path issue"
```

`quick` writes `.agent/sessions/context_pack.md`, renders `.agent/codex/codex_prompt.md`, and tries to copy the prompt to your clipboard. Paste the generated prompt into Codex.

After Codex finishes:

```bash
nacm done
```

`done` writes `.agent/reports/latest_report.md` with Git status, diff stat, changed files, and forbidden path warnings.

## Documentation

- [MVP design](docs/design.md)
- [Workflow](docs/workflow.md)
- [Roadmap](docs/roadmap.md)

Private planning documents are kept in `private_docs/` and are not part of the public repository.
