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

:: ── Step 0: Git pull — sync all projects from GitHub ─────────
echo  [0/3] Pulling latest from GitHub (source of truth)...
cd /d "%MS%"
git pull origin main
echo.
cd /d "%PROJECTS%\CityLauncher"
git pull origin main
echo.
cd /d "%PROJECTS%\AdvertAgent"
git pull origin main
echo.
cd /d "%MS%"
echo   All projects synced from GitHub.
echo.

:: ── Step 1: Open live sites in browser ───────────────────────
echo  [1/4] Opening live sites and admin app in browser...
start "" "https://trustsquare.co?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/admin.html?v=%random%"
timeout /t 1 /nobreak >nul
echo   Done.
echo.

:: ── Step 2: Open Projects folder in Explorer ─────────────────
echo  [2/4] Opening MarketSquare project folder...
explorer "%MS%"
timeout /t 1 /nobreak >nul
echo.

:: ── Step 3: Launch session dashboard ────────────────────────
echo  [3/4] Launching session dashboard...
if exist "%MS%\session_dashboard.py" (
    cd /d "%MS%"
    start "" /B python "%MS%\session_dashboard.py"
    timeout /t 3 /nobreak >nul
) else (
    echo   WARNING: session_dashboard.py not found — falling back to clipboard prompt.
    if exist "%MS%\SESSION_START_PROMPT.md" (
        powershell -NoProfile -Command "Get-Content '%MS%\SESSION_START_PROMPT.md' -Raw -Encoding UTF8 | Set-Clipboard; Write-Host '   SESSION_START_PROMPT.md on clipboard.'"
    )
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
echo  Dashboard: session_dashboard_live.html — choose direction, copy prompt, paste into Cowork
echo.
echo  ── Quick deploy commands ────────────────────────────────────
echo   scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo   scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
echo   scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
echo   ssh root@178.104.73.239 "systemctl restart marketsquare"
echo.
timeout /t 8 /nobreak >nul
exit
