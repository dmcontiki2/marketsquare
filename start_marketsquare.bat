@echo off
title TrustSquare - Session Starting...
color 0A

set PROJECTS=C:\Users\David\Projects
set MS=%PROJECTS%\MarketSquare

echo.
echo  ============================================================
echo   TRUSTSQUARE  ^|  Session Starting...
echo  %DATE%   %TIME%
echo  ============================================================
echo.

:: -- Step 0: Git pull — sync all projects from GitHub ----------
echo  [0/3] Pulling latest from GitHub...
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
echo   All projects synced.
echo.

:: -- Step 1: Open live sites in browser ------------------------
echo  [1/3] Opening browser tabs...
start "" "https://trustsquare.co?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/admin.html?v=%random%"
timeout /t 1 /nobreak >nul
start "" "https://trustsquare.co/dashboard.html?v=%random%"
timeout /t 1 /nobreak >nul
echo   Done.
echo.

:: -- Step 2: Open Projects folder in Explorer -----------------
echo  [2/3] Opening MarketSquare project folder...
explorer "%MS%"
timeout /t 1 /nobreak >nul
echo.

echo  ============================================================
echo   SESSION READY
echo  ============================================================
echo.
echo  Browser tabs:
echo    trustsquare.co                buyer app
echo    trustsquare.co/admin.html     admin tool
echo    trustsquare.co/dashboard.html session dashboard
echo.
echo  Deploy commands (run from PowerShell in C:\Users\David\Projects\MarketSquare):
echo    scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo    scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
echo    scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
echo    ssh root@178.104.73.239 "systemctl restart marketsquare"
echo.
timeout /t 5 /nobreak >nul
exit
