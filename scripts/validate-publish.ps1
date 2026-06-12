param(
  [string]$Dist = "dist"
)

$ErrorActionPreference = "Stop"

$wheel = Get-ChildItem -Path $Dist -Filter "neo_agent_context_manager-*.whl" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1
$sdist = Get-ChildItem -Path $Dist -Filter "neo_agent_context_manager-*.tar.gz" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (!$wheel) {
  throw "No wheel found in $Dist. Run .\scripts\build-release.ps1 first."
}
if (!$sdist) {
  throw "No source distribution found in $Dist. Run .\scripts\build-release.ps1 first."
}

.\scripts\write-release-manifest.ps1 -Dist $Dist

py -3.11 -m twine --version 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  py -3.11 -m pip install twine | Out-Null
}
py -3.11 -m twine check $wheel.FullName $sdist.FullName

Write-Output "Publish validation passed."
Write-Output "Artifacts are ready for GitHub Release and PyPI upload:"
Write-Output $wheel.FullName
Write-Output $sdist.FullName
Write-Output (Join-Path $Dist "release-manifest.json")
