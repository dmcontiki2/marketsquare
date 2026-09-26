@echo off
title TrustSquare - Refresh Ops Dashboard
cd /d C:\Users\David\Projects\MarketSquare
echo Pushing the 4 dashboard docs to the server (refreshes /dashboard/summary)...
scp STATUS.md root@178.104.73.239:/var/www/marketsquare/STATUS.md
scp CHANGELOG.md root@178.104.73.239:/var/www/marketsquare/CHANGELOG.md
scp BACKLOG.md root@178.104.73.239:/var/www/marketsquare/BACKLOG.md
scp AUDIT_PROGRESS.md root@178.104.73.239:/var/www/marketsquare/AUDIT_PROGRESS.md
echo.
echo Purging Cloudflare so the dashboard page picks it up...
:: ADMIN-KEY-LOCAL-1 (25 Sep 2026 inspection, qa-10): the purge is admin-only; it runs on the box with the key
:: the RUNNING app holds (read there, passed to curl on stdin - never typed here).
ssh root@178.104.73.239 "P=$(systemctl show -p MainPID --value marketsquare); K=$(tr '\0' '\n' < /proc/$P/environ 2>/dev/null | sed -n 's/^MS_ADMIN_KEY=//p' | head -n 1); echo X-Admin-Key: $K | curl -s -X POST -H @- http://localhost:8000/admin/purge-cache"
echo.
echo.
echo Confirming the server session counter:
:: ADMIN-KEY-LOCAL-1 (qa-04): /dashboard/summary answers a key-less caller with a bare heartbeat (no session number).
ssh root@178.104.73.239 "P=$(systemctl show -p MainPID --value marketsquare); K=$(tr '\0' '\n' < /proc/$P/environ 2>/dev/null | sed -n 's/^MS_ADMIN_KEY=//p' | head -n 1); echo X-Admin-Key: $K | curl -s -H @- http://localhost:8000/dashboard/summary | grep -oE 'currentSession[^,]*'"
echo.
echo If that matches STATUS.md the dashboard is current. Window closes in 25s.
timeout /t 25 /nobreak >nul
