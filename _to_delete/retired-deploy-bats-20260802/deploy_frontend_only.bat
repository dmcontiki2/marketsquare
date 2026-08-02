@echo off
setlocal enableextensions
title TrustSquare - Frontend Cache-Bust Deploy
cd /d C:\Users\David\Projects\MarketSquare
echo ============================================================
echo  Frontend deploy  (bump FIRST, assets, HTML, purge, then VERIFY)
echo ============================================================
echo [0/5] Bumping cache-buster version in marketsquare.html...
powershell -NoProfile -Command "$f='C:\Users\David\Projects\MarketSquare\marketsquare.html'; $c=Get-Content -Raw -LiteralPath $f; $c=[regex]::Replace($c,'ms\.js\?v=(\d+)',{'ms.js?v='+([int]$args[0].Groups[1].Value+1)}); $c=[regex]::Replace($c,'ms\.css\?v=(\d+)',{'ms.css?v='+([int]$args[0].Groups[1].Value+1)}); Set-Content -NoNewline -LiteralPath $f -Value $c; Write-Host ('  bumped -> ms.js?v=' + [regex]::Match($c,'ms\.js\?v=(\d+)').Groups[1].Value)"
if %errorlevel% neq 0 (
    echo  PowerShell is blocked on this machine - switching to the no-PowerShell deploy...
    call deploy_frontend_nops.bat
    exit /b %errorlevel%
)
echo [1/5] Uploading ms.js  -^> /static/ms.js ...
scp ms.js root@178.104.73.239:/var/www/marketsquare/static/ms.js
if %errorlevel% neq 0 ( echo  ERROR: ms.js UPLOAD FAILED ^(scp^). Check SSH/network. NOTHING is live. & echo  Press a key to close. & pause >nul & exit /b 1 )
echo    ms.js uploaded OK.
echo [2/5] Uploading ms.css -^> /static/ms.css ...
scp ms.css root@178.104.73.239:/var/www/marketsquare/static/ms.css
if %errorlevel% neq 0 ( echo  WARNING: ms.css upload failed - continuing ^(css is not the map fix^). )
echo [3/5] Uploading marketsquare.html -^> index.html ...
scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
if %errorlevel% neq 0 ( echo  ERROR: index.html UPLOAD FAILED ^(scp^). Users will NOT get the new version. & echo  Press a key to close. & pause >nul & exit /b 1 )
echo    index.html uploaded OK.
echo [4/5] Purging Cloudflare edge cache ...
curl.exe -s -X POST https://trustsquare.co/admin/purge-cache
echo.
echo [5/5] Verifying the NEW version actually reached users...
for /f "usebackq delims=" %%V in (`powershell -NoProfile -Command "[regex]::Match((Get-Content -Raw -LiteralPath 'C:\Users\David\Projects\MarketSquare\marketsquare.html'),'ms\.js\?v=(\d+)').Groups[1].Value"`) do set LOCALVER=%%V
curl.exe -s "https://trustsquare.co/?nocache=%RANDOM%%RANDOM%" | findstr /C:"ms.js?v=%LOCALVER%" >nul && (echo    [OK] LIVE now serves ms.js?v=%LOCALVER% - hard-refresh your browser and the maps will be correct.) || (echo    [FAIL] LIVE still does NOT serve ms.js?v=%LOCALVER% - the upload did not take; tell Claude.)
echo.
echo ============================================================
echo  Deploy finished. Read the [5/5] line above, then press a key.
echo ============================================================
pause >nul
