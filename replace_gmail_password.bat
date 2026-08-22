@echo off
setlocal
cd /d "%~dp0"
title Replace the Gmail app password
color 0E
set SRV=root@178.104.73.239
echo(
echo   Paste the NEW 16-character Google app password (spaces are fine - they
echo   are stripped). It goes STRAIGHT to the server over ssh, is never stored
echo   on this PC, and Claude never sees it.
echo(
set /p GPW=New app password: 
if "%GPW%"=="" (
  echo No password entered - nothing done.
  pause
  exit /b 1
)
set GPW=%GPW: =%
echo(
echo [1/3] Writing to the server (owner-only, chmod 600)...
ssh -o ConnectTimeout=15 %SRV% "umask 077 && mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=GMAIL_APP_PASSWORD=%GPW%\n' > /etc/systemd/system/marketsquare.service.d/gmail.conf && chmod 600 /etc/systemd/system/marketsquare.service.d/gmail.conf && python3 -c \"import re,os; p='/etc/environment'; s=open(p).read(); open(p,'w').write(re.sub(r'(?m)^\s*GMAIL_APP_PASSWORD=.*\n?','',s)); os.chmod(p,0o600)\" && systemctl daemon-reload && systemctl restart marketsquare && sleep 4 && systemctl is-active marketsquare"
set RC=%errorlevel%
set GPW=
if not "%RC%"=="0" (
  echo   ERROR: write or restart failed - tell Claude before retrying.
  pause
  exit /b 1
)
echo(
echo [2/3] Verifying by logging in to Gmail SMTP (sends nothing)...
scp -q scripts\verify_gmail_password.py %SRV%:/tmp/verify_gmail_password.py
ssh %SRV% "python3 /tmp/verify_gmail_password.py; rm -f /tmp/verify_gmail_password.py"
echo(
echo [3/3] Done. Paste this whole window to Claude - it contains no secrets.
echo(
pause
