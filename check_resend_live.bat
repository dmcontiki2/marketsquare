@echo off
setlocal
cd /d "%~dp0"
title Prove the new Resend key still sends
color 0B
set SRV=root@178.104.73.239
echo(
echo   Testing the LIVE key against Resend (sends nothing, shows no secrets)...
echo(
scp -q scripts\check_resend_live.sh %SRV%:/tmp/check_resend_live.sh
if errorlevel 1 goto :fail
ssh %SRV% "bash /tmp/check_resend_live.sh; rm -f /tmp/check_resend_live.sh"
echo(
echo   Done. Nothing was changed and no email was sent.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
