param(
  [string]$Dist = "dist",
  [string]$OutputPath = "",
  [string]$Version = "",
  [string]$ReleaseTag = ""
)

$ErrorActionPreference = "Stop"

if (!$Version) {
  $pyproject = Get-Content -Path "pyproject.toml" -Raw
  if ($pyproject -match '(?m)^version\s*=\s*"([^"]+)"') {
    $Version = $Matches[1]
  } else {
    throw "Could not read project version from pyproject.toml"
  }
}

if (!$ReleaseTag) {
  $ReleaseTag = "v$($Version -replace 'a', '-alpha.')"
}

if (!$OutputPath) {
  $OutputPath = Join-Path $Dist "release-manifest.json"
}

$artifacts = Get-ChildItem -Path $Dist -File |
  Where-Object { $_.Name -like "neo_agent_context_manager-*" -and ($_.Extension -in ".whl", ".gz") } |
  Sort-Object Name

if (!$artifacts) {
  throw "No NACM release artifacts found in $Dist. Run .\scripts\build-release.ps1 first."
}

$entries = foreach ($artifact in $artifacts) {
  $hash = Get-FileHash -Path $artifact.FullName -Algorithm SHA256
  $kind = if ($artifact.Extension -eq ".whl") { "wheel" } else { "sdist" }
  [PSCustomObject]@{
    name = $artifact.Name
    kind = $kind
    length = $artifact.Length
    sha256 = $hash.Hash.ToLowerInvariant()
  }
}

$manifest = [PSCustomObject]@{
  package = "neo-agent-context-manager"
  version = $Version
  release_tag = $ReleaseTag
  generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  artifacts = $entries
}

$json = $manifest | ConvertTo-Json -Depth 6
$directory = Split-Path -Parent $OutputPath
if ($directory) {
  New-Item -ItemType Directory -Force -Path $directory | Out-Null
}

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$resolvedOutputPath = [System.IO.Path]::GetFullPath($OutputPath)
[System.IO.File]::WriteAllText($resolvedOutputPath, $json + [Environment]::NewLine, $utf8NoBom)

Write-Output "Release manifest: $OutputPath"
foreach ($entry in $entries) {
  Write-Output "$($entry.name) SHA256 $($entry.sha256) Length $($entry.length)"
}
