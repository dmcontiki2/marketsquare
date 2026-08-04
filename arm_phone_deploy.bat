@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "MSG=%~1"
if "!MSG!"=="" set "MSG=Armed for phone deploy %DATE% %TIME%"

echo.
echo   ARM PHONE DEPLOY
echo   ---------------------------------------------
echo   Runs every gate NOW, commits, and pushes main only.
echo   NOTHING goes live until you tap Merge on your phone.
echo.

:: [1/5] the usual lock self-heal (GIT-LOCK-1)
if exist "%~dp0git_unlock.bat" call "%~dp0git_unlock.bat"

:: [2/5] the same housekeeping the deploy bat does
where python >nul 2>&1 && (
  python "%~dp0scripts\autobump.py"
  python "%~dp0scripts\changelog_compile.py"
  if exist "%~dp0scripts\status_compile.py" python "%~dp0scripts\status_compile.py"
)

:: [3/5] GATES — STRICT. This is the whole point: you will not be at a keyboard
::       when this ships, so a red gate must stop it here, not warn and continue.
set "PREDEPLOY_MODE=strict"
echo   [gates] pre-deploy scan (strict)...
python "%~dp0predeploy_check.py"
if errorlevel 1 goto :blocked
for %%T in (test_tester_intake.py test_maintenance_agent.py test_trust_base40.py test_pg_readiness.py) do (
  if exist "%~dp0%%T" (
    echo   [gates] %%T
    python "%~dp0%%T" >nul 2>&1
    if errorlevel 1 (
      echo   !! %%T FAILED
      goto :blocked
    )
  )
)
echo   [gates] all green.

:: [4/5] commit + push MAIN ONLY. main is a mirror; it deploys nothing.
git add -A
git commit -m "!MSG!"
git push origin HEAD:main
if errorlevel 1 goto :pushfail

:: [5/5] tell him where to tap
echo.
echo   ARMED - and nothing is live yet.
echo.
echo   From your phone, open this and tap Merge pull request:
echo     https://github.com/dmcontiki2/marketsquare/compare/deploy...main?expand=1
echo.
echo   The server picks it up within ~2 minutes, runs its own health check,
echo   and rolls itself back if the site does not come up. Testers can verify
echo   about 5 minutes after you tap.
echo.
goto :eof

:blocked
echo.
echo   BLOCKED. Nothing was committed, nothing was pushed.
echo   A gate failed - fix it before arming a deploy you will not be watching.
echo.
exit /b 1

:pushfail
echo.
echo   Commit succeeded but the push to main FAILED. Nothing is armed.
echo   Check your network / GitHub auth and re-run.
echo.
exit /b 1
