@echo off
title MarketSquare · Deploying to Server...
color 0A

:: ════════════════════════════════════════════════════════════
::  deploy_marketsquare.bat
::  MarketSquare · Deploy Script
::  Copies latest HTML + BEA files to Hetzner server
::  Place this file in: C:\Users\David\Projects\MarketSquare
::  Run whenever you want to push changes live
::
::  Always save your working files as:
::    marketsquare.html        (buyer app)
::    marketsquare_admin.html  (admin tool)
::    bea_main.py              (BEA backend)
::  Version numbers live inside the file — not in the filename.
:: ════════════════════════════════════════════════════════════

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare

echo.
echo  ============================================================
echo   MARKETSQUARE  ^|  Deploying to trustsquare.co...
echo  ============================================================
echo.

:: ── Check files exist before attempting deploy ───────────
if not exist "%PROJECT%\marketsquare.html" (
    echo  ERROR: marketsquare.html not found in project folder.
    echo  Make sure you saved the file as marketsquare.html
    pause
    exit /b 1
)
if not exist "%PROJECT%\marketsquare_admin.html" (
    echo  ERROR: marketsquare_admin.html not found in project folder.
    echo  Make sure you saved the file as marketsquare_admin.html
    pause
    exit /b 1
)

:: ── Step 1: Deploy buyer app ─────────────────────────────
echo  [1/4] Deploying buyer app (marketsquare.html -> index.html)...
scp "%PROJECT%\marketsquare.html" %SERVER%:%REMOTE%/index.html
if %errorlevel% neq 0 (
    echo  ERROR: Failed to deploy buyer app. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 2: Deploy admin tool ────────────────────────────
echo  [2/4] Deploying admin tool (marketsquare_admin.html -> admin.html)...
scp "%PROJECT%\marketsquare_admin.html" %SERVER%:%REMOTE%/admin.html
if %errorlevel% neq 0 (
    echo  ERROR: Failed to deploy admin tool. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3: Deploy BEA backend ───────────────────────────
if exist "%PROJECT%\bea_main.py" (
    echo  [3/4] Deploying BEA backend (bea_main.py -> main.py)...
    scp "%PROJECT%\bea_main.py" %SERVER%:%REMOTE%/main.py
    if %errorlevel% neq 0 (
        echo  WARNING: Failed to deploy BEA. Check SSH connection.
    ) else (
        echo  Done. Restarting BEA service...
        ssh %SERVER% "systemctl restart marketsquare"
        if %errorlevel% neq 0 (
            echo  WARNING: BEA restart may have failed. Check server.
        ) else (
            echo  BEA restarted.
        )
    )
) else (
    echo  [3/4] Skipping BEA deploy (bea_main.py not found).
)
echo.

:: ── Step 4: Reload nginx ─────────────────────────────────
echo  [4/4] Reloading nginx on server...
ssh %SERVER% "nginx -s reload"
if %errorlevel% neq 0 (
    echo  WARNING: nginx reload may have failed. Check server manually.
) else (
    echo  Done.
)
echo.

echo  ============================================================
echo   DEPLOY COMPLETE
echo  ============================================================
echo.
echo  trustsquare.co        ^|  buyer app updated
echo  trustsquare.co/admin  ^|  admin tool updated
echo  BEA backend           ^|  restarted
echo.
echo  Opening sites in browser to verify (cache-busted)...
timeout /t 2 /nobreak >nul
start "" "https://trustsquare.co?v=%random%"
start "" "https://trustsquare.co/admin.html?v=%random%"
echo.
timeout /t 6 /nobreak >nul
exit
