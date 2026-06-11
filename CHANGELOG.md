# Changelog

All notable changes to NACM will be documented in this file.

## Unreleased

### Added

- `nacm validate smoke` for running the core workflow smoke test from the CLI.
- `nacm match explain` for inspecting ranked file matches and score signals.
- Local matcher quality fixtures covering source, tests, benchmark, localization, and typing-marker files.

### Changed

- Improved public validation documentation with real-project validation notes.
- Improved Python file summaries with imports, methods, test functions, exports, and doc keywords.
- Ignored Python cache directories during index builds.

## 0.1.0a1

Initial alpha release candidate.

### Added

- Local `.agent/` workspace initialization.
- Low-memory and workstation profiles.
- Lightweight path and file-header index generation.
- Task capture and context pack generation.
- Codex prompt generation and clipboard copy.
- Jinja-based prompt and context pack templates.
- Relevant file matching using path, filename, symbol, and keyword signals.
- `nacm quick` workflow for task setup and prompt copy.
- `nacm done` report with changed-file categories, forbidden path checks, large-change risk, and index dirty state.
- `nacm status` and `nacm doctor` diagnostics.
- Public design, workflow, examples, installation, validation, and roadmap documentation.

### Not Included

- Claude Code support.
- MCP, plugins, hooks, background services, GUI/TUI, embeddings, vector databases, cloud sync, or automatic Git commits.
