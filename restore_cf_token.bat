@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restore_cf_token.ps1"
if errorlevel 1 pause
