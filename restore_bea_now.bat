@echo off
REM ── EMERGENCY RESTORE: push a known-good BEA to the server so the site is live again. ──
REM The current deployed main.py is crashing. This restores the pre-change local backup.
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set GOOD=bea_main.py.bak-20260627-091640
echo Backing up the CRASHING main.py on the server first (so Claude can still diagnose it)...
ssh %SERVER% "cp %REMOTE%/main.py %REMOTE%/main.py.CRASHED 2>/dev/null && echo saved main.py.CRASHED"
echo.
echo Pushing known-good BEA (%GOOD%) to the server as main.py...
scp "%~dp0%GOOD%" %SERVER%:%REMOTE%/main.py
if errorlevel 1 ( echo  SCP FAILED - check SSH. & exit /b 1 )
echo.
echo Restarting the BEA...
ssh %SERVER% "systemctl restart marketsquare; sleep 4; systemctl is-active marketsquare && echo BEA-ACTIVE || echo STILL-DOWN"
echo.
echo Verifying /health...
ssh %SERVER% "for i in 1 2 3 4 5; do curl -s http://localhost:8000/health | grep -qE 'status.*ok' && { echo HEALTH-OK; break; }; sleep 2; done"
echo.
echo If it says BEA-ACTIVE + HEALTH-OK, the site is live again on the pre-change BEA.
echo The crashing version is saved as main.py.CRASHED for Claude to diagnose.
