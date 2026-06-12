param(
  [string]$Root = "D:\Project\nacm-benchmark-projects",
  [string]$NacmSource = "D:\Project\neo-agent-context-manager\src",
  [string]$ReportPath = "docs\benchmark-results.md",
  [string]$JsonPath = "docs\benchmark-results.json",
  [string]$Project = "all",
  [int]$MaxFiles = 5
)

$ErrorActionPreference = "Stop"
$env:PYTHONPATH = $NacmSource

function Resolve-OutputPath {
  param(
    [string]$Path
  )

  if ([System.IO.Path]::IsPathRooted($Path)) {
    return $Path
  }
  return Join-Path (Get-Location) $Path
}

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

if ($Project -ne "all") {
  $cases = @($cases | Where-Object { $_.Name -eq $Project })
  if ($cases.Count -eq 0) {
    throw "Unknown benchmark project: $Project"
  }
}

$nacmVersion = py -3.11 -c "import pathlib, tomllib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"

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
  $repoCommit = git rev-parse --short HEAD
  py -3.11 -m nacm init --profile low-memory | Out-Null
  $indexSeconds = (Measure-Command { py -3.11 -m nacm index build | Out-Null }).TotalSeconds
  $quickSeconds = (Measure-Command {
    py -3.11 -m nacm quick $case.Task --max-files $MaxFiles --explain | Out-Null
  }).TotalSeconds
  $statsSeconds = (Measure-Command {
    $script:stats = py -3.11 -m nacm stats --json | ConvertFrom-Json
  }).TotalSeconds
  Pop-Location

  $results += [ordered]@{
    project = $case.Name
    task = $case.Task
    repo_commit = $repoCommit
    nacm_version = $nacmVersion
    max_files = $MaxFiles
    indexed_files = $stats.indexed_files
    context_files = $stats.context_files
    context_chars = $stats.context_chars
    file_reduction_percent = $stats.file_reduction_percent
    index_seconds = [math]::Round($indexSeconds, 3)
    quick_seconds = [math]::Round($quickSeconds, 3)
    stats_seconds = [math]::Round($statsSeconds, 3)
  }
}

$reportLines = @(
  "# Benchmark Results",
  "",
  "These benchmark cases measure how much NACM narrows a task from indexed files to selected context files.",
  "",
  "| Project | Task | Repo commit | NACM version | Max files | Indexed files | Context files | Context chars | File reduction | Index seconds | Quick seconds | Stats seconds |",
  "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
)

foreach ($item in $results) {
  $reportLines += "| $($item.project) | $($item.task) | $($item.repo_commit) | $($item.nacm_version) | $($item.max_files) | $($item.indexed_files) | $($item.context_files) | $($item.context_chars) | $([math]::Round($item.file_reduction_percent, 1))% | $($item.index_seconds) | $($item.quick_seconds) | $($item.stats_seconds) |"
}

$reportLines += @(
  "",
  "Regenerate with:",
  "",
  '```powershell',
  '.\scripts\benchmark-projects.ps1',
  '.\scripts\benchmark-projects.ps1 -Project humanize -MaxFiles 5',
  '```'
)

$reportFile = Resolve-OutputPath -Path $ReportPath
$jsonFile = Resolve-OutputPath -Path $JsonPath
New-Item -ItemType Directory -Force -Path (Split-Path $reportFile) | Out-Null
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllLines($reportFile, $reportLines, $utf8NoBom)
[System.IO.File]::WriteAllText($jsonFile, (@($results) | ConvertTo-Json -Depth 8), $utf8NoBom)

Write-Output "Benchmark report: $reportFile"
Write-Output "Benchmark JSON: $jsonFile"
