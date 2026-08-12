# scripts/create-demand.ps1
param(
    [string]$Type,
    [string]$Name,
    [string]$Version,
    [switch]$InitVersion,
    [switch]$Interactive,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ValidTypes = @("feature", "ui-style", "api-adapter", "fix")
$TypeLabels = @{
    "feature"      = "新功能 / 新页面"
    "ui-style"     = "UI 还原 / 视觉改版"
    "api-adapter"  = "接口对接 / 联调"
    "fix"          = "Bug / 兼容性修复"
}
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SuperpowersBase = Join-Path $ProjectRoot "docs\superpowers"

function Write-Title([string]$Text) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Text" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

function Read-YesNo([string]$Prompt, [bool]$DefaultYes = $true) {
    $hint = if ($DefaultYes) { "Y/n" } else { "y/N" }
    while ($true) {
        $answer = Read-Host "$Prompt [$hint]"
        if ([string]::IsNullOrWhiteSpace($answer)) { return $DefaultYes }
        $v = $answer.Trim().ToLower()
        if ($v -in @("y", "yes")) { return $true }
        if ($v -in @("n", "no")) { return $false }
        Write-Host "  请输入 Y 或 N" -ForegroundColor Yellow
    }
}

function Normalize-SuperpowersVersion([string]$Ver) {
    if ($Ver -match '^v\d+\.\d+$') { return "$Ver.0" }
    return $Ver
}

function Resolve-SuperpowersVersionDir([string]$Ver) {
    $normalized = Normalize-SuperpowersVersion $Ver
    $exact = Join-Path $SuperpowersBase $normalized
    if (Test-Path $exact) { return $normalized }
    if ($normalized -match '^v(\d+)\.(\d+)\.0$') {
        $legacy = "v$($Matches[1]).$($Matches[2])"
        $legacyPath = Join-Path $SuperpowersBase $legacy
        if (Test-Path $legacyPath) { return $legacy }
    }
    return $normalized
}

function Get-SuperpowersVersion {
    $currentLink = Join-Path $SuperpowersBase "current"
    $currentTxt = Join-Path $SuperpowersBase "current-version.txt"
    $raw = "v1.0.0"

    if (Test-Path $currentLink) {
        $item = Get-Item $currentLink -Force
        if ($item.LinkType) {
            $target = $item.Target
            if ($target -is [array]) { $target = $target[0] }
            $raw = ($target -replace '^\./', '')
        }
    } elseif (Test-Path $currentTxt) {
        $raw = (Get-Content $currentTxt -Raw -Encoding UTF8).Trim()
    }
    return (Normalize-SuperpowersVersion $raw)
}

function Ensure-Dir([string]$Path) {
    if (Test-Path $Path) {
        Write-Host "  [跳过] 已存在: $Path" -ForegroundColor DarkGray
    } else {
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
        Write-Host "  [创建] $Path" -ForegroundColor Green
    }
}

function Init-VersionSkeleton([string]$Ver) {
    $versionDir = Join-Path $SuperpowersBase $Ver
    Write-Host "初始化版本骨架: $versionDir"
    foreach ($t in $ValidTypes) {
        Ensure-Dir (Join-Path $versionDir $t)
    }
}

function New-ModuleDirs([string]$Ver, [string]$Type, [string]$ModuleName) {
    $moduleRoot = Join-Path $SuperpowersBase "$Ver\$Type\$ModuleName"
    Write-Host ""
    Write-Host "创建模块: $moduleRoot" -ForegroundColor Cyan
    Ensure-Dir (Join-Path $moduleRoot "requirements")
    Ensure-Dir (Join-Path $moduleRoot "archive")
    Ensure-Dir (Join-Path $moduleRoot "specs")
    Ensure-Dir (Join-Path $moduleRoot "plans")

    Write-Host ""
    Write-Host "完成。模块根目录:" -ForegroundColor Green
    Write-Host "  $moduleRoot"
    return $moduleRoot
}

function Show-NextSteps([string]$Type, [string]$ModuleName) {
    Write-Host ""
    Write-Host "下一步建议:" -ForegroundColor Cyan
    Write-Host "  1. 将原始需求写入 requirements/"
    Write-Host "  2. brainstorming → specs/01-dev-spec.md"
    Write-Host "  3. writing-plans → plans/01-dev-plan.md"
    Write-Host "  4. 开发完成后归档到 archive/"
}

function Start-Interactive {
    Clear-Host
    Write-Title "Superpowers 新建需求目录"

    $ver = Get-SuperpowersVersion
    $verDir = Resolve-SuperpowersVersionDir $ver
    Write-Host "当前版本: $ver (目录: $verDir)" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "请选择需求分类:" -ForegroundColor Cyan
    for ($i = 0; $i -lt $ValidTypes.Count; $i++) {
        $t = $ValidTypes[$i]
        Write-Host "  $($i + 1). $t  - $($TypeLabels[$t])"
    }
    Write-Host ""

    while ($true) {
        $pick = Read-Host "输入序号 (1-4)"
        if ($pick -match '^\d+$') {
            $idx = [int]$pick - 1
            if ($idx -ge 0 -and $idx -lt $ValidTypes.Count) {
                $script:Type = $ValidTypes[$idx]
                break
            }
        }
        Write-Host "  请输入 1 到 4" -ForegroundColor Red
    }

    Write-Host ""
    while ($true) {
        $script:Name = Read-Host "请输入中文模块名 (如: 登录注册功能)"
        $script:Name = $script:Name.Trim()
        if (-not [string]::IsNullOrWhiteSpace($script:Name)) { break }
        Write-Host "  模块名不能为空" -ForegroundColor Red
    }

    $moduleRoot = Join-Path $SuperpowersBase "$verDir\$Type\$Name"
    Write-Host ""
    Write-Host "将创建目录:" -ForegroundColor Cyan
    Write-Host "  $moduleRoot"
    Write-Host "    requirements\   (原始需求)"
    Write-Host "    archive\        (归档)"
    Write-Host "    specs\"
    Write-Host "    plans\"

    Write-Host ""
    if (-not (Read-YesNo "确认创建?" $true)) {
        Write-Host "已取消。" -ForegroundColor Yellow
        exit 0
    }

    Init-VersionSkeleton $verDir
    $root = New-ModuleDirs $verDir $Type $Name
    Show-NextSteps $Type $Name
}

if ($Help) {
    Write-Host "用法:"
    Write-Host "  双击 create-demand.bat          # 交互式"
    Write-Host "  create-demand.bat --type feature --name `"模块名`""
    Write-Host "  create-demand.bat --init-version [--version v1.0.0]"
    exit 0
}

if ($InitVersion) {
    $ver = if ($Version) { Normalize-SuperpowersVersion $Version } else { Get-SuperpowersVersion }
    Init-VersionSkeleton $ver
    exit 0
}

# 无参数时进入交互模式（双击 bat 场景）
if ($Interactive -or (-not $Type -and -not $Name)) {
    Start-Interactive
    exit 0
}

if (-not $Type -or -not $Name) {
    Write-Host "错误: 缺少 --type 或 --name。直接双击 bat 可进入交互模式。" -ForegroundColor Red
    exit 1
}

if ($ValidTypes -notcontains $Type) {
    Write-Host "错误: 非法分类 '$Type'。允许: $($ValidTypes -join ', ')" -ForegroundColor Red
    exit 1
}

$ver = if ($Version) { Normalize-SuperpowersVersion $Version } else { Get-SuperpowersVersion }
$verDir = if ($Version) { $ver } else { Resolve-SuperpowersVersionDir $ver }
Init-VersionSkeleton $verDir
New-ModuleDirs $verDir $Type $Name | Out-Null
