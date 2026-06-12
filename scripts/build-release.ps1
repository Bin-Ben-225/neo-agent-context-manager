param(
  [string]$Dist = "dist"
)

$ErrorActionPreference = "Stop"

Remove-Item -Recurse -Force $Dist -ErrorAction SilentlyContinue
py -3.11 -m pip install --upgrade build | Out-Null
py -3.11 -m build

$artifacts = Get-ChildItem -Path $Dist -File
if (!$artifacts) {
  throw "No release artifacts were created in $Dist"
}

$artifacts | ForEach-Object { Write-Output "Built artifact: $($_.FullName)" }
