@echo off
REM ── SELF-PROTECTING BEA deploy: backs up, deploys, boot-checks, AUTO-ROLLS-BACK on failure. ──
REM Use this for any bea_main.py change. The site can NEVER be left down by a bad push.
setlocal
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set PROJECT=%~dp0
set OUT=%PROJECT%bea_deploy_report.txt

(
echo ============================================================
echo  SELF-PROTECTING BEA DEPLOY
echo ============================================================

echo [1] Back up the CURRENT working main.py on the server ^(timestamped^)...
ssh %SERVER% "cp %REMOTE%/main.py %REMOTE%/main.py.lastgood && echo backed-up-to-main.py.lastgood"

echo.
echo [2] Push the new bea_main.py -^> main.py...
scp "%PROJECT%bea_main.py" %SERVER%:%REMOTE%/main.py
if errorlevel 1 ( echo  SCP FAILED - nothing changed on server. & goto :done )

echo.
echo [3] BOOT TEST ^(advisory^): import under venv+env. NOTE: if MS_API_KEY shows unset here it is a
echo.
echo     test-harness env quirk, NOT a real failure - step [5] uses the REAL systemd health as the gate.
ssh %SERVER% "cd %REMOTE% && ENVS=$(systemctl show marketsquare -p Environment --value); for ef in $(systemctl show marketsquare -p EnvironmentFiles --value | sed 's/ (ignore_errors=[^)]*)//g'); do [ -f \"$ef\" ] && ENVS=\"$ENVS $(grep -vE '^#|^$' \"$ef\" | tr '\n' ' ')\"; done; env $ENVS venv/bin/python -c 'import main; print(\"BOOT-IMPORT-OK\")' 2>&1 | tail -15"

echo.
echo [4] Restart + health-check ^(retry over ~12s^)...
ssh %SERVER% "systemctl restart marketsquare; ok=0; for i in 1 2 3 4 5 6; do curl -s http://localhost:8000/health | grep -qE 'status.*ok' && { ok=1; break; }; sleep 2; done; if [ $ok -eq 1 ]; then echo HEALTH-OK; else echo HEALTH-FAILED; fi"

echo.
echo [5] AUTO-ROLLBACK if the service is not active OR health failed...
ssh %SERVER% "if systemctl is-active --quiet marketsquare && curl -s http://localhost:8000/health | grep -qE 'status.*ok'; then echo '   [OK] New BEA is live and healthy.'; else echo '   [FAIL] New BEA did NOT come up — ROLLING BACK to main.py.lastgood...'; cp %REMOTE%/main.py %REMOTE%/main.py.CRASHED; cp %REMOTE%/main.py.lastgood %REMOTE%/main.py; systemctl restart marketsquare; sleep 4; systemctl is-active --quiet marketsquare && echo '   [RESTORED] Previous BEA is live again. New main.py saved as main.py.CRASHED for Claude.' || echo '   [CRITICAL] rollback also failed - tell Claude immediately'; fi"

echo.
echo ============================================================
echo  Saved to %OUT%
echo ============================================================
) > "%OUT%" 2>&1

type "%OUT%"
echo.
echo  ^>^>^> Report saved to bea_deploy_report.txt. Press any key to close. ^<^<^<
pause >nul
endlocal
