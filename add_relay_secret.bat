@echo off
REM add_relay_secret.bat v3 - runs silently and writes EVERYTHING to
REM .secrets\relay_install_log.txt (statuses only, never the secret value).
REM Claude reads that log through the folder bridge - no window-watching needed.
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
echo run started %date% %time% > .secrets\relay_install_log.txt
%PY% scripts\relay_secret_install.py >> .secrets\relay_install_log.txt 2>&1
echo exitcode %errorlevel% >> .secrets\relay_install_log.txt
