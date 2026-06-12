param(
  [string]$Dist = "dist"
)

$ErrorActionPreference = "Stop"

$wheel = Get-ChildItem -Path $Dist -Filter "neo_agent_context_manager-*.whl" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (!$wheel) {
  throw "No NACM wheel found in $Dist. Run .\scripts\build-release.ps1 first."
}

Write-Output "Validating wheel: $($wheel.FullName)"

$pipx = Get-Command pipx -ErrorAction SilentlyContinue
if ($pipx) {
  pipx uninstall neo-agent-context-manager --yes 2>$null | Out-Null
  pipx install $wheel.FullName
  nacm --version
  nacm --help | Out-Null
  pipx uninstall neo-agent-context-manager --yes | Out-Null
  Write-Output "pipx install validation passed."
} else {
  Write-Output "pipx not found; skipping pipx validation."
}

$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($uv) {
  uv tool uninstall neo-agent-context-manager 2>$null | Out-Null
  uv tool install $wheel.FullName
  nacm --version
  nacm --help | Out-Null
  uv tool uninstall neo-agent-context-manager | Out-Null
  Write-Output "uv tool install validation passed."
} else {
  Write-Output "uv not found; skipping uv validation."
}

$venv = Join-Path $env:TEMP ("nacm-install-venv-" + [guid]::NewGuid().ToString("N"))
py -3.11 -m venv $venv
$python = Join-Path $venv "Scripts\python.exe"
$nacm = Join-Path $venv "Scripts\nacm.exe"
& $python -m pip install $wheel.FullName | Out-Null
& $nacm --version
& $nacm --help | Out-Null
Remove-Item -Recurse -Force $venv
Write-Output "venv console-script validation passed."
