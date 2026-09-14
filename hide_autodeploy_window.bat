@echo off
:: hide_autodeploy_window.bat -- DOUBLE-CLICK ONCE.
:: Re-registers \MarketSquare\AutodeployAgent so it runs through run_hidden.vbs
:: instead of calling autodeploy_agent.bat directly. Same schedule (every 20 min),
:: same script, same limited run level -- the ONLY change is that the console window
:: no longer flashes on screen each tick. The heartbeat file and the logs are
:: unchanged, so you can still prove the agent ran.
net session >nul 2>&1 || (
    echo Requesting administrator rights...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)
set "TASK=\MarketSquare\AutodeployAgent"
set "VBS=%~dp0run_hidden.vbs"
set "SCRIPT=%~dp0autodeploy_agent.bat"
echo  ============================================================
echo   Re-registering: %TASK%
echo   Runs : wscript run_hidden.vbs -^> autodeploy_agent.bat
echo   When : every 20 minutes, hidden
echo  ============================================================
schtasks /Create /TN "%TASK%" /TR "wscript.exe \"%VBS%\" \"%SCRIPT%\"" /SC MINUTE /MO 20 /F /RL LIMITED
if errorlevel 1 ( echo ERROR - registration failed. & pause & exit /b 1 )
echo.
echo   OK - the window is hidden from the next tick onwards.
echo   prove it ran : type "%~dp0host_queue\agent_heartbeat.txt"
echo   run now      : schtasks /Run /TN "%TASK%"
echo   undo         : double-click register_autodeploy_agent.bat
pause
