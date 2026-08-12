# bootstrap-harness.ps1 — 在 superpowers-demand-workflow 基础上安装 Harness 层
param(
    [string]$ProjectRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$HarnessScripts = $PSScriptRoot
$HarnessRoot = Split-Path -Parent $HarnessScripts
$AgentsSkills = Split-Path -Parent $HarnessRoot
$ProjectRoot = (Resolve-Path $ProjectRoot).Path

Write-Host "Superpowers Harness 安装" -ForegroundColor Cyan
Write-Host "  项目: $ProjectRoot"
Write-Host ""

# Step 1: demand-workflow bootstrap
$DemandBootstrap = Join-Path $AgentsSkills "superpowers-demand-workflow\scripts\bootstrap.ps1"
if (Test-Path $DemandBootstrap) {
    & $DemandBootstrap -ProjectRoot $ProjectRoot
} else {
    Write-Host "  [警告] 未找到 demand-workflow bootstrap，跳过" -ForegroundColor Yellow
}

# Step 2: 复制 scripts/harness/
$TargetHarness = Join-Path $ProjectRoot "scripts\harness"
New-Item -ItemType Directory -Force -Path $TargetHarness | Out-Null

$ValidatorsSrc = Join-Path $HarnessRoot "validators"
$ValidatorsDst = Join-Path $TargetHarness "validators"
if (Test-Path $ValidatorsDst) { Remove-Item -Recurse -Force $ValidatorsDst }
Copy-Item -Path $ValidatorsSrc -Destination $ValidatorsDst -Recurse -Force
Write-Host '  [复制] scripts\harness\validators\' -ForegroundColor Green

$CliSrc = Join-Path $HarnessScripts "validate-harness.mjs"
$CliDst = Join-Path $TargetHarness "validate-harness.mjs"
$cliContent = [System.IO.File]::ReadAllText($CliSrc, [System.Text.Encoding]::UTF8)
$cliContent = $cliContent.Replace("from '../validators/", "from './validators/")
$cliContent = $cliContent.Replace('from "../validators/', 'from "./validators/')
[System.IO.File]::WriteAllText($CliDst, $cliContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "  [复制] scripts\harness\validate-harness.mjs" -ForegroundColor Green

$StatusSrc = Join-Path $HarnessScripts "status.mjs"
$StatusDst = Join-Path $TargetHarness "status.mjs"
if (Test-Path $StatusSrc) {
    Copy-Item $StatusSrc $StatusDst -Force
    Write-Host "  [复制] scripts\harness\status.mjs" -ForegroundColor Green
} else {
    Write-Host "  [警告] 未找到 status.mjs，跳过" -ForegroundColor Yellow
}

# Step 3: HARNESS_RULES.md
$SuperpowersBase = Join-Path $ProjectRoot "docs\superpowers"
New-Item -ItemType Directory -Force -Path $SuperpowersBase | Out-Null
$RulesSrc = Join-Path $HarnessRoot "references\HARNESS_RULES.md"
$RulesDst = Join-Path $SuperpowersBase "HARNESS_RULES.md"
if (-not (Test-Path $RulesDst)) {
    Copy-Item $RulesSrc $RulesDst
    Write-Host "  [创建] docs\superpowers\HARNESS_RULES.md" -ForegroundColor Green
} else {
    Write-Host "  [跳过] HARNESS_RULES.md 已存在" -ForegroundColor DarkGray
}

# Step 4: AGENTS.md
$AgentsDst = Join-Path $ProjectRoot "AGENTS.md"
if (-not (Test-Path $AgentsDst)) {
    $Template = [System.IO.File]::ReadAllText((Join-Path $HarnessRoot "references\AGENTS.md.template"), [System.Text.Encoding]::UTF8)
    $Agents = $Template.Replace('{{FRAMEWORK}}', 'Vue 3 + Vite + TypeScript')
    $Agents = $Agents.Replace('{{UI_LIB}}', 'Element Plus')
    $Agents = $Agents.Replace('{{STATE}}', 'Pinia')
    [System.IO.File]::WriteAllText($AgentsDst, $Agents, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  [创建] AGENTS.md" -ForegroundColor Green
} else {
    Write-Host "  [跳过] AGENTS.md 已存在" -ForegroundColor DarkGray
}

# Step 5: .cursorrules 片段
$CursorRules = Join-Path $ProjectRoot ".cursorrules"
$Snippet = [System.IO.File]::ReadAllText((Join-Path $HarnessRoot "references\cursorrules.snippet"), [System.Text.Encoding]::UTF8)
if (Test-Path $CursorRules) {
    $Existing = [System.IO.File]::ReadAllText($CursorRules, [System.Text.Encoding]::UTF8)
    if ($Existing -notmatch 'Harness 门禁') {
        [System.IO.File]::AppendAllText($CursorRules, "`n$Snippet", [System.Text.UTF8Encoding]::new($false))
        Write-Host "  [追加] .cursorrules Harness 片段" -ForegroundColor Green
    } else {
        Write-Host "  [跳过] .cursorrules 已含 Harness 片段" -ForegroundColor DarkGray
    }
} else {
    [System.IO.File]::WriteAllText($CursorRules, $Snippet, [System.Text.UTF8Encoding]::new($false))
    Write-Host "  [创建] .cursorrules" -ForegroundColor Green
}

# Step 6: 同步 superpowers-harness skill（跳过源目录自身）
$HarnessRootResolved = (Resolve-Path $HarnessRoot).Path
foreach ($Target in @(
    (Join-Path $ProjectRoot ".agents\skills\superpowers-harness"),
    (Join-Path $ProjectRoot ".cursor\skills\superpowers-harness")
)) {
    $TargetResolved = (Resolve-Path $Target -ErrorAction SilentlyContinue)
    if ($TargetResolved -and $TargetResolved.Path -eq $HarnessRootResolved) {
        Write-Host "  [跳过] 源目录与目标相同: $Target" -ForegroundColor DarkGray
        continue
    }
    $Parent = Split-Path $Target -Parent
    New-Item -ItemType Directory -Force -Path $Parent | Out-Null
    if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
    Copy-Item -Path $HarnessRoot -Destination $Target -Recurse -Force
    Write-Host "  [同步] $Target" -ForegroundColor Green
}

# Step 6b: 同步 superpowers-harness-run 编排技能
$RunSkillRoot = Join-Path $AgentsSkills "superpowers-harness-run"
if (Test-Path $RunSkillRoot) {
    foreach ($Target in @(
        (Join-Path $ProjectRoot ".agents\skills\superpowers-harness-run"),
        (Join-Path $ProjectRoot ".cursor\skills\superpowers-harness-run")
    )) {
        $Parent = Split-Path $Target -Parent
        New-Item -ItemType Directory -Force -Path $Parent | Out-Null
        if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
        Copy-Item -Path $RunSkillRoot -Destination $Target -Recurse -Force
        Write-Host "  [同步] $Target" -ForegroundColor Green
    }
} else {
    Write-Host "  [警告] 未找到 superpowers-harness-run skill，跳过" -ForegroundColor Yellow
}

# Step 6c: 同步 .cursor/commands/harness.md（/harness 命令）
$SkillRepoRoot = Split-Path -Parent (Split-Path -Parent $AgentsSkills)
$CmdSrc = Join-Path $SkillRepoRoot ".cursor\commands\harness.md"
if (Test-Path $CmdSrc) {
    $CmdDst = Join-Path $ProjectRoot ".cursor\commands\harness.md"
    New-Item -ItemType Directory -Force -Path (Split-Path $CmdDst -Parent) | Out-Null
    Copy-Item $CmdSrc $CmdDst -Force
    Write-Host "  [同步] .cursor\commands\harness.md" -ForegroundColor Green
} else {
    Write-Host "  [警告] 未找到 harness.md 命令，跳过" -ForegroundColor Yellow
}

# Step 7: package.json harness 脚本 + pre-commit
$PkgPath = Join-Path $ProjectRoot "package.json"
if (Test-Path $PkgPath) {
    $Pkg = Get-Content $PkgPath -Raw -Encoding UTF8 | ConvertFrom-Json
} else {
    $Pkg = [pscustomobject]@{
        name    = (Split-Path -Leaf $ProjectRoot)
        version = '1.0.0'
        private = $true
        type    = 'module'
    }
    Write-Host "  [创建] package.json" -ForegroundColor Green
}

$hook = 'node scripts/harness/validate-harness.mjs || exit 0'

if (-not $Pkg.PSObject.Properties['scripts']) {
    $Pkg | Add-Member -NotePropertyName 'scripts' -NotePropertyValue @{} -Force
}
$scripts = $Pkg.scripts
$harnessScripts = @{
    'harness:status' = 'node scripts/harness/status.mjs'
    'harness:check'  = 'node scripts/harness/validate-harness.mjs'
    'harness:strict' = 'node scripts/harness/validate-harness.mjs --strict'
}
foreach ($k in $harnessScripts.Keys) {
    $hasKey = if ($scripts -is [System.Management.Automation.PSCustomObject]) {
        [bool]$scripts.PSObject.Properties[$k]
    } else {
        $scripts.ContainsKey($k)
    }
    if (-not $hasKey) {
        if ($scripts -is [System.Management.Automation.PSCustomObject]) {
            $scripts | Add-Member -NotePropertyName $k -NotePropertyValue $harnessScripts[$k] -Force
        } else {
            $scripts[$k] = $harnessScripts[$k]
        }
    }
}

if (-not $Pkg.PSObject.Properties['simple-git-hooks']) {
    $Pkg | Add-Member -NotePropertyName 'simple-git-hooks' -NotePropertyValue @{} -Force
}
$sgh = $Pkg.'simple-git-hooks'
$hasPreCommit = if ($sgh -is [System.Management.Automation.PSCustomObject]) {
    [bool]$sgh.PSObject.Properties['pre-commit'] -and $sgh.'pre-commit'
} else {
    $sgh.ContainsKey('pre-commit') -and $sgh['pre-commit']
}
if ($hasPreCommit) {
    $existing = if ($sgh -is [System.Management.Automation.PSCustomObject]) { $sgh.'pre-commit' } else { $sgh['pre-commit'] }
    if ($existing -notmatch 'validate-harness') {
        $merged = "$existing && $hook"
        if ($sgh -is [System.Management.Automation.PSCustomObject]) {
            $sgh.'pre-commit' = $merged
        } else {
            $sgh['pre-commit'] = $merged
        }
    }
} else {
    if ($sgh -is [System.Management.Automation.PSCustomObject]) {
        $sgh | Add-Member -NotePropertyName 'pre-commit' -NotePropertyValue $hook -Force
    } else {
        $sgh['pre-commit'] = $hook
    }
}
[System.IO.File]::WriteAllText($PkgPath, ($Pkg | ConvertTo-Json -Depth 10), [System.Text.UTF8Encoding]::new($false))
Write-Host "  [更新] package.json harness 脚本 + pre-commit" -ForegroundColor Green

# Step 8: .gitignore
$Gitignore = Join-Path $ProjectRoot ".gitignore"
if (Test-Path $Gitignore) {
    $Gi = [System.IO.File]::ReadAllText($Gitignore, [System.Text.Encoding]::UTF8)
    if ($Gi -notmatch '\.harness/') {
        [System.IO.File]::AppendAllText($Gitignore, "`n.harness/`n", [System.Text.UTF8Encoding]::new($false))
        Write-Host "  [追加] .gitignore .harness/" -ForegroundColor Green
    }
} else {
    [System.IO.File]::WriteAllText($Gitignore, ".harness/`n", [System.Text.UTF8Encoding]::new($false))
    Write-Host "  [创建] .gitignore (.harness/)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Harness 安装完成。" -ForegroundColor Green
Write-Host "  自查: pnpm harness:status / pnpm harness:check" -ForegroundColor Green
Write-Host "  规则: docs\superpowers\HARNESS_RULES.md" -ForegroundColor Green
Write-Host "  技能: superpowers-harness-run (/harness)" -ForegroundColor Green
