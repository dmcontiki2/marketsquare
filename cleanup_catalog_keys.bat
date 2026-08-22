@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0cleanup_catalog_keys.ps1"
if errorlevel 1 pause
