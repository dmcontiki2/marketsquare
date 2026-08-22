@echo off
setlocal
cd /d "%~dp0"
title Which Resend key is each holder using
color 0B
set SRV=root@178.104.73.239
echo(
echo   Comparing Resend keys by fingerprint (read-only, NO secret values shown)...
echo(
scp -q scripts\check_email_keys.sh %SRV%:/tmp/check_email_keys.sh
if errorlevel 1 goto :fail
ssh %SRV% "bash /tmp/check_email_keys.sh; rm -f /tmp/check_email_keys.sh"
echo(
echo   Done. Nothing was changed on the server.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
