@echo off
REM ── MarketSquare one-click commit ──────────────────────────────
REM Double-click this file to stage, commit, and push everything.
REM Runs on the Windows side (correct OS user) so it never hits the
REM sandbox index.lock collision. Pass a message or get a default one.

cd /d "%~dp0"

set "MSG=%~1"
if "%MSG%"=="" set "MSG=WIP: session commit %DATE% %TIME%"

echo.
call "%~dp0git_unlock.bat"
echo === git add -A ===
git add -A

echo.
echo === git commit ===
git commit -m "%MSG%"

echo.
echo === take in GitHub first (SYNC-ORIGIN-1) ===
set "PYEXE=python"
where python >nul 2>&1 || set "PYEXE=py"
%PYEXE% "%~dp0scripts\sync_origin.py"
if errorlevel 1 (
    echo STOP: GitHub has commits that could not be taken in cleanly - committed locally, NOT pushed, nothing overwritten. See SYNC_CONFLICT.txt.
    pause >nul
    exit /b 1
)
echo === git push ===
git push

echo.
echo Done. Press any key to close.
pause >nul
