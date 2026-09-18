@echo off
setlocal
:: enable_scoreboard_unattended.bat - SCOREBOARD-2 (18 Sep 2026)
::
:: Non-interactive twin of enable_scoreboard.bat, for the RUL-095 host queue.
::
:: WHY: OPEN_LOOPS L3 sat as a [D] row from 3 Aug to 18 Sep saying "next deploy carries it, then
:: run enable_scoreboard.bat once". The deploy was never what was missing - the code has ridden
:: many deploys. What was missing is that the bat could not be run by anything except a human at
:: the keyboard: `choice /M` waits for a keypress and `pause` waits for another, so the host-queue
:: worker would hang on it forever. Under RUL-095 running a bat is Claude's, not David's - but only
:: if the bat can actually be run unattended. That, not the deploy, is why the row aged six weeks.
::
:: Same two steps, same server, same flag, no prompts. The interactive original is left in place
:: for David; this is the lane the queue uses. Reverse with disable_scoreboard.bat.
:: Spend: the nightly probe round is well under 1 US cent per night (enable_scoreboard.bat's own
:: figure), and it is bounded by the scoreboard agent's own budget.
cd /d "%~dp0"
echo === enable_scoreboard_unattended  %DATE% %TIME%
echo [1/2] Setting launch_switches.scoreboard_enabled = 1 ...
ssh root@178.104.73.239 "cd /var/www/marketsquare && (sqlite3 marketsquare.db 'ALTER TABLE launch_switches ADD COLUMN scoreboard_enabled INTEGER NOT NULL DEFAULT 0' 2>/dev/null); sqlite3 marketsquare.db 'UPDATE launch_switches SET scoreboard_enabled=1 WHERE id=1' && echo    FLAG ON"
if errorlevel 1 echo    WARNING: flag step returned non-zero
echo [2/2] One probe round so the first table exists ...
ssh root@178.104.73.239 "cd /var/www/marketsquare && python3 ai_scoreboard.py --probe --force --report"
if errorlevel 1 echo    WARNING: probe round returned non-zero
echo === done. Nightly run takes it from here (03:33, after the 03:17 backup).
endlocal
