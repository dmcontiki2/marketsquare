@echo off
:: notify_attention.bat - WINDOW-ZORDER-1 (25 Aug 2026)
:: Thin wrapper, same idiom as diag_gmail.bat. %~1 = the window title to set.
:: Fails silent by design: a deploy must never die because a beep did not play.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0notify_attention.ps1" -Title "%~1" >nul 2>&1
exit /b 0
