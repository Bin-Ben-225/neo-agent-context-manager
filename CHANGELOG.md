# Changelog

All notable changes to NACM will be documented in this file.

## Unreleased

### Added

- Distribution guide covering GitHub Release artifacts, PyPI, Homebrew, WinGet, pipx, and uv install paths.
- Release manifest script for recording artifact size and SHA256 checksums.
- Publish validation script for checking wheel/source distribution metadata before upload.

## 0.1.0a5

Fifth alpha release candidate.

### Added

- Real benchmark results and benchmark reporting with commit, version, and timing fields.
- Expanded stats JSON with task metadata, selected file paths, max file budget, and context budget usage.
- Stats history snapshots written by `nacm done` with `nacm stats --history` summary output.
- Hook install/uninstall all-target support, target-scoped hook doctor, and post-install verification hints.
- Version output via `nacm --version`.
- Release build and install validation scripts for wheel/sdist, pipx, uv tool, and venv console-script checks.

## 0.1.0a4

Fourth alpha release candidate.

### Added

- Project-local UserPromptSubmit hook installer, status, uninstall, and JSON runner for Codex and Claude Code.
- Hook compatibility hardening with platform-specific commands, longer hook timeout, legacy uninstall cleanup, and observed payload notes.
- Hook validation script and release checklist coverage for Codex-shaped and Claude Code-shaped payloads.
- Efficiency stats command and context/report summaries showing indexed files, selected context files, and file reduction percentage.
- Benchmark script and public benchmark results document for tracking file reduction on real projects.
- Hook doctor and verbose hook status output for checking local hook installation details.
- Contributing guide, issue templates, pull request template, and release checklist for open-source collaboration.

## 0.1.0a3

Third alpha release candidate.

### Added

- Workstation relation index artifacts for Python modules, importers, and source-test links.
- Relation-aware matcher boosts for related source, related tests, and importers when a relation index is present.
- Prompt target adapter registry with `codex` and `claude-prompt` targets.
- Prompt-only Claude-style template generation via `--target claude-prompt`.
- Target prompts now include task, confidence counts, and relation-index availability metadata when present.
- Public real-project validation notes and an optional PowerShell validation script.

## 0.1.0a2

Second alpha release candidate.

### Added

- `nacm validate smoke` for running the core workflow smoke test from the CLI.
- `nacm match explain` for inspecting ranked file matches and score signals.
- `nacm task set`, `nacm task list`, and `nacm task show latest` for local task history.
- `nacm plan` for prompt-only batch planning.
- `nacm pack --max-files --explain` and `nacm quick --max-files --explain` for context pack budget control.
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
