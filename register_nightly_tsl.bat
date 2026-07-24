@echo off
:: register_nightly_tsl.bat - DOUBLE-CLICK ONCE to schedule the nightly TSL ready-check.
:: Registers a Windows Task Scheduler job that runs nightly_tsl.bat every day at 05:45
:: (just after your 05:30 nightly checkpoint). It DEPLOYS NOTHING - it prepares a clean
:: upload and leaves a READY / BLOCKED flag for a one-word morning  /TSL.
:: Runs in your user context - no admin, no stored password needed.
set "TASK=TrustSquare Nightly TSL"
set "SCRIPT=%~dp0nightly_tsl.bat"
echo  ============================================================
echo   Setting up: "%TASK%"
echo   Runs : "%SCRIPT%"
echo   When : every day at 05:45  (deploys nothing; prepares + gates)
echo  ============================================================
echo.
schtasks /Create /TN "%TASK%" /TR "%SCRIPT%" /SC DAILY /ST 05:45 /F
if %errorlevel% neq 0 (
  echo.
  echo  Could not register. If it says "Access is denied", right-click THIS file and
  echo  choose "Run as administrator", then try again.
  pause
  exit /b 1
)
echo.
echo  Done - nightly TSL ready-check is scheduled for 05:45 daily.
echo    check it : schtasks /Query /TN "%TASK%"
echo    run now  : schtasks /Run   /TN "%TASK%"
echo    change   : re-run this file after editing /ST, or use Task Scheduler
echo    remove   : schtasks /Delete /TN "%TASK%" /F
echo.
pause
