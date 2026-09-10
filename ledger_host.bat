@echo off
setlocal
:: ledger_host.bat - SANDBOX-REPAIR-1 (9 Sep 2026). Runs the regression ledger ON DAVID'S PC
:: (his own Python, no 180 s cap) when the Cowork sandbox cannot. The host queue keeps only
:: the last 4000 chars of output, which is the tail of a 336-entry board - proven 21:48:
:: "3 previously-fixed issues HAVE COME BACK" with the three names cut off. So the FULL board
:: goes to host_queue\done\ledger_host_<stamp>.txt (git-ignored like every .result) and the
:: queue tail carries the summary: header, every REGRESSION / READY TO LOCK / UNVERIFIED row
:: WITH ITS WHOLE DETAIL (ledger_rows.ps1 - findstr matched line by line and dropped the
:: second line of a multi-line fail, which on 10 Sep hid the one red that mattered), and the
:: RESULT line. Read-only: probes the live site and the working tree, writes nothing else.
:: STAMP-LOCALE-1 (10 Sep): %DATE% here is MM/DD/YYYY, so the stamp is built with PowerShell
:: rather than by slicing it - the sliced form produced file names dated 20261009 on 10 Sep.
set STAMP=
for /f %%S in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set STAMP=%%S
set OUT=%~dp0host_queue\done\ledger_host_%STAMP%.txt
cd /d "%~dp0"
echo === ledger_host  %DATE% %TIME%   full board: %OUT%
python scripts\regression_ledger.py > "%OUT%" 2>&1
set RC=%ERRORLEVEL%
echo.
findstr /L /C:"# Regression ledger" "%OUT%"
findstr /R /C:"^[0-9][0-9]* entries" "%OUT%"
echo.
echo --- rows that need a human eye (REGRESSION / READY TO LOCK / UNVERIFIED), full detail ---
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0ledger_rows.ps1" -Board "%OUT%"
echo.
findstr /L /C:"RESULT:" "%OUT%"
echo === ledger_host done at %TIME%  rc=%RC%  (0 = all holding, 1 = regression, 2 = unverified, 3 = unstable run)
exit /b %RC%
