@echo off
REM ===========================================================================
REM  remove_kb_properly.bat  -  find out WHY KB5124008 will not come off, and
REM  remove it the supported way.
REM
REM  Background: two restarts, "Yes" every time, and the update is still there
REM  (install date still 2026-09-10, build still 26200.9445). So the removal is
REM  failing silently. The earlier script used  wusa /quiet , which hides the
REM  error. Windows 11 cumulative updates often CANNOT be removed by wusa at
REM  all - DISM is the supported route.
REM
REM  This script: shows the real error, then tries DISM, then tells you plainly
REM  whether a restart is worth doing. Nothing is hidden.
REM ===========================================================================
setlocal enabledelayedexpansion

net session >nul 2>&1
if errorlevel 1 (
  echo. & echo Asking Windows for administrator rights. Please say Yes.
  powershell -NoProfile -Command "Start-Process '%~f0' -Verb RunAs"
  exit /b
)

set LOG=%~dp0host_queue\done\kb_removal_report.txt
echo KB5124008 removal report  %DATE% %TIME% > "%LOG%"

echo.
echo ============================================================
echo  1 of 4  -  is it actually installed right now?
echo ============================================================
wmic qfe where "HotFixID='KB5124008'" get HotFixID,InstalledOn 2>nul | findstr /i KB5124008
if errorlevel 1 (
  echo   NOT in the installed list. It may already be removed and waiting
  echo   for a restart. Skip to step 4.
) else (
  echo   Still installed.
)
wmic qfe where "HotFixID='KB5124008'" get HotFixID,InstalledOn >> "%LOG%" 2>&1

echo.
echo ============================================================
echo  2 of 4  -  what does wusa actually say? (error NOT hidden)
echo ============================================================
echo   Running wusa without /quiet. A Windows dialog may appear -
echo   READ IT, it carries the real reason. Close it to continue.
echo.
start /wait wusa.exe /uninstall /kb:5124008 /norestart
echo   wusa exit code = %errorlevel%
echo   wusa exit code = %errorlevel% >> "%LOG%"
echo.
echo   0        = accepted (restart will finish it)
echo   2359303  = this update is not permitted to be uninstalled
echo   87       = wusa cannot uninstall this package type (normal for
echo              Windows 11 cumulative updates - DISM is next)
echo.

echo.
echo ============================================================
echo  3 of 4  -  the supported route: DISM
echo ============================================================
echo   Finding the real package name...
set PKG=
for /f "tokens=*" %%P in ('dism /online /get-packages /format:table ^| findstr /i "RollupFix"') do (
  for /f "tokens=1 delims= " %%N in ("%%P") do set PKG=%%N
)
if "!PKG!"=="" (
  echo   Could not find a RollupFix package to remove.
  echo   Full package list written to the report file.
  dism /online /get-packages /format:table >> "%LOG%" 2>&1
) else (
  echo   Package: !PKG!
  echo   Package: !PKG! >> "%LOG%"
  echo   Removing it...
  dism /online /remove-package /packagename:!PKG! /norestart >> "%LOG%" 2>&1
  echo   DISM exit code = !errorlevel!
  echo   DISM exit code = !errorlevel! >> "%LOG%"
  echo   0    = removed, restart will finish it
  echo   3010 = removed, restart REQUIRED
  echo   87 or 0x800f0825 = this update cannot be removed on this PC
)

echo.
echo ============================================================
echo  4 of 4  -  is a removal actually pending?
echo ============================================================
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending" >nul 2>&1
if errorlevel 1 (
  echo   NO reboot is pending.
  echo   ^>^> A restart will NOT change anything. Do not restart a 3rd time.
  echo   NO reboot pending >> "%LOG%"
) else (
  echo   YES - a servicing change is pending.
  echo   ^>^> Restart now. This one should actually take effect.
  echo   reboot pending = YES >> "%LOG%"
)

echo.
echo   Report saved: %LOG%
echo   Claude reads this file, so just say "did it work" afterwards.
echo.
pause
