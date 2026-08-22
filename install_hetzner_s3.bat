@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_hetzner_s3.ps1"
if errorlevel 1 pause
