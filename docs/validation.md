# Validation

This page documents a public-safe smoke test for the current NACM workflow. It creates a temporary Git repository, runs the CLI, and verifies generated local files.

## Prerequisites

Install NACM in development mode:

```powershell
cd D:\Project\neo-agent-context-manager
py -3.11 -m pip install -e .[dev]
```

## Smoke Test

Run the built-in smoke validation:

```powershell
py -3.11 -m nacm validate smoke
```

Expected final output:

```text
Smoke passed: <temporary path>
```

The command creates a temporary Git repository, runs the core workflow, and verifies generated local files.
The equivalent PowerShell flow is:

```powershell
$ErrorActionPreference='Stop'

$smoke = Join-Path $env:TEMP ('nacm-smoke-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $smoke | Out-Null
Set-Location $smoke

git init | Out-Null
git config user.name 'Smoke Test'
git config user.email 'smoke@example.com'

New-Item -ItemType Directory -Path src | Out-Null
Set-Content -Path src\images.py -Value "def load_image(path):`n    return path`n" -Encoding UTF8
git add src\images.py
git commit -m 'add image loader' | Out-Null

py -3.11 -m nacm status | Out-Null
py -3.11 -m nacm init --profile low-memory | Out-Null
py -3.11 -m nacm index build | Out-Null
py -3.11 -m nacm doctor | Out-Null
py -3.11 -m nacm quick "fix src/images.py image loading failure" | Out-Null

Set-Content -Path src\new_feature.py -Value "def feature():`n    return True`n" -Encoding UTF8
py -3.11 -m nacm done | Out-Null

$context = Get-Content .agent\sessions\context_pack.md -Raw
$prompt = Get-Content .agent\codex\codex_prompt.md -Raw
$report = Get-Content .agent\reports\latest_report.md -Raw

$checks = @(
  (Test-Path .agent\config.toml),
  (Test-Path .agent\index\file_summary.json),
  (Test-Path .agent\sessions\context_pack.md),
  (Test-Path .agent\codex\codex_prompt.md),
  (Test-Path .agent\reports\latest_report.md),
  ((Get-Content .git\info\exclude -Raw) -match '\.agent/'),
  ($context -match 'Functions: load_image'),
  ($prompt -match 'First read `.agent/sessions/context_pack.md`.'),
  ($report -match 'Changed file count: 1')
)

if ($checks -contains $false) {
  throw 'Smoke check failed'
}

Write-Output "Smoke passed: $smoke"
```

The final output is:

```text
Smoke passed: <temporary path>
```

## Verification Commands

Before publishing or tagging a release candidate, run:

```powershell
py -3.11 -m pytest tests -q
py -3.11 -m ruff check .
py -3.11 -m pip wheel . -w $env:TEMP\nacm-wheel-check
```

## Real Project Validation

The current workflow has also been checked against
[`python-humanize/humanize`](https://github.com/python-humanize/humanize), a small Python library with source files,
tests, documentation, localization files, and benchmark files.

Use a fresh clone of the project and run:

```powershell
py -3.11 -m nacm init --profile low-memory
py -3.11 -m nacm index build
py -3.11 -m nacm doctor
py -3.11 -m nacm status
```

Then run task-focused checks:

```powershell
py -3.11 -m nacm quick "check src/humanize/filesize.py naturalsize file size formatting logic"
py -3.11 -m nacm quick "check humanize number intcomma intword logic and tests"
py -3.11 -m nacm quick "check naturaltime naturalday date and time formatting logic"
```

Expected high-confidence matches:

- Filesize task: `src/humanize/filesize.py`, `tests/test_filesize.py`
- Number task: `src/humanize/number.py`, `tests/test_number.py`
- Time task: `src/humanize/time.py`, `tests/test_time.py`

Acceptable secondary matches include related documentation, package entry points, i18n tests, and benchmark files.
Localization catalogs and typing marker files should not crowd out the core source and test files.
