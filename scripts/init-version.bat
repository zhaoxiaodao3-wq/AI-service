@echo off
chcp 65001 >nul
title Superpowers Init Version
cd /d "%~dp0.."

powershell -NoProfile -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; & '%~dp0init-version.ps1'"
if errorlevel 1 (
  echo.
  echo Script failed. See errors above.
)

echo.
pause
