@echo off
setlocal
:: boards_host.bat - SANDBOX-REPAIR-1 lane (9 Sep 2026). Runs the two dashboard-truth boards
:: ON DAVID'S PC while the Cowork sandbox is dead (KB5124008 / claude-code #92984), because the
:: queue's run_py lane cannot pass the --check flag these scripts need.
::   1. session_counter.py            -- the DESIGNED remedy for RG-0154: re-derives the session
::                                       number from the fragments on disk and self-verifies the
::                                       write. Writes SESSION_COUNTER.json only. RG-0154's own
::                                       mechanism, not a hand-edited number.
::   2. session_counter.py --check    -- proves the write landed.
::   3. dashboard_provenance.py --check -- READ-ONLY auditor (RG-0155): lists every chip painting
::                                       a health colour nothing measures, and every registered
::                                       static surface past its review date. Changes nothing.
:: Full output -> host_queue\done\boards_host_<stamp>.txt; the queue tail carries the verdicts.
:: No money, no sending, no deletion, no server change.
set STAMP=
for /f %%S in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set STAMP=%%S
set OUT=%~dp0host_queue\done\boards_host_%STAMP%.txt
cd /d "%~dp0"
echo === boards_host  %DATE% %TIME%   full output: %OUT%
> "%OUT%" echo === boards_host %DATE% %TIME%
>>"%OUT%" echo.
>>"%OUT%" echo --- 1. session_counter.py  (re-derive + write SESSION_COUNTER.json)
python scripts\session_counter.py >>"%OUT%" 2>&1
>>"%OUT%" echo [rc=%ERRORLEVEL%]
>>"%OUT%" echo.
>>"%OUT%" echo --- 2. session_counter.py --check  (prove it landed)
python scripts\session_counter.py --check >>"%OUT%" 2>&1
set RC1=%ERRORLEVEL%
>>"%OUT%" echo [rc=%RC1%]
>>"%OUT%" echo.
>>"%OUT%" echo --- 3. dashboard_provenance.py --check  (read-only: what is unfed or past review)
python scripts\dashboard_provenance.py --check >>"%OUT%" 2>&1
set RC2=%ERRORLEVEL%
>>"%OUT%" echo [rc=%RC2%]
type "%OUT%"
echo.
echo === boards_host done at %TIME%   session_counter --check rc=%RC1%   dashboard_provenance --check rc=%RC2%   (0 = clean)
exit /b 0
