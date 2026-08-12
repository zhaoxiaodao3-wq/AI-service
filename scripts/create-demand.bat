@echo off
chcp 65001 >nul
title Superpowers 新建需求
cd /d "%~dp0.."

if "%~1"=="" (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '%~dp0create-demand.ps1' -Interactive"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '%~dp0create-demand.ps1' %*"
)

if errorlevel 1 (
  echo.
  echo 执行失败，请查看上方错误信息。
)

echo.
pause
