@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_cf_token.ps1"
if errorlevel 1 pause
