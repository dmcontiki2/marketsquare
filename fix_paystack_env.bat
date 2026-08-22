@echo off
setlocal
cd /d "%~dp0"
title Find and fix every stale Paystack key
color 0C
set SRV=root@178.104.73.239
echo(
echo   Finding EVERY definition of the Paystack key and putting them all
echo   on the new value. No secret values are printed.
echo(
scp -q scripts\fix_paystack_env.py %SRV%:/tmp/fix_paystack_env.py
if errorlevel 1 goto :fail
ssh %SRV% "python3 /tmp/fix_paystack_env.py; rm -f /tmp/fix_paystack_env.py"
echo(
echo   Paste this whole window to Claude - it contains no secrets.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
