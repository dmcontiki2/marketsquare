@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0purge_gmail_password.ps1"
if errorlevel 1 pause
