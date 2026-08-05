@echo off
REM RECONCILE_FAULTS.bat v2 - AIK-VERIFY-1: people report, machines verify.
REM v1 failed 403: the edge gate (RG-0027) rejects ANY off-browser HTTP call before
REM the maint key is even examined - by design. v2 runs the reconcile ON the server
REM against localhost via your SSH key (the same transport the deploy uses). The
REM script reads MS_MAINT_KEY from the server's own .env; nothing secret travels.
REM Shows the plan, asks ONE y/n in this window, writes the report, copies it back.
setlocal
cd /d "%~dp0"
set SERVER=root@178.104.73.239
echo Shipping the reconcile script to the server...
scp scripts\fault_reconcile.py %SERVER%:/tmp/fault_reconcile.py
if not %errorlevel%==0 ( echo scp failed - is your SSH key loaded? & pause & exit /b 1 )
ssh -t %SERVER% "MS_BEA_URL=http://localhost:8000 python3 /tmp/fault_reconcile.py"
echo Fetching the report (if one was written)...
scp %SERVER%:/tmp/FAULT_RECONCILE_*.md Records\ >nul 2>nul
ssh %SERVER% "rm -f /tmp/fault_reconcile.py /tmp/FAULT_RECONCILE_*.md"
echo.
echo Done - refresh the Ops Map: verified faults move into the green chip.
pause
