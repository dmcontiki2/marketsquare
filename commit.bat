@echo off
REM ── MarketSquare one-click commit ──────────────────────────────
REM Double-click this file to stage, commit, and push everything.
REM Runs on the Windows side (correct OS user) so it never hits the
REM sandbox index.lock collision. Pass a message or get a default one.

cd /d "%~dp0"

set "MSG=%~1"
if "%MSG%"=="" set "MSG=WIP: session commit %DATE% %TIME%"

echo.
echo === git add -A ===
git add -A

echo.
echo === git commit ===
git commit -m "%MSG%"

echo.
echo === git push ===
git push

echo.
echo Done. Press any key to close.
pause >nul
