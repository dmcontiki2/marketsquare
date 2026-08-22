@echo off
setlocal
cd /d "%~dp0"
title Rotate the Paystack live secret key
color 0E
set SRV=root@178.104.73.239
echo ================================================================
echo   TrustSquare - ROTATE the Paystack live secret key
echo ================================================================
echo.
echo   This replaces BOTH PAYSTACK_SECRET_KEY and PAYSTACK_WEBHOOK_SECRET
echo   (Paystack signs webhooks with the same key), restarts the service
echo   and proves the new key authenticates.
echo.
echo   Paste the NEW key from Paystack (starts with sk_live_) and press Enter.
echo   It goes STRAIGHT to the server over ssh - never stored on this PC,
echo   never shown to Claude.
echo.
set /p PKEY=New key: 
if "%PKEY%"=="" (
  echo No key entered - nothing done.
  pause
  exit /b 1
)
echo.
echo [1/3] Writing both values to the server (owner-only, chmod 600)...
ssh -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 %SRV% "umask 077 && mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=PAYSTACK_SECRET_KEY=%PKEY%\nEnvironment=PAYSTACK_WEBHOOK_SECRET=%PKEY%\n' > /etc/systemd/system/marketsquare.service.d/paystack.conf && chmod 600 /etc/systemd/system/marketsquare.service.d/paystack.conf && rm -f /etc/systemd/system/marketsquare.service.d/paystack_webhook.conf && systemctl daemon-reload && systemctl restart marketsquare && sleep 4 && systemctl is-active marketsquare"
set RC=%errorlevel%
set PKEY=
if not "%RC%"=="0" (
  echo.
  echo   ERROR: write or restart failed - tell Claude before retrying.
  pause
  exit /b 1
)
echo.
echo [2/3] Verifying (no secret values shown)...
scp -q scripts\verify_paystack_key.sh %SRV%:/tmp/verify_paystack_key.sh
ssh %SRV% "bash /tmp/verify_paystack_key.sh; rm -f /tmp/verify_paystack_key.sh"
echo.
echo [3/3] Done. Paste this whole window to Claude - it contains no secrets.
echo.
pause
