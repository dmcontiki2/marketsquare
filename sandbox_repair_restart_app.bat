@echo off
setlocal
:: sandbox_repair_restart_app.bat - SANDBOX-REPAIR-1 stage 2 (9 Sep 2026)
:: Restarts the Claude desktop app on David's PC. The Cowork Linux sandbox is a VM the app
:: itself manages (WSL is NOT installed on this PC - proven 9 Sep 20:51), so when it fails
:: with "no Plan9 drive shares mounted" the remedy is restarting the app. That used to be a
:: David click; now it is a queued action (RUL-095), queued by Claude only once the sandbox
:: is proven dead this session. Guard: runs only in the same desktop session as the Claude
:: app, so the restarted app is visible; refuses otherwise. Touches nothing else in the
:: repo, the databases or the server. No money, no sending.
:: NOTE: `timeout` does not work here (the host agent runs bats with no console/stdin),
:: so waits go through PowerShell Start-Sleep.
echo === SANDBOX-REPAIR-1 stage 2 (restart app)  %DATE% %TIME%
echo user=%USERNAME%
set MYSESS=
set CLSESS=
for /f "tokens=1,2" %%A in ('powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sandbox_repair_sess.ps1"') do (
    set MYSESS=%%A
    set CLSESS=%%B
)
echo my session=%MYSESS%  claude session=%CLSESS%
if "%MYSESS%"=="" (
    echo REFUSED: could not read my own session id - not restarting anything blind.
    exit /b 3
)
if "%MYSESS%"=="0" (
    echo REFUSED: running in session 0 - a restarted Claude app would be invisible to David.
    echo The host agent task must run 'only when user is logged on' for stage 2 to be usable.
    exit /b 3
)
if not "%CLSESS%"=="none" if not "%CLSESS%"=="%MYSESS%" (
    echo REFUSED: Claude runs in session %CLSESS% but this script in %MYSESS% - the restart would land on the wrong desktop.
    exit /b 3
)
echo.
echo --- DIAGNOSTICS before restart (read-only; what the sandbox VM is made of)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sandbox_repair_diag.ps1" 2>&1
echo.
echo --- closing Claude desktop
taskkill /IM claude.exe /F 2>&1
powershell -NoProfile -Command "Start-Sleep -Seconds 6"
echo --- starting Claude desktop (same launch as start_session.bat)
start "" "claude:"
echo start rc=%ERRORLEVEL%
powershell -NoProfile -Command "Start-Sleep -Seconds 25"
echo --- Claude processes AFTER
tasklist /FI "IMAGENAME eq claude.exe" /FO CSV /NH 2>&1
echo.
:: WINDOW-ZORDER-2: the fresh app pins itself always-on-top; one-shot demote, no second watcher
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\unpin_claude.ps1" 2>&1 | findstr /I "Demoted"
echo === STAGE 2 done at %TIME%. Claude re-tests the sandbox once its session relinks.
exit /b 0
