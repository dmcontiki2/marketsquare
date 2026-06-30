@echo off
REM ==========================================================================
REM  repair_claude_mem.bat  -  double-click (or run) this to repair claude-mem
REM  Wraps the PowerShell repair so Windows execution policy / blocked-file
REM  flags can't stop it. Built 2026-06-28.
REM ==========================================================================
echo.
echo  Running claude-mem repair... (this window will stay open when done)
echo.
cd /d "%~dp0"

REM Unblock the ps1 in case Windows marked it as downloaded, then run it
REM with a policy bypass scoped to THIS process only.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Unblock-File -Path '%~dp0repair_claude_mem.ps1' -ErrorAction SilentlyContinue; & '%~dp0repair_claude_mem.ps1'"

echo.
echo  ==========================================================================
echo   Repair script finished. Read the [repair] lines above.
echo   If you see errors, copy this whole window to Claude.
echo  ==========================================================================
echo.
pause
