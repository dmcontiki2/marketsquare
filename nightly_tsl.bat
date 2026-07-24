@echo off
:: nightly_tsl.bat - UNATTENDED nightly "ready-to-ship" prep for TrustSquare.
:: Run by Windows Task Scheduler. DEPLOYS NOTHING (matches check_deploy_drift.py's
:: deliberate shadow rule). It: (1) checks whether local is ahead of live, and if so
:: (2) runs the CM+DB gate, then writes a one-line verdict + a READY / BLOCKED flag
:: that a morning  /TSL  reads to fast-path the actual, intentional upload.
cd /d "%~dp0"
set "LOG=%~dp0nightly_tsl_log.txt"
set "FLAG=%~dp0TSL_READY.flag"
set "GATEOUT=%~dp0nightly_tsl_gate.txt"

set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE (
    where py >nul 2>&1 && set "PYEXE=py"
)
if not defined PYEXE ( echo %date% %time%  SKIP: python not on PATH>>"%LOG%" & exit /b 0 )
if not exist "%~dp0tsl_gate.py" ( echo %date% %time%  SKIP: tsl_gate.py missing>>"%LOG%" & exit /b 0 )
if not exist "%~dp0check_deploy_drift.py" ( echo %date% %time%  SKIP: check_deploy_drift.py missing>>"%LOG%" & exit /b 0 )
if exist "%FLAG%" del /f "%FLAG%"

:: (1) Drift: is local ahead of live? (read-only md5 compare, deploys nothing)
set "DRIFTLINE="
for /f "delims=" %%D in ('%PYEXE% "%~dp0check_deploy_drift.py" 2^>nul') do if not defined DRIFTLINE set "DRIFTLINE=%%D"
echo %DRIFTLINE% | find /i "clean" >nul
if not errorlevel 1 (
    echo %date% %time%  IN SYNC - %DRIFTLINE%>>"%LOG%"
    exit /b 0
)

:: (2) Local is ahead -> run the CM+DB gate in strict mode (exit 0 = clean-green)
set "TSL_MODE=strict"
%PYEXE% "%~dp0tsl_gate.py" gate > "%GATEOUT%" 2>&1
set "GATERC=%errorlevel%"
set "TSL_MODE="

if "%GATERC%"=="0" (
    > "%FLAG%" echo READY %date% %time%
    >> "%FLAG%" echo %DRIFTLINE%
    >> "%FLAG%" echo Gate: CM+DB green. Type /TSL to release the upload.
    echo %date% %time%  READY - %DRIFTLINE% ^| gate green>>"%LOG%"
) else (
    > "%FLAG%" echo BLOCKED %date% %time%
    >> "%FLAG%" echo %DRIFTLINE%
    >> "%FLAG%" echo Gate not clean ^(rc=%GATERC%^). See nightly_tsl_gate.txt before shipping.
    echo %date% %time%  BLOCKED - gate rc=%GATERC% ^| %DRIFTLINE%>>"%LOG%"
)
exit /b 0
