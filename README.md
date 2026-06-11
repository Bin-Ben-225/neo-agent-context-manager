# NACM - NeoAgent Context Manager

A lightweight local context manager for AI coding agents on low-memory devices.

NACM prepares small, task-focused context packs so Codex can work with fewer broad scans and less local I/O. The current version is Codex-first and prompt-only.

## Current Capabilities

The current version focuses on:

- Local `.agent/` workspace
- Low-memory and workstation profiles
- Lightweight path and Python-aware file-header index
- Task-level context pack generation
- Task history and prompt-only batch planning
- Context pack file-budget controls
- Match explanations for relevant file selection
- Codex prompt generation
- Clipboard copy for Codex prompts
- Task finalization report with changed-file summaries, forbidden path checks, and large-change risk hints
- Built-in smoke validation command

This version does not implement Claude Code, MCP, plugins, hooks, embeddings, vector databases, GUI/TUI, background services, or automatic Git commits.

## Install For Development

```bash
python -m pip install -e .[dev]
```

On Windows, if `python` points to an environment without `pip`, use the Python launcher:

```bash
py -3.11 -m pip install -e .[dev]
```

After installation, either command form works:

```bash
nacm --help
python -m nacm --help
```

On Windows, `nacm.exe` may be installed into a Python `Scripts` directory that is not on `PATH`. In that case, use:

```powershell
py -3.11 -m nacm --help
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

`done` writes `.agent/reports/latest_report.md` with Git status, diff stat, changed-file categories, forbidden path warnings, large-change risk hints, and index dirty state.

Validate the core workflow with:

```bash
nacm validate smoke
```

Inspect why NACM selected files for a task:

```bash
nacm match explain "fix image loading path issue"
```

For a larger request, create a local prompt-only batch plan:

```bash
nacm plan "refactor matcher and add tests"
```

## Documentation

- [Design](docs/design.md)
- [Workflow](docs/workflow.md)
- [Examples](docs/examples.md)
- [Installation](docs/install.md)
- [Validation](docs/validation.md)
- [Roadmap](docs/roadmap.md)
