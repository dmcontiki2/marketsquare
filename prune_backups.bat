@echo off
:: prune_backups.bat - tidy the backups\ folder ON DEMAND (no fresh pull/push).
:: Applies the same retention as the nightly: keep 7 daily / 4 weekly / monthly,
:: remove redundant intermediate folders. ONLY touches dated YYYY-MM-DD_HHMM archives
:: - your loose files (marketsquare.db, super-photos, etc.) are never touched.
:: Shows a preview first, then asks before deleting.
cd /d "%~dp0"
set "PYEXE=python"
where python >nul 2>&1 || set "PYEXE=py"
echo ============================================================
echo   Backups tidy - PREVIEW (nothing deleted yet)
echo ============================================================
%PYEXE% "%~dp0backup_retention.py" "%~dp0backups"
echo.
choice /m "Apply this and delete the PRUNE items above"
if errorlevel 2 ( echo  Cancelled - nothing was deleted. & pause & exit /b 0 )
echo.
%PYEXE% "%~dp0backup_retention.py" "%~dp0backups" --apply
echo.
echo  Done.
pause
