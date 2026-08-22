@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check_all_lanes.ps1"
if errorlevel 1 pause
