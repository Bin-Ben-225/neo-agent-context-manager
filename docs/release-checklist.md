# Release Checklist

Use this checklist before tagging a NACM alpha release candidate.

## Preflight

- Confirm the working tree is clean:

```powershell
git status --short --branch
```

- Confirm the version in `pyproject.toml` matches the intended release.
- Confirm `CHANGELOG.md` has a dated or versioned section for the release.

## Verification

Run:

```powershell
py -3.11 -m pytest tests -q
py -3.11 -m ruff check .
py -3.11 -m nacm validate smoke
py -3.11 -m pip wheel . -w $env:TEMP\nacm-wheel-check
```

Check packaged prompt templates when prompt targets change:

```powershell
@'
import os, zipfile
from pathlib import Path
wheel_dir = Path(os.environ["TEMP"]) / "nacm-wheel-check"
wheel = max(wheel_dir.glob("neo_agent_context_manager-*.whl"), key=lambda path: path.stat().st_mtime)
with zipfile.ZipFile(wheel) as zf:
    names = set(zf.namelist())
    assert "nacm/templates/codex_prompt.md.j2" in names
    assert "nacm/templates/claude_prompt.md.j2" in names
print("Prompt templates packaged")
'@ | py -3.11 -
```

## Public Documentation Scan

Run a public-wording scan before tagging:

```powershell
$terms = @("Pha" + "se", "M" + "VP", "private" + "_docs", "private " + "docs", "Later " + "Pha" + "ses")
rg -n ($terms -join "|") README.md docs CHANGELOG.md CONTRIBUTING.md .github AGENTS.md src tests pyproject.toml scripts
```

No matches should appear.

## Tagging

Replace `X` with the alpha number:

```powershell
git tag v0.1.0-alpha.X
git push origin v0.1.0-alpha.X
```

After tagging, avoid moving the tag. Put follow-up changes in `CHANGELOG.md` under `Unreleased`.
