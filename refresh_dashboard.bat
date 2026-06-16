@echo off
title TrustSquare - Refresh Ops Dashboard (Session 139)
cd /d C:\Users\David\Projects\MarketSquare
echo Pushing the 4 dashboard docs to the server (refreshes /dashboard/summary)...
scp STATUS.md root@178.104.73.239:/var/www/marketsquare/STATUS.md
scp CHANGELOG.md root@178.104.73.239:/var/www/marketsquare/CHANGELOG.md
scp BACKLOG.md root@178.104.73.239:/var/www/marketsquare/BACKLOG.md
scp AUDIT_PROGRESS.md root@178.104.73.239:/var/www/marketsquare/AUDIT_PROGRESS.md
echo.
echo Purging Cloudflare so the dashboard page picks it up...
curl.exe -s -X POST https://trustsquare.co/admin/purge-cache
echo.
echo.
echo Confirming the server now reports Session 139:
ssh root@178.104.73.239 "curl -s http://localhost:8000/dashboard/summary | grep -oE 'currentSession[^,]*'"
echo.
echo If that shows currentSession:139 the dashboard is current. Window closes in 25s.
timeout /t 25 /nobreak >nul
