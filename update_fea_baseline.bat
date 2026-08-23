@echo off
REM update_fea_baseline.bat -- one-shot, ATTENDED (DW-061: deploy-not-tamper pattern)
REM v2: points at the LIVE instrument in the web root (/var/www/marketsquare -- the copy
REM the 01:30 cron sensor runs, with index.html + baseline beside it), NOT the src clone.
REM v2 guard: a traceback/garbage in step 1 ABORTS -- only a real delta reaches the pause.
REM BAT LESSON honored: ssh output goes to a %TEMP% file, never for /f ('ssh ...').
setlocal
set SERVER=msdeploy@178.104.73.239
set FEA=/var/www/marketsquare/fea_integrity_check.py
set OUT=%TEMP%\fea_check.json

echo === 1/3 current FEA status (the delta to eyeball) ===
ssh -o ConnectTimeout=15 %SERVER% "python3 %FEA% --json" > "%OUT%" 2>&1
type "%OUT%"
echo.
findstr /C:"\"status\"" "%OUT%" >nul || (
  echo ABORT: step 1 did not return FEA JSON - nothing was changed. Show the output above to Claude.
  goto :done
)
findstr /C:"\"status\": \"ok\"" "%OUT%" >nul && (
  echo Baseline already clean - nothing to update.
  goto :done
)
echo === If the delta matches the known deploys - f77f08c 21 Aug and 74ab420 23 Aug - continue. Else Ctrl+C. ===
pause

echo === 2/3 refreshing baseline ===
ssh -o ConnectTimeout=15 %SERVER% "python3 %FEA% --update-baseline"

echo === 3/3 re-check (want: status ok, alerts []) ===
ssh -o ConnectTimeout=15 %SERVER% "python3 %FEA% --json" > "%OUT%" 2>&1
type "%OUT%"
findstr /C:"\"status\": \"ok\"" "%OUT%" >nul && (
  echo RESULT: OK - DW-061 closes on the next watch pass.
) || (
  echo RESULT: still alerting - do NOT close DW-061; show this output to Claude.
)
:done
endlocal
pause
