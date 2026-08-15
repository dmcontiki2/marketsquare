@echo off
setlocal
echo ================================================================
echo  TrustSquare - arm the Paystack webhook (PAYSTACK_WEBHOOK_SECRET)
echo ================================================================
echo.
echo Step 1: checking whether the server already has the secret...
ssh -o ConnectTimeout=15 root@178.104.73.239 "systemctl show marketsquare -p Environment | tr ' ' '\n' | grep -c '^PAYSTACK_WEBHOOK_SECRET=' || true" > "%TEMP%\ts_whk.txt" 2>nul
set /p WHKSET=<"%TEMP%\ts_whk.txt"
del "%TEMP%\ts_whk.txt" >nul 2>&1
if "%WHKSET%"=="1" (
  echo ALREADY SET on the server - nothing to do. The webhook lane is armed.
  pause
  exit /b 0
)
echo Not set yet (or check could not run - pasting again is safe either way).
echo.
echo Step 2: paste your LIVE SECRET KEY (starts with sk_live_) and press Enter.
echo Paystack signs webhooks with this same key - there is no separate secret.
echo It goes STRAIGHT to the server over ssh - it is never stored on this PC
echo and Claude never sees it.
echo.
set /p WKEY=Key: 
if "%WKEY%"=="" (
  echo No key entered - nothing done.
  pause
  exit /b 1
)
echo.
echo Writing key to the server (owner-only file, chmod 600) + restarting BEA...
ssh -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 root@178.104.73.239 "umask 077 && mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=PAYSTACK_WEBHOOK_SECRET=%WKEY%\n' > /etc/systemd/system/marketsquare.service.d/paystack_webhook.conf && chmod 600 /etc/systemd/system/marketsquare.service.d/paystack_webhook.conf && systemctl daemon-reload && systemctl restart marketsquare && sleep 3 && systemctl is-active marketsquare"
if %errorlevel% neq 0 (
  echo.
  echo ERROR: write or restart failed - tell Claude before retrying.
  pause
  exit /b 1
)
set WKEY=
echo.
echo Done: webhook secret stored 600, BEA restarted and active.
echo Close this window and tell Claude: "webhook key is in".
pause
