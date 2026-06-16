@echo off
title TrustSquare - Frontend Cache-Bust Deploy
cd /d C:\Users\David\Projects\MarketSquare
echo ============================================================
echo  Deploying frontend  (assets FIRST, then HTML, then purge)
echo ============================================================
echo [1/3] ms.js  -^> /static/ms.js
scp ms.js root@178.104.73.239:/var/www/marketsquare/static/ms.js
echo [2/3] ms.css -^> /static/ms.css
scp ms.css root@178.104.73.239:/var/www/marketsquare/static/ms.css
echo [3/3] marketsquare.html -^> index.html  (references ms.js?v=174)
scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo.
echo Purging Cloudflare edge cache ...
curl.exe -s -X POST https://trustsquare.co/admin/purge-cache
echo.
echo.
echo DONE - badges should now load. This window closes in 25 seconds.
timeout /t 25 /nobreak >nul
