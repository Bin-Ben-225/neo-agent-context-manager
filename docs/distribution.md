# Distribution

NACM is distributed as a Python CLI first. The current release path keeps the
artifact small and easy to verify before broader package-manager submission.

## Recommended User Installs

Use `pipx` when users want a global `nacm` command without mixing NACM into a
project environment:

```bash
pipx install neo-agent-context-manager
nacm --version
```

Use `uv tool install` when users already use uv for Python tooling:

```bash
uv tool install neo-agent-context-manager
nacm --version
```

Use a GitHub Release wheel before the package is available on PyPI:

```powershell
pipx install .\neo_agent_context_manager-0.1.0a5-py3-none-any.whl
nacm --version
```

## GitHub Release Artifacts

Each release should upload:

- `neo_agent_context_manager-<version>-py3-none-any.whl`
- `neo_agent_context_manager-<version>.tar.gz`
- `release-manifest.json`

Generate the manifest after building the wheel and source distribution:

```powershell
.\scripts\build-release.ps1
.\scripts\write-release-manifest.ps1
```

The manifest records artifact name, type, size, and SHA256 checksum. It is safe
to publish with the release and gives users a stable way to verify downloads.

## PyPI

PyPI is the primary channel for `pipx` and `uv tool install` by package name.
Before publishing, run the full release checklist and verify the GitHub Release
wheel installs correctly. Publish only from a clean tree and only after the
version in `pyproject.toml`, `CHANGELOG.md`, and the Git tag agree.

Expected install commands after PyPI publication:

```bash
pipx install neo-agent-context-manager
uv tool install neo-agent-context-manager
```

## Homebrew

Homebrew should be added through a separate tap repository after the GitHub
Release artifact and checksum are stable. The tap can reference the source
distribution URL and the SHA256 value from `release-manifest.json`.

Recommended tap shape:

```text
Bin-Ben-225/homebrew-nacm
Formula/nacm.rb
```

The formula should install the `nacm` console command and verify:

```bash
nacm --version
nacm --help
```

Homebrew formulas for Python CLIs also need dependency resources. Generate or
audit those resources before opening the tap to users.

## WinGet

WinGet is best added after NACM has a Windows-native installer or signed zip
artifact. The current wheel works well through `pipx`, but WinGet users expect a
direct installer flow. Keep WinGet as a follow-up channel after the release
package includes a Windows artifact with a stable checksum.

Minimum WinGet preparation:

- A GitHub Release URL for the Windows artifact.
- SHA256 checksum from the published artifact.
- A verified install command that makes `nacm --version` work in a new shell.

## Release Order

Recommended order for public distribution:

1. GitHub Release with wheel, source distribution, and `release-manifest.json`.
2. PyPI publication for `pipx` and `uv tool install`.
3. Homebrew tap once Python dependency resources are prepared.
4. WinGet after a Windows installer or standalone archive is available.
