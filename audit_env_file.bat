@echo off
setlocal
cd /d "%~dp0"
title Prove Paystack + audit /etc/environment
color 0E
set SRV=root@178.104.73.239
echo(
echo   Proving the new Paystack key, then auditing /etc/environment.
echo   Read-only. No secret values are printed.
echo(
scp -q scripts\audit_env_file.sh %SRV%:/tmp/audit_env_file.sh
if errorlevel 1 goto :fail
ssh %SRV% "bash /tmp/audit_env_file.sh; rm -f /tmp/audit_env_file.sh"
echo(
echo   Paste this whole window to Claude - it contains no secrets.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
