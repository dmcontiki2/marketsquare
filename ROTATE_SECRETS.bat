@echo off
REM ============================================================================
REM  ROTATE_SECRETS.bat -- rotate TrustSquare's five SELF-ISSUED secrets.
REM
REM  REWRITTEN 26 Aug 2026 (SECRET-ONSCREEN-1, ledger RG-0189).
REM  The old step [3/4] scp'd the server's combined values file to
REM  .secrets\rotated_secrets.txt and LEFT IT THERE. That file then sat on the PC
REM  for four days until an unrelated request to open Notepad restored it as the
REM  previous tab and a screenshot captured five live credentials -- forcing a
REM  re-rotation three days before soft launch.
REM
REM  The dump is now a TRANSIT BUFFER, not a resting place:
REM      server -> rotated_secrets.txt -> split into per-purpose files -> gone
REM
REM  The only value that cannot be filed automatically is MS_ADMIN_PASSWORD --
REM  it is a HUMAN credential and belongs in a password manager. So the script
REM  stops, tells you to save it, and waits. It will not shred the last copy of
REM  something only you can keep. That pause is deliberate and is the one moment
REM  the file is open; everything else is hands-off.
REM ============================================================================
setlocal
cd /d "%~dp0"
set SRV=root@178.104.73.239
set DUMP=.secrets\rotated_secrets.txt

echo ============================================================
echo   TrustSquare secret rotation
echo   Nothing secret is ever printed to this window.
echo ============================================================
echo.
echo [1/6] Uploading the rotation script...
scp scripts\rotate_secrets.py %SRV%:/tmp/rotate_secrets.py
if errorlevel 1 goto :fail
echo.
echo [2/6] Rotating on the server...
ssh %SRV% "python3 /tmp/rotate_secrets.py"
set RC=%errorlevel%
if not "%RC%"=="0" echo   ^(exit %RC% - read the !! lines above^)
echo.
echo [3/6] Collecting the new values (TRANSIT ONLY - not a resting place)...
if not exist ".secrets" mkdir ".secrets"
scp %SRV%:/root/ts_rotated_latest.txt "%DUMP%"
if errorlevel 1 goto :nofile
echo   collected.
echo.
echo [4/6] Wiping the copies off the server...
ssh %SRV% "rm -f /root/ts_rotated_latest.txt /tmp/rotate_secrets.py"
echo   done.

REM --- WATCH-COPY-REFRESH-1 (28 Aug 2026) ------------------------------------
REM The daily watch reads the RED-alert Resend key from an OUT-OF-BAND COPY at
REM /etc/marketsquare/resend.watch.conf -- a duplicate of the app's systemd
REM drop-in, first installed by the retired fix_watch_alerts.bat on 5 Aug 2026.
REM A rotation replaces the drop-in and leaves that copy behind, so the ONE
REM channel that wakes David about an outage dies SILENTLY -- nothing exercises
REM it except a real RED. That is exactly what happened: the 22-23 Aug rotation
REM orphaned it, and it was found on 26 Aug only because a genuine RED fired and
REM never arrived, leaving the site unwatched for six days into launch week.
REM Refreshing the copy IN THE ROTATION removes the human step that failed.
REM Asserted by ledger RG-0201.
echo.
echo [4b/6] Refreshing the watch RED-alert copy from the live drop-in...
ssh %SRV% "install -o root -g msdeploy -m 640 /etc/systemd/system/marketsquare.service.d/resend.conf /etc/marketsquare/resend.watch.conf"
if errorlevel 1 (
  echo   [!!] COULD NOT refresh /etc/marketsquare/resend.watch.conf.
  echo   [!!] The outage alarm is now running on a STALE key - fix before you walk away.
) else (
  echo   [ok] watch copy refreshed - the RED-alert path carries the new key.
)
REM ---------------------------------------------------------------------------
echo.
echo [5/6] Filing the values into their per-purpose files...
python3 scripts\split_rotated_secrets.py
if errorlevel 1 python scripts\split_rotated_secrets.py
echo.
echo ============================================================
echo   ONE THING ONLY YOU CAN DO
echo   MS_ADMIN_PASSWORD is a human credential - it is deliberately
echo   NOT written to any file. Open %DUMP%,
echo   copy it into your password manager, and close the file.
echo ============================================================
echo.
pause
echo.
echo [6/6] Shredding the combined dump and pruning stale key backups...
if exist "%DUMP%" del /f /q "%DUMP%"
if exist "%DUMP%" (
  echo   [!!] COULD NOT DELETE %DUMP% - delete it by hand NOW.
) else (
  echo   [ok] combined dump gone - no file on this PC holds the full set.
)

REM Prune credential backups older than 7 days. A .bak beside a live key file is a
REM second copy of a secret that nothing is watching -- the slow version of the same
REM fault. Asserted by ledger RG-0189.
powershell -NoProfile -Command ^
  "$c=0; Get-ChildItem '.secrets' -File -ErrorAction SilentlyContinue |" ^
  "  Where-Object { $_.Name -match '\.bak[-.]' -and $_.LastWriteTime -lt (Get-Date).AddDays(-7) } |" ^
  "  ForEach-Object { Remove-Item $_.FullName -Force; $c++ };" ^
  "if($c -gt 0){ Write-Host ('  [ok] pruned ' + $c + ' credential backup(s) older than 7 days') }" ^
  "else { Write-Host '  [ok] no stale credential backups to prune' }"

echo.
echo ============================================================
echo   ROTATION COMPLETE.
echo   Verify with:  python3 scripts\regression_ledger.py
echo   (RG-0146 no credential BURNT - RG-0189 no dump at rest)
echo ============================================================
goto :end

:nofile
echo   No values file came back - the rotation probably rolled back.
echo   Nothing changed. Paste the [2/6] output to Claude (it carries no values).
goto :end
:fail
echo   Upload failed - nothing was changed on the server.
:end
endlocal
