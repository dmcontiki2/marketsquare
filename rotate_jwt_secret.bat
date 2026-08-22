@echo off
setlocal
cd /d "%~dp0"
title Rotate MS_JWT_SECRET
color 0C
set SRV=root@178.104.73.239
echo(
echo   Rotating MS_JWT_SECRET (the token-signing key) and moving it out of
echo   the box-wide file into the 600 secrets file.
echo   Automatic rollback if the service does not come back.
echo   No secret values are printed.
echo(
scp -q scripts\rotate_jwt_secret.py %SRV%:/tmp/rotate_jwt_secret.py
if errorlevel 1 goto :fail
ssh %SRV% "python3 /tmp/rotate_jwt_secret.py; rm -f /tmp/rotate_jwt_secret.py"
echo(
echo   Paste this whole window to Claude - it contains no secrets.
goto :end
:fail
echo   Upload failed - could not reach the server.
:end
echo(
pause
