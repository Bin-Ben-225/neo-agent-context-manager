# Installation

NACM is a Python CLI. The current package targets Python 3.10 or newer.

## Development Install

From the repository root:

```bash
python -m pip install -e .[dev]
```

On Windows, the Python launcher is often more reliable:

```powershell
py -3.11 -m pip install -e .[dev]
```

## Command Forms

If your Python `Scripts` directory is on `PATH`, use:

```bash
nacm --help
```

If `nacm` is not on `PATH`, use the module form:

```bash
python -m nacm --help
```

On Windows:

```powershell
py -3.11 -m nacm --help
```

## Package Build Check

Build a wheel:

```powershell
py -3.11 -m pip wheel . -w $env:TEMP\nacm-wheel-check
```

NACM includes Markdown templates inside the wheel. A quick package-data check:

```powershell
@'
import os, zipfile
from pathlib import Path
wheel_dir = Path(os.environ["TEMP"]) / "nacm-wheel-check"
wheel = next(wheel_dir.glob("neo_agent_context_manager-*.whl"))
with zipfile.ZipFile(wheel) as zf:
    names = zf.namelist()
    assert "nacm/templates/codex_prompt.md.j2" in names
    assert "nacm/templates/context_pack.md.j2" in names
print("Templates packaged")
'@ | py -3.11 -
```

## Local Smoke Test

See [Validation](validation.md) for an end-to-end smoke test.
