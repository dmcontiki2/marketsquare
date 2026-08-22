@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
echo run started %date% %time% > .secrets\close_secrets_log.txt
%PY% scripts\close_selfissued_secrets.py >> .secrets\close_secrets_log.txt 2>&1
echo exitcode %errorlevel% >> .secrets\close_secrets_log.txt
type .secrets\close_secrets_log.txt
echo(
pause
