@echo off
setlocal
cd /d "%~dp0"
title Lock down /etc/environment
color 0C
set SRV=root@178.104.73.239
echo(
echo   Making /etc/environment owner-only (600) and checking nothing breaks.
echo   No secret values are printed.
echo(
scp -q scripts\harden_env_file.sh %SRV%:/tmp/harden_env_file.sh
if errorlevel 1 goto :fail
ssh %SRV% "bash /tmp/harden_env_file.sh; rm -f /tmp/harden_env_file.sh"
echo(
echo   Paste this whole window to Claude - it contains no secrets.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
