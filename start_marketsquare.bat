@echo off
title MarketSquare · Starting Session...
color 0A

:: ════════════════════════════════════════════════════════════
::  start_marketsquare.bat
::  MarketSquare · Session Startup Script
::  Place this file on your Desktop
::  Double-click to begin any development session
:: ════════════════════════════════════════════════════════════

set PROJECT=C:\Users\David\Projects\MarketSquare
set CHANGELOG=%PROJECT%\CHANGELOG.md

echo.
echo  ============================================================
echo   MARKETSQUARE  ^|  Session Starting...
echo  ============================================================
echo.

:: ── Step 1: Copy last CHANGELOG entry to clipboard ──────────
echo  [1/5] Copying last session summary to clipboard...

if exist "%CHANGELOG%" (
    powershell -NoProfile -Command "$content = Get-Content '%CHANGELOG%' -Raw -Encoding UTF8; $blocks = $content -split '(?m)^## '; $last = $blocks[-1].Trim(); $formatted = '## ' + $last; Set-Clipboard -Value $formatted; Write-Host '  Done — last session summary is on your clipboard.'"
) else (
    powershell -NoProfile -Command "Set-Clipboard -Value 'New MarketSquare session. No previous CHANGELOG entry found.'; Write-Host '  No CHANGELOG found — placeholder copied.'"
)

echo.

:: ── Step 2: Open Claude Chat in browser ─────────────────────
echo  [2/5] Opening Claude Chat...
start "" "https://claude.ai/new"
timeout /t 2 /nobreak >nul

:: ── Step 3: Open project folder for file uploads ────────────
echo  [3/5] Opening project folder...
explorer "%PROJECT%"
timeout /t 1 /nobreak >nul

:: ── Step 4: Open live site and admin tool ───────────────────
echo  [4/5] Opening trustsquare.co and admin panel...
start "" "https://trustsquare.co?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/admin.html?v=%random%"
timeout /t 1 /nobreak >nul

:: ── Step 5: Launch Claude Code in Windows Terminal ──────────
echo  [5/5] Launching Claude Code...
wt -d "%PROJECT%" cmd /k "claude"

echo.
echo  ============================================================
echo   ALL DONE — YOUR SESSION IS READY
echo  ============================================================
echo.
echo  Your clipboard holds the last CHANGELOG session summary.
echo.
echo  In Claude Chat:
echo    1. Upload CLAUDE.md
echo    2. Upload AGENT_BRIEFING.md
echo    3. Upload Solar_Council_Codex_v4_3.docx
echo    4. Upload STATUS.md
echo    5. Upload marketsquare.html
echo    6. Upload marketsquare_admin.html
echo    7. Upload CHANGELOG.md
echo    8. Press Ctrl+V to paste session context
echo    9. Press Enter — Claude is fully briefed
echo.
echo  Claude Code — paste this to START the session:
echo  ────────────────────────────────────────────────
echo   Read STATUS.md first, then AGENT_BRIEFING.md.
echo  ────────────────────────────────────────────────
echo.
echo  Claude Code — paste this to END the session:
echo  ────────────────────────────────────────────────
echo   Session complete. Now:
echo   1) Update STATUS.md - move completed tasks to
echo      Last Completed, write the exact next task.
echo      Keep it under 60 lines.
echo   2) Append one paragraph per completed task
echo      to CHANGELOG.md.
echo   3) Git commit with message: "Session X complete"
echo   4) Push to GitHub.
echo  ────────────────────────────────────────────────
echo.
timeout /t 8 /nobreak >nul
exit
