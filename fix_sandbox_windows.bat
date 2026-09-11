@echo off
REM ===========================================================================
REM  fix_sandbox_windows.bat  -  the ONE thing to run when the Claude sandbox
REM  cannot see the hard drive ("Plan9 share not mounted").
REM
REM  It does BOTH halves in one elevated run:
REM    1. Removes Windows update KB5124008, which causes the fault.
REM    2. PAUSES Windows Update for 5 weeks, so Windows stops putting it back.
REM
REM  Half 2 is the new part. On 10 Sep 2026 only half 1 was done, and the
REM  update reinstalled itself overnight - the fault was back by the morning
REM  of 11 Sep. Removing without pausing buys about one day.
REM
REM  David's permission, 10 Sep 2026: "please proceed and remove that update
REM  until Anthropic has fixed the issue."
REM  Upstream report: github.com/anthropics/claude-code/issues/92984
REM
REM  Windows will ask you to approve this once. Say Yes.
REM ===========================================================================
setlocal

net session >nul 2>&1
if errorlevel 1 (
  echo.
  echo Asking Windows for administrator rights. Please say Yes.
  powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)

echo.
echo ================================================================
echo  STEP 1 of 2  -  removing update KB5124008
echo ================================================================
echo.
wusa.exe /uninstall /kb:5124008 /quiet /norestart
echo   (if it says the update is not installed, that is fine - go on)
echo.

echo ================================================================
echo  STEP 2 of 2  -  pausing Windows Update for 5 weeks
echo ================================================================
echo.
for /f %%T in ('powershell -NoProfile -Command "(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')"') do set NOWZ=%%T
for /f %%T in ('powershell -NoProfile -Command "(Get-Date).ToUniversalTime().AddDays(35).ToString('yyyy-MM-ddTHH:mm:ssZ')"') do set ENDZ=%%T

set K=HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings
reg add "%K%" /v PauseUpdatesStartTime        /t REG_SZ /d "%NOWZ%" /f >nul
reg add "%K%" /v PauseUpdatesExpiryTime       /t REG_SZ /d "%ENDZ%" /f >nul
reg add "%K%" /v PauseQualityUpdatesStartTime /t REG_SZ /d "%NOWZ%" /f >nul
reg add "%K%" /v PauseQualityUpdatesEndTime   /t REG_SZ /d "%ENDZ%" /f >nul
reg add "%K%" /v PauseFeatureUpdatesStartTime /t REG_SZ /d "%NOWZ%" /f >nul
reg add "%K%" /v PauseFeatureUpdatesEndTime   /t REG_SZ /d "%ENDZ%" /f >nul
echo   Updates paused until %ENDZ%
echo.
echo   Reading the setting back to prove it took:
reg query "%K%" /v PauseUpdatesExpiryTime
echo.

echo ================================================================
echo  DONE. Now restart the PC.
echo ================================================================
echo.
echo  After the restart, two things to confirm:
echo    - Settings ^> Windows Update should say updates are paused.
echo    - Claude's sandbox should be able to read your drive again.
echo.
echo  If Settings does NOT say paused, set it by hand there:
echo  Settings ^> Windows Update ^> Pause updates ^> 5 weeks.
echo.
pause
