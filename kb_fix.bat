@echo off
REM Launcher for kb_fix.ps1 - asks for admin rights, then hands over to
REM PowerShell, which records the whole run to a file even if it crashes.
REM The window is held open at the end either way.
net session >nul 2>&1
if errorlevel 1 (
  echo.
  echo Asking Windows for administrator rights. Please say Yes.
  powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)
powershell -NoProfile -ExecutionPolicy Bypass -NoExit -File "%~dp0kb_fix.ps1"
