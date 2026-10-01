@echo off
:: nightly_checkpoint.bat - UNATTENDED nightly git checkpoint (no deploy).
:: Run by Windows Task Scheduler. Banks the working tree into git so it never
:: drifts days behind again. LOCAL git only - nothing is scp'd, nothing goes live.
cd /d "%~dp0"
set "LOG=%~dp0checkpoint_log.txt"
where git >nul 2>&1 || ( echo %date% %time%  SKIP: git not on PATH>>"%LOG%" & exit /b 0 )
git rev-parse --is-inside-work-tree >nul 2>&1 || ( echo %date% %time%  SKIP: not a git repo>>"%LOG%" & exit /b 0 )
REM GIT-LOCK-6 (25 Sep 2026, DW-154): sweep stale locks EVERY night, before the clean-tree
REM early exit. On 25 Sep the tree was clean, so the old order exited before git_unlock.bat ran
REM and a HEAD.lock stranded by a sandbox commit at 02:01 survived to the morning watch.
call "%~dp0git_unlock.bat"
set DIRTY=0
for /f %%i in ('git status --porcelain ^| find /c /v ""') do set DIRTY=%%i
if "%DIRTY%"=="0" ( echo %date% %time%  clean - nothing to commit>>"%LOG%" & goto :take_in )
git add -A
git commit -m "Nightly checkpoint %date% %time% (auto, no deploy)" >>"%LOG%" 2>&1
echo %date% %time%  committed %DIRTY% change^(s^)>>"%LOG%"
:take_in
:: SYNC-ORIGIN-1 (RUL-193): take in what the cloud shipped, so the laptop never drifts days behind.
:: Merge only; a conflict is aborted, logged and left in SYNC_CONFLICT.txt for the next session. Never pushes.
set "PYEXE=python"
where python >nul 2>&1 || set "PYEXE=py"
%PYEXE% "%~dp0scripts\sync_origin.py" >>"%LOG%" 2>&1
if errorlevel 1 ( echo %date% %time%  SYNC STOP - see SYNC_CONFLICT.txt; main NOT mirrored>>"%LOG%" & exit /b 0 )
:: ...and mirror the laptop's own commits to GitHub main, so cloud sessions start from what the laptop holds.
:: main only -- never deploy: this is a mirror, not a release. The pre-push hook refuses any overwrite.
git push -q origin HEAD:main >>"%LOG%" 2>&1 && echo %date% %time%  main mirrored to GitHub>>"%LOG%"
exit /b 0
