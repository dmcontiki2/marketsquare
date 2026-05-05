@echo off
title TrustSquare · Session Starting...
color 0A

:: ════════════════════════════════════════════════════════════
::  start_marketsquare.bat
::  Session Startup — TrustSquare (Cowork mode)
::  Double-click to begin any development session
::
::  Opens:
::    - trustsquare.co (buyer app)
::    - trustsquare.co/admin.html (admin tool)
::    - Projects folder in Explorer
::    - Claude desktop (Cowork)
::
::  NOTE: No Claude Code / terminal windows are launched.
::  NOTE: CityLauncher dashboard removed — not in active use.
:: ════════════════════════════════════════════════════════════

set PROJECTS=C:\Users\David\Projects
set MS=%PROJECTS%\MarketSquare

echo.
echo  ============================================================
echo   TRUSTSQUARE  ^|  Session Starting...
echo  %DATE%   %TIME%
echo  ============================================================
echo.

:: ── Step 1: Open live sites in browser ───────────────────────
echo  [1/3] Opening live sites and admin app in browser...
start "" "https://trustsquare.co?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/admin.html?v=%random%"
timeout /t 1 /nobreak >nul
echo   Done.
echo.

:: ── Step 2: Open Projects folder in Explorer ─────────────────
echo  [2/3] Opening MarketSquare project folder...
explorer "%MS%"
timeout /t 1 /nobreak >nul
echo.

:: ── Step 3: Copy session start prompt + launch Claude Cowork ─
echo  [3/3] Copying session start prompt to clipboard...
if exist "%MS%\SESSION_START_PROMPT.md" (
    powershell -NoProfile -Command "Get-Content '%MS%\SESSION_START_PROMPT.md' -Raw -Encoding UTF8 | Set-Clipboard; Write-Host '   SESSION_START_PROMPT.md on clipboard — paste into Cowork when ready.'"
) else (
    powershell -NoProfile -Command "Set-Clipboard -Value 'Read STATUS.md first, then AGENT_BRIEFING.md.'; Write-Host '   Fallback prompt copied.'"
)
echo.

echo  ============================================================
echo   SESSION READY
echo  ============================================================
echo.
echo  Browser tabs:
echo    trustsquare.co              buyer app
echo    trustsquare.co/admin.html   admin tool
echo.
echo  Clipboard: TrustSquare SESSION_START_PROMPT — paste into Cowork to start
echo.
echo  ── Quick deploy commands ────────────────────────────────────
echo   scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo   scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
echo   scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
echo   ssh root@178.104.73.239 "systemctl restart marketsquare"
echo.
timeout /t 8 /nobreak >nul
exit
