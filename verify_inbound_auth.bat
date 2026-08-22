@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_inbound_auth.ps1"
if errorlevel 1 pause
