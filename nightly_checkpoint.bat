@echo off
:: nightly_checkpoint.bat - UNATTENDED nightly git checkpoint (no deploy).
:: Run by Windows Task Scheduler. Banks the working tree into git so it never
:: drifts days behind again. LOCAL git only - nothing is scp'd, nothing goes live.
cd /d "%~dp0"
set "LOG=%~dp0checkpoint_log.txt"
where git >nul 2>&1 || ( echo %date% %time%  SKIP: git not on PATH>>"%LOG%" & exit /b 0 )
git rev-parse --is-inside-work-tree >nul 2>&1 || ( echo %date% %time%  SKIP: not a git repo>>"%LOG%" & exit /b 0 )
set DIRTY=0
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set DIRTY=%%i
if "%DIRTY%"=="0" ( echo %date% %time%  clean - nothing to commit>>"%LOG%" & exit /b 0 )
git add -A
git commit -m "Nightly checkpoint %date% %time% (auto, no deploy)" >>"%LOG%" 2>&1
echo %date% %time%  committed %DIRTY% change^(s^)>>"%LOG%"
exit /b 0
