@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
echo run started %date% %time% > .secrets\inbound_fix_log2.txt
%PY% scripts\finish_email_secret.py >> .secrets\inbound_fix_log2.txt 2>&1
echo exitcode %errorlevel% >> .secrets\inbound_fix_log2.txt
type .secrets\inbound_fix_log2.txt
echo(
pause
