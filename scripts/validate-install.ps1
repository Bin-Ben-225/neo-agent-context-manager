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

function Get-NacmCommand {
  $command = Get-Command nacm -ErrorAction SilentlyContinue
  if ($command) {
    return $command.Source
  }

  $pipxLocal = Join-Path $env:USERPROFILE ".local\bin\nacm.exe"
  if (Test-Path $pipxLocal) {
    return $pipxLocal
  }

  $pythonScripts = Join-Path $env:APPDATA "Python\Python311\Scripts\nacm.exe"
  if (Test-Path $pythonScripts) {
    return $pythonScripts
  }

  throw "nacm command was installed but could not be found. Check PATH or pipx app path."
}

$pipx = Get-Command pipx -ErrorAction SilentlyContinue
if ($pipx -or (py -3.11 -m pipx --version 2>$null)) {
  py -3.11 -m pipx uninstall neo-agent-context-manager 2>$null | Out-Null
  py -3.11 -m pipx install $wheel.FullName
  $nacm = Get-NacmCommand
  & $nacm --version
  & $nacm --help | Out-Null
  py -3.11 -m pipx uninstall neo-agent-context-manager | Out-Null
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
