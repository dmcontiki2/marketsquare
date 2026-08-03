@echo off
title TrustSquare - Enable the AI scoreboard agent (nightly probes)
color 0A
echo.
echo  ============================================================
echo   AI SCOREBOARD - ENABLE NIGHTLY PROBES  (SCOREBOARD-1)
echo  ============================================================
echo.
echo  This turns ON the silent scoreboard agent: every night at 03:33
echo  it probes every configured AI lane x task tier and builds the
echo  rolling 90-day ranking (uptime / latency / cost, quality-gated).
echo  Estimated spend: well under 1 US cent per night.
echo.
echo  NOTE: the code must be ON the server first (ships with the next
echo  deploy after 3 Aug 2026). Off by default until you run this.
echo.
choice /M "Enable nightly scoreboard probes"
if errorlevel 2 exit /b 0
echo.
echo  [1/2] Setting launch_switches.scoreboard_enabled = 1 ...
ssh root@178.104.73.239 "cd /var/www/marketsquare && (sqlite3 marketsquare.db 'ALTER TABLE launch_switches ADD COLUMN scoreboard_enabled INTEGER NOT NULL DEFAULT 0' 2>/dev/null); sqlite3 marketsquare.db 'UPDATE launch_switches SET scoreboard_enabled=1 WHERE id=1' && echo    FLAG ON"
echo.
echo  [2/2] Running one attended probe round so you see the first table...
ssh root@178.104.73.239 "cd /var/www/marketsquare && python3 ai_scoreboard.py --probe --force --report"
echo.
echo  Done. The nightly run takes it from here (03:33, after the 03:17 backup).
echo  Turn it off any time with disable_scoreboard.bat.
pause
