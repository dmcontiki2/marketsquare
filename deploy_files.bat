@echo off
REM deploy_files.bat - reusable TARGETED deploy (born from the EULA v1.9 ship, 23 Jul 2026).
REM Ships ONLY the files listed in deploy_files.txt (one per line; use "local|remote" if the
REM server name differs, e.g. marketsquare.html|index.html). Then: cache purge + video re-warm
REM + sentinel check. Everything logs to deploy_files.log. Safe to re-run.
setlocal enabledelayedexpansion
set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set LOG=%PROJECT%\deploy_files.log
set LIST=%PROJECT%\deploy_files.txt
cd /d "%PROJECT%"

echo ==== targeted deploy %DATE% %TIME% ==== > "%LOG%"

if not exist "%LIST%" (
  echo FAIL: %LIST% not found - list the files to ship, one per line >> "%LOG%"
  goto :done
)

echo [1/5] clear stale git lock if present >> "%LOG%"
if exist "%PROJECT%\.git\index.lock" del /f "%PROJECT%\.git\index.lock" >> "%LOG%" 2>&1

echo [2/5] git commit >> "%LOG%"
git add -A >> "%LOG%" 2>&1
git commit -m "Targeted deploy %DATE% %TIME% (deploy_files.bat): see deploy_files.txt" >> "%LOG%" 2>&1

echo [3/5] ship listed files >> "%LOG%"
set FAILED=0
for /f "usebackq tokens=1,2 delims=| eol=#" %%a in ("%LIST%") do (
  set DEST=%%b
  if "!DEST!"=="" set DEST=%%a
  echo   %%a -^> !DEST! >> "%LOG%"
  scp -o BatchMode=yes -o ConnectTimeout=20 "%PROJECT%\%%a" %SERVER%:%REMOTE%/!DEST! >> "%LOG%" 2>&1
  if errorlevel 1 (echo   FAIL: %%a >> "%LOG%" & set FAILED=1)
)
if "%FAILED%"=="1" (echo ABORT: one or more files failed - fix and re-run >> "%LOG%" & goto :done)

echo [4/5] Cloudflare purge + tutor-video re-warm >> "%LOG%"
ssh -n -o BatchMode=yes -o ConnectTimeout=20 %SERVER% "curl -sf -m 20 -X POST http://localhost:8000/admin/purge-cache >/dev/null 2>&1 && echo purge OK || echo purge WARN" >> "%LOG%" 2>&1
ssh -n -o BatchMode=yes -o ConnectTimeout=20 %SERVER% "bash %REMOTE%/warm_videos.sh >/dev/null 2>&1 && echo warm OK || echo warm WARN" >> "%LOG%" 2>&1

echo [5/5] sentinel: list shipped files on server with sizes >> "%LOG%"
for /f "usebackq tokens=1,2 delims=| eol=#" %%a in ("%LIST%") do (
  set DEST=%%b
  if "!DEST!"=="" set DEST=%%a
  ssh -n -o BatchMode=yes -o ConnectTimeout=20 %SERVER% "ls -la %REMOTE%/!DEST!" >> "%LOG%" 2>&1
)
echo DEPLOY-TARGETED-COMPLETE >> "%LOG%"
:done
echo ==== end %TIME% ==== >> "%LOG%"
endlocal
exit
