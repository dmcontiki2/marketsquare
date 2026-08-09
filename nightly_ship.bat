@echo off
:: nightly_ship.bat — UNATTENDED nightly RELEASE for TrustSquare.
:: (David, 9 Aug 2026: "we need to fix the human need to run one more time.")
:: Task Scheduler runs this at 02:00 in David's user context — the git push key
:: never leaves his machine (Codex B3). This wrapper decides only WHETHER to ship;
:: HOW is still the ONE deploy engine (deploy_marketsquare.bat -> deploy ref ->
:: server_deploy.sh -> gates, health-check, auto-rollback, migrations).
:: Nothing half-clean ships at 2am: gates run STRICT — any finding blocks.
cd /d "%~dp0"
set "LOG=%~dp0nightly_ship_log.txt"
echo ============================================================>>"%LOG%"
echo %date% %time%  NIGHTLY SHIP wake>>"%LOG%"

set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE ( where py >nul 2>&1 && set "PYEXE=py" )
if not defined PYEXE ( echo %date% %time%  SKIP: python not on PATH>>"%LOG%" & exit /b 0 )

:: Anything to ship? (read-only content compare — RG-0026 aware)
set "DRIFTLINE="
for /f "delims=" %%D in ('%PYEXE% "%~dp0check_deploy_drift.py" 2^>nul') do if not defined DRIFTLINE set "DRIFTLINE=%%D"
echo %date% %time%  drift: %DRIFTLINE%>>"%LOG%"
echo %DRIFTLINE% | find /i "clean" >nul
if not errorlevel 1 (
    echo %date% %time%  IN SYNC — nothing to ship>>"%LOG%"
    exit /b 0
)

:: Local is ahead -> release, unattended, STRICT. <nul feeds every pause so the
:: engine never waits for a key at 2am.
set "TSL_MODE=strict"
set "PREDEPLOY_MODE=strict"
call "%~dp0deploy_marketsquare.bat" <nul >>"%LOG%" 2>&1
set "RC=%errorlevel%"
set "TSL_MODE="
set "PREDEPLOY_MODE="
if "%RC%"=="0" (
    echo %date% %time%  SHIPPED rc=0 — server runs migrations + smoke itself>>"%LOG%"
) else (
    echo %date% %time%  BLOCKED/FAILED rc=%RC% — tree untouched live, see log above>>"%LOG%"
)
exit /b %RC%
