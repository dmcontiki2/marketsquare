@echo off
setlocal
echo ==================================================
echo  TrustSquare - add Resend API key to the server
echo ==================================================
echo.
echo Paste your Resend API key (starts with re_) and press Enter.
echo It goes STRAIGHT to the server over ssh - it is never stored on this PC
echo and Claude never sees it.
echo.
set /p RKEY=Key: 
if "%RKEY%"=="" (
  echo No key entered - nothing done.
  pause
  exit /b 1
)
echo.
echo Writing key to the server (owner-only file, chmod 600)...
ssh -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 root@178.104.73.239 "umask 077 && mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=RESEND_API_KEY=%RKEY%\n' > /etc/systemd/system/marketsquare.service.d/resend.conf && chmod 600 /etc/systemd/system/marketsquare.service.d/resend.conf && systemctl daemon-reload && systemctl restart marketsquare && sleep 3 && systemctl is-active marketsquare && echo KEY-FILE-LINES: && grep -c Environment /etc/systemd/system/marketsquare.service.d/resend.conf"
if %errorlevel% neq 0 (
  echo.
  echo ERROR: write or restart failed - tell Claude before retrying.
  pause
  exit /b 1
)
set RKEY=
echo.
echo Done: key stored 600, BEA restarted and active.
echo Close this window and tell Claude: "key is in".
pause
