@echo off
title TrustSquare - Frontend Deploy (no-PowerShell)
cd /d C:\Users\David\Projects\MarketSquare
echo ============================================================
echo  Frontend deploy - scp + curl only (no PowerShell)
echo ============================================================
echo [0/4] Bumping cache-buster (?v=) on any changed static ...
python "scripts\autobump.py" || py "scripts\autobump.py"
if %errorlevel% neq 0 ( echo  WARNING: autobump could not run ^(python missing?^) - ms.js?v= may be stale. )
:: read the ms.js version autobump just settled, so the verify below is never hardcoded (RG-0013)
python -c "import re;open('_msjsver.tmp','w').write(re.search(r'ms.js\?v=(\d+)',open('marketsquare.html',encoding='utf-8').read()).group(1))" 2>nul || py -c "import re;open('_msjsver.tmp','w').write(re.search(r'ms.js\?v=(\d+)',open('marketsquare.html',encoding='utf-8').read()).group(1))" 2>nul
set "MSJSV=?"
if exist _msjsver.tmp set /p MSJSV=<_msjsver.tmp
if exist _msjsver.tmp del _msjsver.tmp
echo    Shipping ms.js?v=%MSJSV%
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
if %errorlevel% neq 0 ( echo  ERROR: index.html UPLOAD FAILED ^(scp/SSH^). Users will not get v%MSJSV%. & pause ^>nul & exit /b 1 )
echo    index.html uploaded OK.
echo [4/4] Purging Cloudflare edge cache ...
curl.exe -s -X POST https://trustsquare.co/admin/purge-cache
echo.
echo    Checking live now serves v%MSJSV% ...
curl.exe -s "https://trustsquare.co/?nocache=%RANDOM%%RANDOM%" | findstr /C:"ms.js?v=%MSJSV%" >nul && (echo    [OK] LIVE serves ms.js?v=%MSJSV% - hard-refresh and the maps + extensions are live.) || (echo    [FAIL] LIVE not v%MSJSV% yet - tell Claude.)
echo.
echo  Done. Read the [OK]/[FAIL] line, then press a key.
pause >nul
