@echo off
:: register_nightly_ship.bat — DOUBLE-CLICK ONCE. Schedules the unattended nightly
:: RELEASE (nightly_ship.bat) daily at 02:00. This REPLACES the human ship step:
:: if the tree is ahead and the gates are green, it goes live while David sleeps.
:: The 05:45 "Nightly TSL" ready-check task can stay — it becomes a second opinion.
:: Laptop must be on (or asleep-with-wake-timers) at 02:00; a missed night simply
:: ships the next night. Runs in your user context — no admin, no stored password.
set "TASK=TrustSquare Nightly Ship"
set "SCRIPT=%~dp0nightly_ship.bat"
echo  ============================================================
echo   Setting up: "%TASK%"
echo   Runs : "%SCRIPT%"
echo   When : every day at 02:00  (ships ONLY if ahead + gates green)
echo  ============================================================
schtasks /Create /TN "%TASK%" /TR "%SCRIPT%" /SC DAILY /ST 02:00 /F
if %errorlevel% neq 0 (
  echo  Could not register — right-click this file, "Run as administrator", retry.
  pause
  exit /b 1
)
echo  Done. Check: schtasks /Query /TN "%TASK%"   Run now: schtasks /Run /TN "%TASK%"
pause
