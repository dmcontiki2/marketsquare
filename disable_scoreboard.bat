@echo off
title TrustSquare - Disable the AI scoreboard agent
color 0E
echo.
echo  Turning OFF the nightly scoreboard probes (history is kept)...
ssh root@178.104.73.239 "cd /var/www/marketsquare && sqlite3 marketsquare.db 'UPDATE launch_switches SET scoreboard_enabled=0 WHERE id=1' && echo    FLAG OFF"
echo.
echo  Done. Re-enable any time with enable_scoreboard.bat.
pause
