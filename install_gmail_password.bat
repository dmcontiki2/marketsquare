@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_gmail_password.ps1"
if errorlevel 1 pause
