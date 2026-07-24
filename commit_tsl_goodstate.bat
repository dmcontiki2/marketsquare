@echo off
:: commit_tsl_goodstate.bat - one-shot: bank the verified TSL good-state into git.
:: NATIVE Windows git (the FUSE mount blocks unlink, so the sandbox cannot do this).
:: Commits ONLY the five TSL files - it will not sweep up another session's edits.
cd /d "%~dp0"
echo ============================================================
echo   Committing the TSL good state (native git)
echo ============================================================

where git >nul 2>&1 || ( echo  ERROR: git not on PATH. & pause & exit /b 1 )

:: Sweep stale locks left by failed/concurrent ops (0-byte, safe by definition here).
if exist ".git\index.lock" ( echo  [sweep] removing stale .git\index.lock & del /f /q ".git\index.lock" )
if exist ".git\HEAD.lock"  ( echo  [sweep] removing stale .git\HEAD.lock  & del /f /q ".git\HEAD.lock" )

echo.
echo  Files to bank:
for %%F in (tsl_gate.py deploy_marketsquare.bat nightly_tsl.bat register_nightly_tsl.bat tsl_selftest.bat) do (
    if exist "%%F" ( echo     + %%F ) else ( echo     ! MISSING: %%F )
)

echo.
git add -- tsl_gate.py deploy_marketsquare.bat nightly_tsl.bat register_nightly_tsl.bat tsl_selftest.bat
if errorlevel 1 ( echo  ERROR: git add failed. & pause & exit /b 1 )

git commit -m "TSL good state: guarded deploy (lock in deploy_marketsquare.bat + CM/DB pre-deploy gate), dead-DB fix + FUSE-safe lock, nightly ready-to-ship scripts. Verified against live server 24 Jul 2026." -- tsl_gate.py deploy_marketsquare.bat nightly_tsl.bat register_nightly_tsl.bat tsl_selftest.bat

if errorlevel 1 (
    echo.
    echo  NOTE: git commit reported nothing to commit ^(already banked^) or an error above.
) else (
    echo.
    echo  Committed. New HEAD:
)
git rev-parse --short HEAD
echo.
echo  --- last commit summary ---
git log -1 --stat -- tsl_gate.py deploy_marketsquare.bat nightly_tsl.bat register_nightly_tsl.bat tsl_selftest.bat
echo.
echo  (git is native here - nothing was pushed; this is a local checkpoint you can restore from.)
pause
