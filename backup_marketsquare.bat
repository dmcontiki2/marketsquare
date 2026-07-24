@echo off
:: backup_marketsquare.bat - MarketSquare belt-and-braces backup (NATIVE Windows).
:: The Cowork sandbox cannot run this: git push needs your GitHub credentials and the
:: DB pull needs your SSH key - both live on THIS machine. So it runs here.
::   [1] push code to the GitHub mirror
::   [2] pull a CONSISTENT snapshot of the live SQLite DB off the Hetzner server
::   [3] zip a dated archive under backups\
::   [4] integrity-check the pulled DB (via Python stdlib - no sqlite3.exe needed)
::   [5] retention: keep 7 daily / 4 weekly / monthly; remove redundant folders
:: Non-destructive on failure: retention runs ONLY after a good archive this run.
:: Writes backup_report.txt so Claude can confirm what got protected. No creds stored.
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "SERVER=root@178.104.73.239"
set "REMOTE=/var/www/marketsquare"
set "DB=marketsquare.db"
set "REPORT=%~dp0backup_report.txt"

set "PYEXE=python"
where python >nul 2>&1 || set "PYEXE=py"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set "STAMP=%%i"
set "OUTDIR=%~dp0backups\%STAMP%"
if not exist "%~dp0backups" mkdir "%~dp0backups"
if not exist "%OUTDIR%" mkdir "%OUTDIR%"

> "%REPORT%" echo MarketSquare backup - %STAMP%
>>"%REPORT%" echo ============================================================
echo ============================================================
echo   MarketSquare belt-and-braces backup   %STAMP%
echo ============================================================

:: ---- [1] CODE -> GitHub mirror ----
echo.
echo [1/5] Pushing code to the GitHub mirror...
if exist ".git\index.lock" del /f /q ".git\index.lock"
if exist ".git\HEAD.lock"  del /f /q ".git\HEAD.lock"
set "AHEAD=?"
for /f %%c in ('git rev-list --count origin/main..HEAD 2^>nul') do set "AHEAD=%%c"
git push origin main
if errorlevel 1 (
   echo   [FAIL] git push failed - code NOT mirrored this run ^(check GitHub auth^).
   >>"%REPORT%" echo [1] CODE: PUSH FAILED - code not mirrored. Check GitHub credentials.
) else (
   echo   [OK] pushed ^(was !AHEAD! commit^(s^) ahead of the mirror^).
   >>"%REPORT%" echo [1] CODE: pushed to github.com/dmcontiki2/marketsquare ^(!AHEAD! commit^(s^)^).
)

:: ---- [2] SERVER DATA -> consistent DB snapshot, then pull ----
echo.
echo [2/5] Snapshotting + pulling the live database...
set "SNAP=/tmp/ms_%STAMP%.db"
ssh -o ConnectTimeout=20 %SERVER% "sqlite3 %REMOTE%/%DB% '.backup %SNAP%'"
if errorlevel 1 (
   echo   [FAIL] server snapshot failed - business data NOT backed up this run.
   >>"%REPORT%" echo [2] DB: FAILED to snapshot on server - business data NOT backed up.
   goto :archive
)
scp %SERVER%:%SNAP% "%OUTDIR%\%DB%"
if errorlevel 1 (
   echo   [FAIL] scp failed - DB NOT pulled.
   >>"%REPORT%" echo [2] DB: snapshot made on server but SCP failed - business data NOT backed up.
) else (
   for %%A in ("%OUTDIR%\%DB%") do set "DBSIZE=%%~zA"
   echo   [OK] pulled marketsquare.db  ^(!DBSIZE! bytes^)  -^> backups\%STAMP%\
   >>"%REPORT%" echo [2] DB: pulled marketsquare.db snapshot ^(!DBSIZE! bytes^) to backups\%STAMP%\
)
ssh %SERVER% "rm -f %SNAP%" 2>nul

ssh -o ConnectTimeout=20 %SERVER% "test -d %REMOTE%/uploads && echo HAS_UPLOADS" | find "HAS_UPLOADS" >nul
if not errorlevel 1 (
   echo   pulling uploads dir...
   scp -r %SERVER%:%REMOTE%/uploads "%OUTDIR%\uploads" >nul 2>&1 && >>"%REPORT%" echo      + uploads/ dir pulled from server.
) else (
   >>"%REPORT%" echo      NOTE: no %REMOTE%/uploads dir found - assets likely in object storage ^(Scaleway/R2^); NOT in this archive.
)

:archive
:: ---- [3] ARCHIVE ----
echo.
echo [3/5] Zipping the dated archive...
set "ZIP=%~dp0backups\%STAMP%.zip"
powershell -NoProfile -Command "Compress-Archive -Path '%OUTDIR%\*' -DestinationPath '%ZIP%' -Force" 2>nul
if exist "%ZIP%" (
   for %%A in ("%ZIP%") do set "ZSIZE=%%~zA"
   echo   [OK] backups\%STAMP%.zip  ^(!ZSIZE! bytes^)
   >>"%REPORT%" echo [3] ARCHIVE: backups\%STAMP%.zip ^(!ZSIZE! bytes^)
) else (
   echo   [WARN] no zip written ^(nothing was pulled to archive^).
   >>"%REPORT%" echo [3] ARCHIVE: none written ^(no data pulled^).
)

:: ---- [4] INTEGRITY ----
echo.
echo [4/5] Integrity-checking the pulled database...
if exist "%OUTDIR%\%DB%" (
   %PYEXE% "%~dp0backup_integrity.py" "%OUTDIR%\%DB%" > "%~dp0_integ.txt" 2>&1
   type "%~dp0_integ.txt"
   >>"%REPORT%" echo [4] INTEGRITY:
   type "%~dp0_integ.txt" >> "%REPORT%"
   del /f /q "%~dp0_integ.txt" 2>nul
) else (
   echo   [SKIP] no DB pulled to check.
   >>"%REPORT%" echo [4] INTEGRITY: skipped ^(no DB pulled^).
)

:: ---- [5] RETENTION (only after a good archive this run) ----
echo.
echo [5/5] Applying retention (7 daily / 4 weekly / monthly)...
if exist "%ZIP%" (
   %PYEXE% "%~dp0backup_retention.py" "%~dp0backups" --apply > "%~dp0_ret.txt" 2>&1
   type "%~dp0_ret.txt"
   >>"%REPORT%" echo [5] RETENTION:
   type "%~dp0_ret.txt" >> "%REPORT%"
   del /f /q "%~dp0_ret.txt" 2>nul
) else (
   echo   [SKIP] no archive written this run - retention skipped ^(never prune on a failed run^).
   >>"%REPORT%" echo [5] RETENTION: skipped ^(no archive this run - nothing pruned^).
)

>>"%REPORT%" echo ------------------------------------------------------------
>>"%REPORT%" echo Code mirror = off-machine ^(GitHub^). DB archive = local backups\ folder.
>>"%REPORT%" echo NOT covered: object-storage assets ^(if any^). Loose non-archive files are left as-is.
echo.
echo ============================================================
echo   Backup run complete.   Report: backup_report.txt
echo ============================================================
endlocal
pause
