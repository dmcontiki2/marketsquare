@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0trace_email_secret.ps1"
if errorlevel 1 pause
