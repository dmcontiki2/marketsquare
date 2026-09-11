@echo off
setlocal
:: maint_host.bat - MAINT-HOST-1 (11 Sep 2026). Runs the SHADOW maintenance agent ON DAVID'S PC
:: when the Cowork Linux sandbox cannot start. Sibling of ledger_host.bat / rulings_host.bat.
::
:: Why: the daily maintenance loop's step 2 (read the fault queue, classify, shadow-patch, post
:: the heartbeat) was the ONLY step with no host-side lane. On 9 Sep and again on 11 Sep the
:: sandbox died on the KB5124008 Windows-update class (claude-code #92984) and the loop could
:: not read its own queue at all. The boards already had this lane; the brain did not. One
:: missing line turned a tooling outage into a missed run - that is the class this closes.
::
:: SHADOW ONLY. MAINTENANCE_AGENT_ENABLED is never set here - arming is David's act alone
:: (MAINTENANCE_AGENT.md B2b). With the kill switch off the agent cannot commit; it classifies,
:: gates, writes its run report to .maint_agent\ and posts the heartbeat. No deploy, no send,
:: no deletion. Same run the sandbox lane performs, on the same key files (.secrets\).
::
:: STAMP-LOCALE-1 (10 Sep): %DATE% is MM/DD/YYYY here, so build the stamp with PowerShell.
set STAMP=
for /f %%S in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set STAMP=%%S
set OUT=%~dp0host_queue\done\maint_host_%STAMP%.txt
cd /d "%~dp0"
set MS_BEA_URL=https://trustsquare.co
echo === maint_host  %DATE% %TIME%   full run log: %OUT%
python -c "import httpx" 2>nul
if errorlevel 1 (
  echo httpx MISSING on host python - installing for this user only
  python -m pip install --quiet --user httpx
)
python scripts\maintenance_agent.py > "%OUT%" 2>&1
set RC=%ERRORLEVEL%
echo.
echo --- run banner + verdict lines ---
findstr /L /C:"[maint]" "%OUT%"
echo.
echo === maint_host done at %TIME%  rc=%RC%
exit /b %RC%
