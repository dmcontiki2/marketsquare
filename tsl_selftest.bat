@echo off
:: tsl_selftest.bat - run the CM+DB gate ONCE against the live server and show the
:: result. Read-only: it deploys nothing and changes nothing. Use this to prove the
:: read-only msdeploy@ path can reach the databases before relying on /TSL.
cd /d "%~dp0"
set "OUT=%~dp0tsl_gate_selftest.txt"
set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE (
    where py >nul 2>&1 && set "PYEXE=py"
)
if not defined PYEXE ( echo python not found on PATH - install Python or add it to PATH & pause & exit /b 1 )
echo  Running the TrustSquare Load gate (read-only)...
echo.
%PYEXE% "%~dp0tsl_gate.py" gate > "%OUT%" 2>&1
type "%OUT%"
echo.
echo  (saved to %OUT%)
pause
