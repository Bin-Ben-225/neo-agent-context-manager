# AGENTS.md

This repository builds NACM, a local context manager for AI coding agents on low-memory devices.

## Development Rules

- Keep the MVP Codex-first and prompt-only.
- Do not implement Claude Code hooks, MCP, plugins, background services, embeddings, vector databases, or GUI/TUI features in Phase 1.
- Use `pathlib.Path` for path handling.
- Store cross-device index keys as relative POSIX paths.
- Do not read credentials or upload user code.
- Do not modify a user's `.gitignore` by default.
- Do not create or modify a user's root `AGENTS.md` during `nacm init`.
- New CLI behavior must have basic tests.
- Keep `.agent/` local and out of version control.
