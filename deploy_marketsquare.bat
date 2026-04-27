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
if not exist "%PROJECT%\service-worker.js" (
    echo  ERROR: service-worker.js not found in %PROJECT%
    pause
    exit /b 1
)
echo  All four files found locally.
echo.

:: ── Step 1: Deploy buyer app ──────────────────────────────
echo  [1/6] Deploying buyer app (marketsquare.html -^> index.html)...
scp "%PROJECT%\marketsquare.html" %SERVER%:%REMOTE%/index.html
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for buyer app. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 2: Deploy admin tool ─────────────────────────────
echo  [2/6] Deploying admin tool (marketsquare_admin.html -^> admin.html)...
scp "%PROJECT%\marketsquare_admin.html" %SERVER%:%REMOTE%/admin.html
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for admin tool. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3: Deploy service worker (Wishlist Web Push) ────
echo  [3/6] Deploying service worker (service-worker.js -^> service-worker.js)...
scp "%PROJECT%\service-worker.js" %SERVER%:%REMOTE%/service-worker.js
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for service-worker.js. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 4: Deploy BEA + restart ──────────────────────────
echo  [4/6] Deploying BEA backend (bea_main.py -^> main.py)...
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

:: ── Step 5: Reload nginx ──────────────────────────────────
echo  [5/6] Reloading nginx...
ssh %SERVER% "nginx -s reload"
if %errorlevel% neq 0 (
    echo  WARNING: nginx reload may have failed. Check server manually.
) else (
    echo  Done.
)
echo.

:: ── Step 6: Verify deploy on server ──────────────────────
echo  [6/6] Verifying deploy on server...
echo.

ssh %SERVER% "grep -q 'listings/mine' %REMOTE%/main.py && echo   [OK] BEA: new routes confirmed in main.py || echo   [FAIL] BEA: old main.py still on server - SCP may have failed"

ssh %SERVER% "grep -q 'tuppence/balance' %REMOTE%/main.py && echo   [OK] BEA: tuppence/balance endpoint confirmed || echo   [FAIL] BEA: missing endpoint - redeploy needed"

ssh %SERVER% "grep -q 'wishlist/feed' %REMOTE%/main.py && echo   [OK] BEA: wishlist feed endpoints confirmed || echo   [FAIL] BEA: wishlist endpoints missing - redeploy needed"

ssh %SERVER% "systemctl is-active marketsquare >nul 2>&1 && echo   [OK] BEA service is active || echo   [FAIL] BEA service is NOT active - check journalctl"

ssh %SERVER% "grep -q 'dev-tools\|devtools' %REMOTE%/admin.html && echo   [OK] Admin: new admin.html confirmed on server || echo   [FAIL] Admin: old admin.html still on server"

ssh %SERVER% "grep -q 'view-showcase' %REMOTE%/admin.html && echo   [OK] Admin: showcase tab confirmed || echo   [FAIL] Admin: showcase tab missing - redeploy needed"

ssh %SERVER% "grep -q 'screen-edit-listing' %REMOTE%/index.html && echo   [OK] Buyer app: new index.html confirmed on server || echo   [FAIL] Buyer app: old index.html still on server"

ssh %SERVER% "grep -q 'wlBootToken\|wishlist-feed' %REMOTE%/index.html && echo   [OK] Buyer app: wishlist feed UI confirmed || echo   [FAIL] Buyer app: wishlist UI missing - redeploy needed"

ssh %SERVER% "test -f %REMOTE%/service-worker.js && echo   [OK] Service worker confirmed on server || echo   [FAIL] service-worker.js missing - redeploy needed"

ssh %SERVER% "grep -q 'local-market/listings' %REMOTE%/main.py && echo   [OK] BEA: Local Market endpoints confirmed || echo   [FAIL] BEA: Local Market endpoints missing - redeploy needed"

ssh %SERVER% "grep -q 'trust-score/breakdown' %REMOTE%/main.py && echo   [OK] BEA: Trust Score Hub endpoint confirmed || echo   [FAIL] BEA: Trust Score Hub endpoint missing - redeploy needed"

ssh %SERVER% "grep -q 'screen-local-market' %REMOTE%/index.html && echo   [OK] Buyer app: Local Market page confirmed || echo   [FAIL] Buyer app: Local Market page missing - redeploy needed"

ssh %SERVER% "grep -q 'lm-eula-modal' %REMOTE%/admin.html && echo   [OK] Admin: Local Market form + EULA modal confirmed || echo   [FAIL] Admin: Local Market form missing - redeploy needed"

ssh %SERVER% "grep -q 'tsh-panel' %REMOTE%/admin.html && echo   [OK] Admin: Trust Score Hub UI confirmed || echo   [FAIL] Admin: Trust Score Hub missing - redeploy needed"

ssh %SERVER% "curl -s http://localhost:8000/health | grep -q '1.3.0' && echo   [OK] BEA reports v1.3.0 || echo   [FAIL] BEA version mismatch - check service restart"

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
