@echo off
REM ===========================================================================
REM deploy_email_worker.bat -- EMAIL-FIREWALL-1 (RUL-069), armed 5 Sep 2026.
REM
REM Publishes cloudflare_email_worker with CUSTOMER_FIREWALL="1" set in
REM wrangler.toml, so no customer email is ever forwarded to a personal inbox.
REM
REM WHAT ARMING MEANS, so nobody runs this casually: with the firewall on, a
REM message that cannot be triaged is REJECTED at SMTP time. The sender is told,
REM which is honest -- but it does mean the app being down turns into bounced
REM customer mail. Do not arm unless https://trustsquare.co/email/inbound is
REM answering; the pre-flight below checks the app is up before deploying.
REM
REM Runs from the host queue (RUL-095): never waits for a key, never opens a
REM browser. CI=1 makes wrangler fail loudly instead of prompting.
REM ===========================================================================
setlocal
cd /d "%~dp0cloudflare_email_worker"
set "CI=1"
set "WRANGLER_SEND_METRICS=false"
set "LOG=%~dp0cloudflare_email_worker\worker_deploy_log.txt"

echo. >>"%LOG%"
echo ===== deploy_email_worker %date% %time% ===== >>"%LOG%"

echo --- pre-flight: is the app answering? --- >>"%LOG%"
curl -s -o nul -w "health %%{http_code}\n" --max-time 20 https://trustsquare.co/health >>"%LOG%" 2>&1
findstr /c:"health 200" "%LOG%" >nul 2>&1
if errorlevel 1 (
  echo [X] trustsquare.co/health is not answering 200 -- REFUSING to arm the firewall. >>"%LOG%"
  echo [X] app not healthy -- firewall NOT armed
  exit /b 2
)

echo --- whoami --- >>"%LOG%"
call npx --yes wrangler@3 whoami >>"%LOG%" 2>&1
if errorlevel 1 (
  echo [X] wrangler is not authenticated on this machine. Nothing deployed. >>"%LOG%"
  echo [X] wrangler not authenticated -- see %LOG%
  exit /b 3
)

if not exist node_modules (
  echo --- npm install (postal-mime) --- >>"%LOG%"
  call npm install --no-audit --no-fund >>"%LOG%" 2>&1
  if errorlevel 1 (
    echo [X] npm install FAILED -- nothing deployed. >>"%LOG%"
    echo [X] npm install FAILED -- see %LOG%
    exit /b 4
  )
)

echo --- deploy --- >>"%LOG%"
call npx --yes wrangler@3 deploy >>"%LOG%" 2>&1
if errorlevel 1 (
  echo [X] wrangler deploy FAILED -- the firewall is NOT armed. >>"%LOG%"
  echo [X] wrangler deploy FAILED -- see %LOG%
  exit /b 5
)

echo [OK] email worker deployed with CUSTOMER_FIREWALL=1. >>"%LOG%"
echo [OK] email worker deployed with CUSTOMER_FIREWALL=1.
endlocal
exit /b 0
