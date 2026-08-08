@echo off
setlocal
cd /d "%~dp0"
set SRV=root@178.104.73.239
echo ============================================================
echo   TrustSquare secret rotation
echo   Nothing secret is ever printed to this window.
echo ============================================================
echo.
echo [1/4] Uploading the rotation script...
scp scripts\rotate_secrets.py %SRV%:/tmp/rotate_secrets.py
if errorlevel 1 goto :fail
echo.
echo [2/4] Rotating on the server...
ssh %SRV% "python3 /tmp/rotate_secrets.py"
set RC=%errorlevel%
if not "%RC%"=="0" echo   ^(exit %RC% - read the !! lines above^)
echo.
echo [3/4] Collecting the new values into .secrets\ ...
if not exist ".secrets" mkdir ".secrets"
scp %SRV%:/root/ts_rotated_latest.txt ".secrets\rotated_secrets.txt"
if errorlevel 1 goto :nofile
echo   saved to .secrets\rotated_secrets.txt
echo.
echo [4/4] Wiping the copies off the server...
ssh %SRV% "rm -f /root/ts_rotated_latest.txt /tmp/rotate_secrets.py"
echo   done.
echo.
echo ============================================================
echo   Your new admin password is in .secrets\rotated_secrets.txt
echo   Open that file - do not paste it into chat.
echo ============================================================
goto :end
:nofile
echo   No values file came back - the rotation probably rolled back.
echo   Nothing changed. Paste the [2/4] output to Claude.
goto :end
:fail
echo   Upload failed - nothing was changed on the server.
:end
echo.
pause
