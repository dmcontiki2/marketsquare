@echo off
setlocal
cd /d "%~dp0"
title Verify Resend key landed
color 0B
set SRV=root@178.104.73.239
echo(
echo   Verifying the Resend key write (read-only, prints NO secret values)...
echo(
scp -q scripts\check_resend_key.sh %SRV%:/tmp/check_resend_key.sh
if errorlevel 1 goto :fail
ssh %SRV% "bash /tmp/check_resend_key.sh; rm -f /tmp/check_resend_key.sh"
echo(
echo   Done. Nothing was changed on the server.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
