@echo off
setlocal
:: rulings_host.bat - SANDBOX-REPAIR-1 (9 Sep 2026). Runs scripts\rulings_check.py ON DAVID'S PC
:: when the Cowork sandbox cannot. Full output -> host_queue\done\rulings_host_<stamp>.txt
:: (git-ignored); the queue tail carries the whole report when it fits, else its end.
:: Read-only: reads RULINGS.md and the canon files it points at, writes nothing else.
set STAMP=%DATE:~-4%%DATE:~-7,2%%DATE:~-10,2%-%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set STAMP=%STAMP: =0%
set OUT=%~dp0host_queue\done\rulings_host_%STAMP%.txt
cd /d "%~dp0"
echo === rulings_host  %DATE% %TIME%   full report: %OUT%
python scripts\rulings_check.py > "%OUT%" 2>&1
set RC=%ERRORLEVEL%
type "%OUT%"
echo === rulings_host done at %TIME%  rc=%RC%
exit /b %RC%
