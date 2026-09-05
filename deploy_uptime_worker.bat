@echo off
REM ===========================================================================
REM deploy_uptime_worker.bat -- ALERT-OFFORIGIN-1 (5 Sep 2026, DW-097)
REM
REM Publishes ops\cloudflare\uptime_monitor_worker.js (which now carries POST /alert)
REM and binds the ALERT_INGEST_KEY secret to the DEPLOYED worker.
REM
REM ORDER MATTERS, and it is the 28 Aug lesson recorded in UPTIME_DEPLOYED.md:
REM   `wrangler secret put` against a not-yet-deployed worker creates a PLACEHOLDER,
REM   which the following `wrangler deploy` then REPLACES -- taking the secret with it.
REM   So: DEPLOY FIRST, SECRET SECOND. Never the other way round.
REM
REM Runs from the host queue (RUL-095), so it must NEVER wait for a keypress and never
REM open a browser -- CI=1 makes wrangler fail loudly instead of prompting (RG-0262 class).
REM ===========================================================================
setlocal
cd /d "%~dp0"
set "CI=1"
set "WRANGLER_SEND_METRICS=false"
set "LOG=%~dp0ops\cloudflare\worker_deploy_log.txt"
set "CFG=ops\cloudflare\uptime_wrangler.toml"
set "KEYF=%~dp0.secrets\watch_alert_key.txt"

echo. >>"%LOG%"
echo ===== deploy_uptime_worker %date% %time% ===== >>"%LOG%"

if not exist "%KEYF%" (
  echo [X] missing .secrets\watch_alert_key.txt -- nothing deployed. >>"%LOG%"
  echo [X] missing .secrets\watch_alert_key.txt
  exit /b 2
)

echo --- whoami --- >>"%LOG%"
call npx --yes wrangler@latest whoami >>"%LOG%" 2>&1
if errorlevel 1 (
  echo [X] wrangler is not authenticated on this machine. Nothing deployed. >>"%LOG%"
  echo [X] wrangler not authenticated -- see %LOG%
  exit /b 3
)

echo --- deploy --- >>"%LOG%"
call npx --yes wrangler@latest deploy --config "%CFG%" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo [X] wrangler deploy FAILED -- see %LOG% >>"%LOG%"
  echo [X] wrangler deploy FAILED -- see %LOG%
  exit /b 4
)

echo --- secret put ALERT_INGEST_KEY (after the deploy, on purpose) --- >>"%LOG%"
type "%KEYF%" | call npx --yes wrangler@latest secret put ALERT_INGEST_KEY --config "%CFG%" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo [X] secret put FAILED -- the worker is deployed but /alert will answer 503. >>"%LOG%"
  echo [X] secret put FAILED -- see %LOG%
  exit /b 5
)

echo [OK] worker deployed and ALERT_INGEST_KEY bound. >>"%LOG%"
echo [OK] worker deployed and ALERT_INGEST_KEY bound.
endlocal
exit /b 0
