@echo off
setlocal
echo ==================================================
echo  TrustSquare - add OpenAI API key to the server
echo ==================================================
echo.
echo Paste your OpenAI API key (starts with sk-) and press Enter.
echo It goes STRAIGHT to the server over ssh - it is never stored on this PC
echo and Claude never sees it.
echo.
set /p OKEY=Key: 
if "%OKEY%"=="" (
  echo No key entered - nothing done.
  pause
  exit /b 1
)
echo.
echo Writing key to the server (owner-only file, chmod 600)...
ssh -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 root@178.104.73.239 "umask 077 && mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=OPENAI_API_KEY=%OKEY%\n' > /etc/systemd/system/marketsquare.service.d/openai.conf && chmod 600 /etc/systemd/system/marketsquare.service.d/openai.conf && systemctl daemon-reload && systemctl restart marketsquare && sleep 3 && systemctl is-active marketsquare && echo KEY-FILE-LINES: && grep -c Environment /etc/systemd/system/marketsquare.service.d/openai.conf"
if %errorlevel% neq 0 (
  echo.
  echo ERROR: write or restart failed - tell Claude before retrying.
  pause
  exit /b 1
)
set OKEY=
echo.
echo Done: key stored 600, BEA restarted and active. Re-run today's loop or
echo the monitor to see OpenAI flip STANDBY -^> UP.
echo Close this window and tell Claude: "openai key is in".
pause
