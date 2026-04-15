@echo off
title Session Starting — MarketSquare...
color 0A

:: ════════════════════════════════════════════════════════════
::  start_marketsquare.bat
::  Session Startup — MarketSquare + Related Projects
::  Place this file on your Desktop
::  Double-click to begin any development session
::
::  Opens:
::    - trustsquare.co (buyer app)
::    - trustsquare.co/admin.html (admin tool)
::    - trustsquare.co/launch/ (CityLauncher)
::    - Projects folder in Explorer
::    - Claude Code at C:\Users\David\Projects\MarketSquare
::
::  Projects:
::    MarketSquare  — main app (includes Advert Agent, BEA, FEA)
::    CityLauncher  — launch dashboard at /launch/
::    SellerScraper — lead generation tool
::
::  Note: Advert Agent (AA) is integrated into MarketSquare.
::  No separate AdvertAgent project window needed.
:: ════════════════════════════════════════════════════════════

set PROJECTS=C:\Users\David\Projects
set MS=%PROJECTS%\MarketSquare

echo.
echo  ============================================================
echo   SESSION STARTING  ^|  MarketSquare
echo  ============================================================
echo.

:: ── Step 1: Copy session start prompt to clipboard ───────────
echo  [1/5] Copying session start prompt to clipboard...
if exist "%MS%\SESSION_START_PROMPT.md" (
    powershell -NoProfile -Command "Get-Content '%MS%\SESSION_START_PROMPT.md' -Raw -Encoding UTF8 | Set-Clipboard; Write-Host '  Done.'"
) else (
    powershell -NoProfile -Command "Set-Clipboard -Value 'Read STATUS.md first, then AGENT_BRIEFING.md.'; Write-Host '  Fallback copied.'"
)
echo.

:: ── Step 2: Open live sites in browser ───────────────────────
echo  [2/5] Opening live sites...
start "" "https://trustsquare.co?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/admin.html?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/launch/?v=%random%"
timeout /t 1 /nobreak >nul
echo.

:: ── Step 3: Open Projects folder in Explorer ─────────────────
echo  [3/5] Opening MarketSquare project folder...
explorer "%MS%"
timeout /t 1 /nobreak >nul
echo.

:: ── Step 4: Launch Claude Code — MarketSquare ────────────────
echo  [4/5] Launching Claude Code (MarketSquare)...
wt -d "%MS%" cmd /k "claude"
timeout /t 2 /nobreak >nul
echo.

:: ── Step 5: Launch Claude Code — Projects root ───────────────
echo  [5/5] Launching Claude Code (Projects root)...
wt -d "%PROJECTS%" cmd /k "claude"
timeout /t 2 /nobreak >nul
echo.

echo  ============================================================
echo   ALL DONE — YOUR SESSION IS READY
echo  ============================================================
echo.
echo  Browser:
echo    trustsquare.co             buyer app (Advert Agent integrated)
echo    trustsquare.co/admin.html  admin tool
echo    trustsquare.co/launch/     CityLauncher dashboard
echo.
echo  Claude Code windows:
echo    C:\Users\David\Projects\MarketSquare   (primary — AA + BEA + FEA)
echo    C:\Users\David\Projects               (all projects root)
echo.
echo  Clipboard holds SESSION_START_PROMPT — Ctrl+V in Claude Code.
echo.
echo  ── Quick deploy (or use deploy_marketsquare.bat) ───────────
echo   scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo   scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
echo   scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
echo   ssh root@178.104.73.239 "systemctl restart marketsquare"
echo.
timeout /t 8 /nobreak >nul
exit
