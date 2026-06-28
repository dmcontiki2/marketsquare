@echo off
REM ── Find the REAL crash cause. Writes to a file AND holds the window open. Read-only; site stays up. ──
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set OUT=%~dp0bea_crash_report.txt

REM everything below is teed to the screen AND saved to bea_crash_report.txt
(
echo ============================================================
echo  BEA CRASH DIAGNOSIS  ^(loads systemd env; read-only^)
echo ============================================================
echo.
echo [A] Is MS_API_KEY in the systemd service env? ^(proves the key is fine^):
ssh %SERVER% "systemctl show marketsquare -p Environment -p EnvironmentFiles | tr ' ' '\n' | grep -iE 'MS_API_KEY|EnvironmentFile' | sed 's/=.*/=<set>/'"
echo.
echo [B] Import the CRASHED file WITH the service environment ^(the true error^):
ssh %SERVER% "cd %REMOTE% && cp main.py.CRASHED _probe.py 2>/dev/null; set -a; eval $(systemctl show marketsquare -p Environment --value | tr ' ' '\n' | sed 's/^/export /' 2>/dev/null); python3 -c 'import _probe' 2>&1 | tail -30; rm -f _probe.py"
echo.
echo [C] Crash traceback from the service logs ^(last 3 hours^):
ssh %SERVER% "journalctl -u marketsquare --no-pager --since '-3 hours' | grep -B2 -A20 -iE 'traceback|importerror|nameerror|attributeerror|syntaxerror|modulenotfound' | tail -40"
echo.
echo ============================================================
echo  Saved to: %OUT%
echo  Open that file and paste its contents to Claude.
echo ============================================================
) > "%OUT%" 2>&1

type "%OUT%"
echo.
echo.
echo  ^>^>^> Full report saved to bea_crash_report.txt ^<^<^<
echo  ^>^>^> Window will stay open. Press any key when done reading. ^<^<^<
pause >nul
