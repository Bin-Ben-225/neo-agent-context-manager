param(
  [string]$Root = "",
  [string]$NacmSource = ""
)

$ErrorActionPreference = "Stop"

if ($NacmSource -ne "") {
  $env:PYTHONPATH = $NacmSource
}

if ($Root -eq "") {
  $Root = Join-Path $env:TEMP ("nacm-hook-validation-" + [guid]::NewGuid().ToString("N"))
}

function New-HookProject {
  param(
    [string]$Name
  )

  $project = Join-Path $Root $Name
  New-Item -ItemType Directory -Force -Path (Join-Path $project "src") | Out-Null
  Set-Content -Path (Join-Path $project "src\app.py") -Value "def run():`n    return True" -Encoding UTF8
  return $project
}

function Invoke-HookValidation {
  param(
    [string]$Project,
    [string]$Target,
    [hashtable]$Payload,
    [string]$PromptPath
  )

  Push-Location $Project
  py -3.11 -m nacm hook install --target $Target
  $Payload | ConvertTo-Json -Compress | py -3.11 -m nacm hook run --target $Target | Out-Null
  py -3.11 -m nacm hook status
  Pop-Location

  $contextPack = Join-Path $Project ".agent\sessions\context_pack.md"
  if (!(Test-Path $contextPack)) {
    throw "Missing context pack for $Target at $contextPack"
  }
  if (!(Test-Path (Join-Path $Project $PromptPath))) {
    throw "Missing prompt file for $Target at $PromptPath"
  }
}

New-Item -ItemType Directory -Force -Path $Root | Out-Null

$codexProject = New-HookProject -Name "codex"
$codexPayload = @{
  cwd = $codexProject
  hook_event_name = "UserPromptSubmit"
  prompt = "Codex hook validation: inspect src/app.py"
  model = "gpt-5-codex"
  turn_id = "turn-validation"
}
Invoke-HookValidation `
  -Project $codexProject `
  -Target "codex" `
  -Payload $codexPayload `
  -PromptPath ".agent\codex\codex_prompt.md"

$claudeProject = New-HookProject -Name "claude-code"
$claudePayload = @{
  session_id = "validation"
  transcript_path = (Join-Path $claudeProject "session.jsonl")
  cwd = $claudeProject
  permission_mode = "default"
  hook_event_name = "UserPromptSubmit"
  prompt = "Claude Code hook validation: inspect src/app.py"
}
Invoke-HookValidation `
  -Project $claudeProject `
  -Target "claude-code" `
  -Payload $claudePayload `
  -PromptPath ".agent\claude\claude_prompt.md"

Write-Output "Hook validation passed: $Root"
