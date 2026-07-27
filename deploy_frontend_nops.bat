@echo off
title TrustSquare - Frontend Deploy (no-PowerShell)
cd /d C:\Users\David\Projects\MarketSquare
echo ============================================================
echo  Frontend deploy - scp + curl only (no PowerShell)  v395
echo ============================================================
echo [1/4] Uploading ms.js  -^> /static/ms.js ...
scp ms.js root@178.104.73.239:/var/www/marketsquare/static/ms.js
if %errorlevel% neq 0 ( echo  ERROR: ms.js UPLOAD FAILED ^(scp/SSH^). Nothing is live. & pause ^>nul & exit /b 1 )
echo    ms.js uploaded OK.
echo [1b] Uploading tour maps -^> /static/ ...
scp adventures_c2c_map.html adventures_na_map.html root@178.104.73.239:/var/www/marketsquare/static/
if %errorlevel% neq 0 ( echo  WARNING: map upload failed - ms.js still ships. )
echo [2/4] Uploading ms.css -^> /static/ms.css ...
scp ms.css root@178.104.73.239:/var/www/marketsquare/static/ms.css
if %errorlevel% neq 0 ( echo  WARNING: ms.css upload failed - continuing. )
echo [3/4] Uploading marketsquare.html -^> index.html ...
scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
if %errorlevel% neq 0 ( echo  ERROR: index.html UPLOAD FAILED ^(scp/SSH^). Users will not get v395. & pause ^>nul & exit /b 1 )
echo    index.html uploaded OK.
echo [4/4] Purging Cloudflare edge cache ...
curl.exe -s -X POST https://trustsquare.co/admin/purge-cache
echo.
echo    Checking live now serves v395 ...
curl.exe -s "https://trustsquare.co/?nocache=%RANDOM%%RANDOM%" | findstr /C:"ms.js?v=395" >nul && (echo    [OK] LIVE serves ms.js?v=395 - hard-refresh and the maps + extensions are live.) || (echo    [FAIL] LIVE not v395 yet - tell Claude.)
echo.
echo  Done. Read the [OK]/[FAIL] line, then press a key.
pause >nul
