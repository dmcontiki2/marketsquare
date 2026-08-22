@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0place_inbound_secrets.ps1"
if errorlevel 1 pause
