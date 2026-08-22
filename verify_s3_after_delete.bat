@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_s3_after_delete.ps1"
if errorlevel 1 pause
