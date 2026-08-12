# scripts/init-version.ps1
# 交互式初始化 Superpowers 新版本目录（双击 init-version.bat）

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ValidTypes = @("feature", "ui-style", "api-adapter", "fix")
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SuperpowersBase = Join-Path $ProjectRoot "docs\superpowers"
$CurrentTxt = Join-Path $SuperpowersBase "current-version.txt"
$CurrentLink = Join-Path $SuperpowersBase "current"

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
        if ([string]::IsNullOrWhiteSpace($answer)) {
            return $DefaultYes
        }
        $v = $answer.Trim().ToLower()
        if ($v -in @("y", "yes")) { return $true }
        if ($v -in @("n", "no")) { return $false }
        Write-Host "  请输入 Y 或 N" -ForegroundColor Yellow
    }
}

function Get-CurrentVersion {
    if (Test-Path $CurrentLink) {
        $item = Get-Item $CurrentLink -Force
        if ($item.LinkType) {
            $target = $item.Target
            if ($target -is [array]) { $target = $target[0] }
            $raw = ($target -replace '^\./', '')
            return (Normalize-SuperpowersVersion $raw)
        }
    }
    if (Test-Path $CurrentTxt) {
        $raw = (Get-Content $CurrentTxt -Raw -Encoding UTF8).Trim()
        return (Normalize-SuperpowersVersion $raw)
    }
    return "v1.0.0"
}

function Normalize-SuperpowersVersion([string]$Ver) {
    if ($Ver -match '^v\d+\.\d+$') { return "$Ver.0" }
    return $Ver
}

function Set-CurrentVersion([string]$Ver) {
    $normalized = Normalize-SuperpowersVersion $Ver
    [System.IO.File]::WriteAllText($CurrentTxt, "$normalized`n", [System.Text.UTF8Encoding]::new($false))
    Write-Host "  已更新: $CurrentTxt -> $normalized" -ForegroundColor Green
}

function Ensure-Dir([string]$Path) {
    if (Test-Path $Path) {
        Write-Host "  [跳过] 已存在: $Path" -ForegroundColor DarkGray
        return $false
    }
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    Write-Host "  [创建] $Path" -ForegroundColor Green
    return $true
}

function Init-VersionSkeleton([string]$Ver) {
    $versionDir = Join-Path $SuperpowersBase $Ver
    $created = 0
    foreach ($t in $ValidTypes) {
        if (Ensure-Dir (Join-Path $versionDir $t)) { $created++ }
    }
    return @{ Dir = $versionDir; Created = $created }
}

function Test-VersionFormat([string]$Ver) {
    return $Ver -match '^v\d+\.\d+\.\d+$'
}

Clear-Host
Write-Title "Superpowers 新版本目录初始化"

$current = Get-CurrentVersion
Write-Host "当前活跃版本: $current" -ForegroundColor Yellow
Write-Host "根目录: $SuperpowersBase"
Write-Host ""

while ($true) {
    $newVer = Read-Host "请输入新版本号 (格式 v主.次.修订，如 v1.1.0)"
    $newVer = $newVer.Trim()
    if (-not (Test-VersionFormat $newVer)) {
        Write-Host "  格式错误，请使用如 v1.1.0、v2.0.0 的格式" -ForegroundColor Red
        continue
    }
    if ($newVer -eq $current) {
        Write-Host "  与当前版本相同" -ForegroundColor Yellow
    }
    break
}

Write-Host ""
Write-Host "将创建以下目录:" -ForegroundColor Cyan
$versionDir = Join-Path $SuperpowersBase $newVer
foreach ($t in $ValidTypes) {
    $p = Join-Path $versionDir $t
    $status = if (Test-Path $p) { "(已存在)" } else { "(新建)" }
    Write-Host "  $p $status"
}

Write-Host ""
if (-not (Read-YesNo "确认创建版本 $newVer 的目录骨架?" $true)) {
    Write-Host "已取消。" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "正在创建..." -ForegroundColor Cyan
$result = Init-VersionSkeleton $newVer
Write-Host ""
Write-Host "完成。新建 $($result.Created) 个分类目录。" -ForegroundColor Green

Write-Host ""
$switch = Read-YesNo "是否将 current 切换到 $newVer ? (更新 current-version.txt)" $true
if ($switch) {
    Set-CurrentVersion $newVer
    Write-Host ""
    Write-Host "后续新建需求将默认写入: docs\superpowers\$newVer\" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "未切换 current。临时指定版本示例:" -ForegroundColor Yellow
    Write-Host "  scripts\create-demand.bat --type feature --name `"模块名`" --version $newVer"
}

Write-Host ""
Write-Host "----------------------------------------"
Write-Host "  初始化完成" -ForegroundColor Green
Write-Host "  版本目录: $versionDir"
Write-Host "  当前活跃: $(Get-CurrentVersion)"
Write-Host "----------------------------------------"
