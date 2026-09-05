@echo off
REM ===========================================================================
REM deploy_email_worker.bat -- EMAIL-FIREWALL-1 (RUL-069), armed 5 Sep 2026 on
REM David's word: "Please close that door for me."
REM
REM Publishes cloudflare_email_worker with CUSTOMER_FIREWALL="1" set in
REM wrangler.toml, so no customer email is ever forwarded to a personal inbox.
REM
REM WHAT ARMING MEANS, so nobody runs this casually: with the firewall on, a
REM message that cannot be triaged is REJECTED at SMTP time. The sender is told,
REM which is honest -- but it does mean the app being down turns into bounced
REM customer mail. The pre-flight below REFUSES to arm unless the app answers 200.
REM
REM WRITTEN WITH GOTO, NOT PARENTHESISED IF-BLOCKS, ON PURPOSE. The first cut
REM died with "--- was unexpected at this time" because an echo inside an
REM if-block contained literal parentheses -- cmd closed the block early. Labels
REM cannot be broken that way, and this bat runs unattended from the host queue
REM where a parse error is a silent no-op.
REM ===========================================================================
setlocal
cd /d "%~dp0cloudflare_email_worker"
set "CI=1"
set "WRANGLER_SEND_METRICS=false"
set "LOG=%~dp0cloudflare_email_worker\worker_deploy_log.txt"
set "HC=%TEMP%\ts_fw_health.txt"

echo. >>"%LOG%"
echo ===== deploy_email_worker %date% %time% ===== >>"%LOG%"

echo --- pre-flight, is the app answering --- >>"%LOG%"
del /q "%HC%" >nul 2>&1
curl -s -o nul -w "%%{http_code}" --max-time 20 https://trustsquare.co/health > "%HC%" 2>>"%LOG%"
set /p HEALTH=<"%HC%"
echo health=%HEALTH% >>"%LOG%"
if not "%HEALTH%"=="200" goto :nothealthy

echo --- whoami --- >>"%LOG%"
call npx --yes wrangler@3 whoami >>"%LOG%" 2>&1
if errorlevel 1 goto :noauth

if exist node_modules goto :havedeps
echo --- npm install, postal-mime --- >>"%LOG%"
call npm install --no-audit --no-fund >>"%LOG%" 2>&1
if errorlevel 1 goto :nodeps
:havedeps

echo --- deploy --- >>"%LOG%"
call npx --yes wrangler@3 deploy >>"%LOG%" 2>&1
if errorlevel 1 goto :nodeploy

echo [OK] email worker deployed with CUSTOMER_FIREWALL=1. >>"%LOG%"
echo [OK] email worker deployed with CUSTOMER_FIREWALL=1.
endlocal
exit /b 0

:nothealthy
echo [X] trustsquare.co/health did not answer 200 -- REFUSING to arm the firewall. >>"%LOG%"
echo [X] app not healthy -- firewall NOT armed
endlocal
exit /b 2

:noauth
echo [X] wrangler is not authenticated on this machine. Nothing deployed. >>"%LOG%"
echo [X] wrangler not authenticated -- see the deploy log
endlocal
exit /b 3

:nodeps
echo [X] npm install FAILED -- nothing deployed. >>"%LOG%"
echo [X] npm install FAILED -- see the deploy log
endlocal
exit /b 4

:nodeploy
echo [X] wrangler deploy FAILED -- the firewall is NOT armed. >>"%LOG%"
echo [X] wrangler deploy FAILED -- see the deploy log
endlocal
exit /b 5
