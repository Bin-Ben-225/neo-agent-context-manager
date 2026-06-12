# Contributing

Thanks for helping improve NACM. This project is a local, prompt-only context manager for AI coding workflows on low-memory devices.

## Development Setup

Install the project in editable mode:

```powershell
py -3.11 -m pip install -e .[dev]
```

Run the core checks before opening a pull request:

```powershell
py -3.11 -m pytest tests -q
py -3.11 -m ruff check .
py -3.11 -m nacm validate smoke
py -3.11 -m pip wheel . -w $env:TEMP\nacm-wheel-check
```

## Scope Boundaries

- Keep NACM local-first and prompt-only.
- Do not upload user code or read credentials.
- Do not commit `.agent/`.
- Do not modify a user's `.gitignore` by default.
- Do not create or modify a user's repository root `AGENTS.md` during `nacm init`.
- Do not implement MCP, plugins, background services, embeddings, vector databases, or GUI/TUI unless that scope has a separate design review.

## Testing Expectations

- New CLI behavior needs tests.
- Matcher changes should include focused fixtures or regression tests.
- Prompt template changes should preserve safety constraints in tests.
- Public documentation should avoid private planning terms and local-only paths.

## Local Validation

Use the optional real-project validation script only when you want broader manual coverage:

```powershell
.\scripts\validate-real-projects.ps1
```

The script clones public repositories into a local validation directory and runs NACM workflows against them.
