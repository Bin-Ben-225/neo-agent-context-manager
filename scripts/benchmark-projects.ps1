param(
  [string]$Root = "D:\Project\nacm-benchmark-projects",
  [string]$NacmSource = "D:\Project\neo-agent-context-manager\src",
  [string]$ReportPath = "docs\benchmark-results.md",
  [string]$JsonPath = "docs\benchmark-results.json"
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = $NacmSource

$cases = @(
  @{
    Name = "humanize"
    Repo = "https://github.com/python-humanize/humanize.git"
    Task = "check naturaltime naturalday date and time formatting logic"
  },
  @{
    Name = "click"
    Repo = "https://github.com/pallets/click.git"
    Task = "check command option parsing and parameter validation logic"
  },
  @{
    Name = "uuid"
    Repo = "https://github.com/uuidjs/uuid.git"
    Task = "check v4 random uuid generation logic and tests"
  }
)

New-Item -ItemType Directory -Force -Path $Root | Out-Null

$results = @()
foreach ($case in $cases) {
  $repoPath = Join-Path $Root $case.Name
  if (!(Test-Path $repoPath)) {
    git clone --depth 1 $case.Repo $repoPath
    if ($LASTEXITCODE -ne 0) {
      throw "Failed to clone $($case.Repo) into $repoPath"
    }
  }

  if (!(Test-Path $repoPath)) {
    throw "Benchmark project path not found: $repoPath"
  }

  Push-Location $repoPath
  py -3.11 -m nacm init --profile low-memory | Out-Null
  py -3.11 -m nacm index build | Out-Null
  py -3.11 -m nacm quick $case.Task --max-files 5 --explain | Out-Null
  $stats = py -3.11 -m nacm stats --json | ConvertFrom-Json
  Pop-Location

  $results += [ordered]@{
    project = $case.Name
    task = $case.Task
    indexed_files = $stats.indexed_files
    context_files = $stats.context_files
    context_chars = $stats.context_chars
    file_reduction_percent = $stats.file_reduction_percent
  }
}

$reportLines = @(
  "# Benchmark Results",
  "",
  "These benchmark cases measure how much NACM narrows a task from indexed files to selected context files.",
  "",
  "| Project | Task | Indexed files | Context files | Context chars | File reduction |",
  "| --- | --- | ---: | ---: | ---: | ---: |"
)

foreach ($item in $results) {
  $reportLines += "| $($item.project) | $($item.task) | $($item.indexed_files) | $($item.context_files) | $($item.context_chars) | $([math]::Round($item.file_reduction_percent, 1))% |"
}

$reportLines += @(
  "",
  "Regenerate with:",
  "",
  '```powershell',
  '.\scripts\benchmark-projects.ps1',
  '```',
  ""
)

$reportFile = Join-Path (Get-Location) $ReportPath
$jsonFile = Join-Path (Get-Location) $JsonPath
New-Item -ItemType Directory -Force -Path (Split-Path $reportFile) | Out-Null
$reportLines | Set-Content -Path $reportFile -Encoding UTF8
$results | ConvertTo-Json -Depth 8 | Set-Content -Path $jsonFile -Encoding UTF8

Write-Output "Benchmark report: $reportFile"
Write-Output "Benchmark JSON: $jsonFile"
