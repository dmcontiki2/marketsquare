@echo off
setlocal
:: ledger_host.bat - SANDBOX-REPAIR-1 (9 Sep 2026). Runs the regression ledger ON DAVID'S PC
:: (his own Python, no 180 s cap) when the Cowork sandbox cannot. The host queue keeps only
:: the last 4000 chars of output, which is the tail of a 335-entry board - proven 21:48:
:: "3 previously-fixed issues HAVE COME BACK" with the three names cut off. So the FULL board
:: goes to host_queue\done\ledger_host_<stamp>.txt (git-ignored like every .result) and the
:: queue tail carries the summary: header, every REGRESSION / READY TO LOCK / UNVERIFIED row,
:: and the RESULT line. Read-only: probes the live site and the working tree, writes nothing else.
set STAMP=%DATE:~-4%%DATE:~-7,2%%DATE:~-10,2%-%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set STAMP=%STAMP: =0%
set OUT=%~dp0host_queue\done\ledger_host_%STAMP%.txt
cd /d "%~dp0"
echo === ledger_host  %DATE% %TIME%   full board: %OUT%
python scripts\regression_ledger.py > "%OUT%" 2>&1
set RC=%ERRORLEVEL%
echo.
findstr /L /C:"# Regression ledger" "%OUT%"
findstr /R /C:"^[0-9][0-9]* entries" "%OUT%"
echo.
echo --- rows that need a human eye (REGRESSION / READY TO LOCK / UNVERIFIED) ---
findstr /L /C:"[ !!!! ]" /C:"[ LOCK ]" /C:"[ ???? ]" /C:"           REGRESSION:" "%OUT%"
echo.
findstr /L /C:"RESULT:" "%OUT%"
echo === ledger_host done at %TIME%  rc=%RC%  (0 = all holding, 1 = regression, 2 = unverified, 3 = unstable run)
exit /b %RC%
