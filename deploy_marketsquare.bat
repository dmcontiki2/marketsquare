@echo off
title MarketSquare · Deploying to Server...
color 0A

:: ════════════════════════════════════════════════════════════
::  deploy_marketsquare.bat
::  MarketSquare · Deploy Script v3
::  Copies latest HTML + BEA files to Hetzner server
::  and VERIFIES each step completed successfully.
::  Place this file in: C:\Users\David\Projects\MarketSquare
::  Run whenever you want to push changes live.
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
echo   %DATE% %TIME%
echo  ============================================================
echo.

:: ── Pre-flight: check all three files exist ───────────────
echo  Checking local files...
if not exist "%PROJECT%\marketsquare.html" (
    echo  ERROR: marketsquare.html not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\marketsquare_admin.html" (
    echo  ERROR: marketsquare_admin.html not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\bea_main.py" (
    echo  ERROR: bea_main.py not found in %PROJECT%
    pause
    exit /b 1
)
echo  All three files found locally.
echo.

:: ── Step 1: Deploy buyer app ──────────────────────────────
echo  [1/5] Deploying buyer app (marketsquare.html -^> index.html)...
scp "%PROJECT%\marketsquare.html" %SERVER%:%REMOTE%/index.html
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for buyer app. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 2: Deploy admin tool ─────────────────────────────
echo  [2/5] Deploying admin tool (marketsquare_admin.html -^> admin.html)...
scp "%PROJECT%\marketsquare_admin.html" %SERVER%:%REMOTE%/admin.html
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for admin tool. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3: Deploy BEA + restart ──────────────────────────
echo  [3/5] Deploying BEA backend (bea_main.py -^> main.py)...
scp "%PROJECT%\bea_main.py" %SERVER%:%REMOTE%/main.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for BEA. Check SSH connection.
    pause
    exit /b 1
)
echo  SCP done. Restarting BEA service...
ssh %SERVER% "systemctl restart marketsquare"
if %errorlevel% neq 0 (
    echo  ERROR: BEA service restart failed. Check server with:
    echo    ssh root@178.104.73.239 "journalctl -u marketsquare -n 30"
    pause
    exit /b 1
)
echo  BEA restarted. Waiting for startup...
timeout /t 5 /nobreak >nul
echo  Done.
echo.

:: ── Step 4: Reload nginx ──────────────────────────────────
echo  [4/5] Reloading nginx...
ssh %SERVER% "nginx -s reload"
if %errorlevel% neq 0 (
    echo  WARNING: nginx reload may have failed. Check server manually.
) else (
    echo  Done.
)
echo.

:: ── Step 5: Verify deploy on server ──────────────────────
echo  [5/5] Verifying deploy on server...
echo.

ssh %SERVER% "grep -q 'listings/mine' %REMOTE%/main.py && echo   [OK] BEA: new routes confirmed in main.py || echo   [FAIL] BEA: old main.py still on server - SCP may have failed"

ssh %SERVER% "grep -q 'tuppence/balance' %REMOTE%/main.py && echo   [OK] BEA: tuppence/balance endpoint confirmed || echo   [FAIL] BEA: missing endpoint - redeploy needed"

ssh %SERVER% "systemctl is-active marketsquare >nul 2>&1 && echo   [OK] BEA service is active || echo   [FAIL] BEA service is NOT active - check journalctl"

ssh %SERVER% "grep -q 'dev-tools\|devtools' %REMOTE%/admin.html && echo   [OK] Admin: new admin.html confirmed on server || echo   [FAIL] Admin: old admin.html still on server"

ssh %SERVER% "grep -q 'screen-edit-listing' %REMOTE%/index.html && echo   [OK] Buyer app: new index.html confirmed on server || echo   [FAIL] Buyer app: old index.html still on server"

echo.
echo  ============================================================
echo   DEPLOY COMPLETE
echo  ============================================================
echo.
echo  trustsquare.co        ^|  buyer app updated
echo  trustsquare.co/admin  ^|  admin tool updated
echo  BEA backend           ^|  restarted and verified
echo.
echo  If any [FAIL] lines appear above, that file did not deploy.
echo  Re-run this script or manually SCP the failing file.
echo.
echo  Opening sites in browser to verify (cache-busted)...
timeout /t 2 /nobreak >nul
start "" "https://trustsquare.co?v=%random%"
start "" "https://trustsquare.co/admin.html?v=%random%"
echo.
timeout /t 6 /nobreak >nul
exit
