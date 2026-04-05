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

:: ── Step 1: Copy SESSION_START_PROMPT to clipboard ──────────
echo  [1/5] Copying session start prompt to clipboard...

if exist "%PROJECT%\SESSION_START_PROMPT.md" (
    powershell -NoProfile -Command "Get-Content '%PROJECT%\SESSION_START_PROMPT.md' -Raw -Encoding UTF8 | Set-Clipboard; Write-Host '  Done — session start prompt is on your clipboard.'"
) else (
    powershell -NoProfile -Command "Set-Clipboard -Value 'Read STATUS.md first, then AGENT_BRIEFING.md.'; Write-Host '  SESSION_START_PROMPT.md not found — fallback copied.'"
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
echo  Your clipboard holds the session start prompt — just Ctrl+V + Enter in Claude Code.
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
echo   Read SESSION_START_PROMPT.md now.
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
echo   Or run deploy_marketsquare.bat to deploy all files.
echo   scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo   scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
echo   scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
echo   ssh root@178.104.73.239 "systemctl restart marketsquare"
echo.
timeout /t 8 /nobreak >nul
exit
