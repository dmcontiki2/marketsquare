@echo off
:: see_predeploy_check.bat - run the pre-deploy change scan and KEEP the window open.
:: Double-click this (not the .py) when you want to read the report by hand.
:: Purely a viewer - it does NOT deploy anything.
cd /d "%~dp0"
echo  Running pre-deploy change scan...
echo.
python "%~dp0predeploy_check.py" || py "%~dp0predeploy_check.py"
echo.
echo  ------------------------------------------------------------
echo   Scan complete. Full history is in deploy_audit.log
echo  ------------------------------------------------------------
pause
