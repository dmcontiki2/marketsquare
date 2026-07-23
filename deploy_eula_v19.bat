@echo off
REM deploy_eula_v19.bat - one-shot targeted deploy of EULA v1.9 (23 Jul 2026)
REM Does: clears stale git lock -> commits v1.9 changes -> ships terms.html + index.html -> verifies.
REM Logs everything to deploy_eula_v19.log. Safe to re-run.
setlocal
set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set LOG=%PROJECT%\deploy_eula_v19.log
cd /d "%PROJECT%"

echo ==== EULA v1.9 targeted deploy %DATE% %TIME% ==== > "%LOG%"

echo [1/6] clear stale git lock (0-byte, from crashed 04:41 auto-commit) >> "%LOG%"
if exist "%PROJECT%\.git\index.lock" del /f "%PROJECT%\.git\index.lock" >> "%LOG%" 2>&1
if exist "%PROJECT%\_to_delete_gitlock" del /f "%PROJECT%\_to_delete_gitlock" >> "%LOG%" 2>&1

echo [2/6] git commit v1.9 changes >> "%LOG%"
git add -A >> "%LOG%" 2>&1
git commit -m "EULA v1.9 published (pre-counsel, David-directed): not-a-referral 2.6, Reference Library 8.10, local-laws 13.5, Country Schedules UK/US/AU; terms.html + embedded gate copy; register/canon v1.9; rollback tag ship-20260723-eulav19" >> "%LOG%" 2>&1

echo [3/6] scp terms.html >> "%LOG%"
scp -o BatchMode=yes -o ConnectTimeout=20 "%PROJECT%\terms.html" %SERVER%:%REMOTE%/terms.html >> "%LOG%" 2>&1
if errorlevel 1 (echo FAIL: terms.html scp >> "%LOG%" & goto :done)

echo [4/6] scp marketsquare.html as index.html >> "%LOG%"
scp -o BatchMode=yes -o ConnectTimeout=20 "%PROJECT%\marketsquare.html" %SERVER%:%REMOTE%/index.html >> "%LOG%" 2>&1
if errorlevel 1 (echo FAIL: index.html scp >> "%LOG%" & goto :done)

echo [5/6] server-side sentinel check >> "%LOG%"
ssh -n -o BatchMode=yes -o ConnectTimeout=20 %SERVER% "grep -c 'Version 1.9' %REMOTE%/terms.html %REMOTE%/index.html && grep -c 'Schedule C' %REMOTE%/terms.html" >> "%LOG%" 2>&1

echo [6/6] done >> "%LOG%"
echo DEPLOY-EULA-V19-COMPLETE >> "%LOG%"
:done
echo ==== end %TIME% ==== >> "%LOG%"
endlocal
exit
