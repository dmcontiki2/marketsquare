@echo off
REM ── EMERGENCY: restore the previous working BEA so the site is live again. ──
REM Uses the server-side backup the deploy makes. Run if the new deploy crashed the BEA.
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
echo Looking for a server-side BEA backup to restore...
ssh %SERVER% "ls -t %REMOTE%/main.py.*bak* 2>/dev/null | head -5"
echo.
echo Restoring the MOST RECENT main.py backup and restarting...
ssh %SERVER% "cp $(ssh %SERVER% 'ls -t %REMOTE%/main.py.*bak* 2>/dev/null | head -1') %REMOTE%/main.py 2>/dev/null; systemctl restart marketsquare; sleep 3; systemctl is-active marketsquare && echo RESTORED-AND-ACTIVE || echo STILL-DOWN-tell-Claude"
