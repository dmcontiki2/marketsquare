@echo off
:: nightly_tsl.bat — UNATTENDED nightly RELEASE for TrustSquare.
:: Runs daily 05:45 via the "TrustSquare Nightly TSL" scheduled task David
:: registered 24 Jul. UPGRADED 9 Aug 2026 on David's explicit instruction
:: ("we need to fix the human need to run one more time"): the old contract
:: (prepare + flag, DEPLOY NOTHING) is superseded — if the tree is ahead and
:: the gates pass STRICT, this now SHIPS through the ONE deploy engine.
:: The git push key stays on this machine (Codex B3). Nothing half-clean ships
:: unattended: strict mode means any gate finding BLOCKS and flags instead.
cd /d "%~dp0"
set "LOG=%~dp0nightly_tsl_log.txt"
set "FLAG=%~dp0TSL_READY.flag"
set "GATEOUT=%~dp0nightly_tsl_gate.txt"

set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE ( where py >nul 2>&1 && set "PYEXE=py" )
if not defined PYEXE ( echo %date% %time%  SKIP: python not on PATH>>"%LOG%" & exit /b 0 )
if not exist "%~dp0tsl_gate.py" ( echo %date% %time%  SKIP: tsl_gate.py missing>>"%LOG%" & exit /b 0 )
if not exist "%~dp0check_deploy_drift.py" ( echo %date% %time%  SKIP: check_deploy_drift.py missing>>"%LOG%" & exit /b 0 )
if exist "%FLAG%" del /f "%FLAG%"

:: (1) Anything to ship? (read-only content compare; RG-0026 CRLF-aware)
set "DRIFTLINE="
for /f "delims=" %%D in ('%PYEXE% "%~dp0check_deploy_drift.py" 2^>nul') do if not defined DRIFTLINE set "DRIFTLINE=%%D"
echo %DRIFTLINE% | find /i "clean" >nul
if not errorlevel 1 (
    echo %date% %time%  IN SYNC - %DRIFTLINE%>>"%LOG%"
    exit /b 0
)

:: (2) Local ahead -> STRICT gates; a finding blocks the unattended ship.
set "TSL_MODE=strict"
%PYEXE% "%~dp0tsl_gate.py" gate > "%GATEOUT%" 2>&1
set "GATERC=%errorlevel%"

if not "%GATERC%"=="0" (
    set "TSL_MODE="
    > "%FLAG%" echo BLOCKED %date% %time%
    >> "%FLAG%" echo %DRIFTLINE%
    >> "%FLAG%" echo Gate not clean ^(rc=%GATERC%^) - NOT shipped. See nightly_tsl_gate.txt.
    echo %date% %time%  BLOCKED - gate rc=%GATERC% ^| %DRIFTLINE% ^| ship withheld>>"%LOG%"
    exit /b 0
)

:: (3) Gates green -> SHIP, unattended. <nul feeds every pause; strict predeploy too.
set "PREDEPLOY_MODE=strict"
echo %date% %time%  SHIPPING - %DRIFTLINE% ^| gate green, releasing unattended>>"%LOG%"
call "%~dp0deploy_marketsquare.bat" <nul >>"%LOG%" 2>&1
set "RC=%errorlevel%"
set "TSL_MODE="
set "PREDEPLOY_MODE="
if "%RC%"=="0" (
    echo %date% %time%  SHIPPED rc=0 - server now runs migrations + health itself>>"%LOG%"
) else (
    > "%FLAG%" echo FAILED %date% %time% rc=%RC% - see nightly_tsl_log.txt
    echo %date% %time%  SHIP FAILED rc=%RC% - engine auto-rolls-back on bad health>>"%LOG%"
)
exit /b %RC%
