@echo off
:: register_autodeploy_agent.bat -- registers AUTODEPLOY-AGENT-1 (RUL-092). Run ONCE, as admin.
net session >nul 2>&1 || (
    echo Requesting administrator rights...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
set "TASK=\MarketSquare\AutodeployAgent"
set "SCRIPT=%~dp0autodeploy_agent.bat"
schtasks /Create /TN "%TASK%" /TR "\"%SCRIPT%\"" /SC MINUTE /MO 20 /F /RL LIMITED
if errorlevel 1 ( echo ERROR - registration failed. & pause & exit /b 1 )
echo.
echo   OK - %TASK% runs every 20 minutes.
echo   Claude ships by writing DEPLOY_REQUEST.flag / CL_DEPLOY_REQUEST.flag; nothing happens otherwise.
echo   check it : schtasks /Query /TN "%TASK%"
echo   run now  : schtasks /Run   /TN "%TASK%"
echo   log      : autodeploy_agent_log.txt
pause
