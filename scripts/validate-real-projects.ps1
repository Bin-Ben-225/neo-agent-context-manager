param(
  [string]$Root = "D:\Project\nacm-validation-projects",
  [string]$NacmSource = "D:\Project\neo-agent-context-manager\src"
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

foreach ($case in $cases) {
  $repoPath = Join-Path $Root $case.Name
  if (!(Test-Path $repoPath)) {
    git clone --depth 1 $case.Repo $repoPath
  }

  Push-Location $repoPath
  py -3.11 -m nacm init --profile low-memory
  py -3.11 -m nacm index build
  py -3.11 -m nacm status
  py -3.11 -m nacm match explain $case.Task --limit 6
  py -3.11 -m nacm quick $case.Task --max-files 5 --explain
  py -3.11 -m nacm plan "Investigate and improve $($case.Name) task workflow"
  py -3.11 -m nacm done
  py -3.11 -m nacm index build --profile workstation
  Pop-Location
}
