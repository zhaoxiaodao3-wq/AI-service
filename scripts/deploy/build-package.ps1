# ============================================================
# 本地打包 AI-agent 部署包（Windows PowerShell）
# 用法: powershell -ExecutionPolicy Bypass -File scripts/deploy/build-package.ps1
# 输出: dist/aigc-agent.tar.gz（不含 .git/node_modules/venv/.env 密钥）
# 可选: -IncludeEnv 把 .env 一起打进去（不推荐，密钥应单独 scp）
# ============================================================
param(
  [string]$OutDir = (Join-Path $PSScriptRoot '..\..\dist'),
  [switch]$IncludeEnv
)
$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$out  = Join-Path $OutDir 'aigc-agent.tar.gz'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$excludes = @(
  '--exclude=.git',
  '--exclude=node_modules',
  '--exclude=.pnpm-store',
  '--exclude=venv',
  '--exclude=__pycache__',
  '--exclude=.pytest_cache',
  '--exclude=.pytest-tmp*',
  '--exclude=.pt-*',
  '--exclude=pytest-cache-files-*',
  '--exclude=*.pyc',
  '--exclude=dist',
  '--exclude=data/uploads',
  '--exclude=.harness',
  '--exclude=.agents',
  '--exclude=.cursor',
  '--exclude=.cursorrules'
)
if (-not $IncludeEnv) {
  $excludes += @('--exclude=.env', '--exclude=backend/.env')
}

Write-Host "打包目录: $root"
Push-Location $root
try {
  tar -czf $out $excludes --exclude=aigc-agent.tar.gz .
  if ($LASTEXITCODE -ne 0) { throw "tar 退出码 $LASTEXITCODE" }
} finally {
  Pop-Location
}
Write-Host "打包完成: $out"
