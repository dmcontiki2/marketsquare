@echo off
:: register_nightly_checkpoint.bat - DOUBLE-CLICK ONCE to set up the nightly checkpoint.
:: Registers a Windows Task Scheduler job that runs nightly_checkpoint.bat every day
:: at 05:30 (after your overnight automation), banking the working tree into git.
:: Runs in your user context - no admin, no stored password needed.
set "TASK=MarketSquare Nightly Checkpoint"
set "SCRIPT=%~dp0nightly_checkpoint.bat"
echo  ============================================================
echo   Setting up: "%TASK%"
echo   Runs : "%SCRIPT%"
echo   When : every day at 05:30
echo  ============================================================
echo.
schtasks /Create /TN "%TASK%" /TR "%SCRIPT%" /SC DAILY /ST 05:30 /F
if %errorlevel% neq 0 (
  echo.
  echo  Could not register. If it says "Access is denied", right-click THIS file and
  echo  choose "Run as administrator", then try again.
  pause
  exit /b 1
)
echo.
echo  Done - nightly checkpoint is scheduled.
echo    check it : schtasks /Query /TN "%TASK%"
echo    run now  : schtasks /Run   /TN "%TASK%"
echo    remove   : schtasks /Delete /TN "%TASK%" /F
echo.
pause
