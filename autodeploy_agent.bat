@echo off
:: ============================================================================
::  autodeploy_agent.bat  --  AUTODEPLOY-AGENT-1 (RUL-092, 3 Sep 2026)
::  Runs every 20 min from Task Scheduler (register_autodeploy_agent.bat).
::  Claude asks for a deploy by writing a flag from any session:
::     MarketSquare\DEPLOY_REQUEST.flag     -> gate + ship MarketSquare (nightly_tsl.bat)
::     MarketSquare\CL_DEPLOY_REQUEST.flag  -> ship CityLauncher (deploy_citylauncher.bat UNATTENDED)
::  BLOCKED gate  = flag stays, retried next tick ("wait out the block, redeploy").
::  SHIPPED / FAILED = flag renamed to DEPLOY_RESULT.txt with the verdict.
::  No flag = nothing happens. Never touches the server directly: MarketSquare ships
::  only by publishing the deploy ref (ONE DEPLOY, RG-0023); CityLauncher by its own bat.
:: ============================================================================
setlocal
cd /d "%~dp0"
set "LOG=%~dp0autodeploy_agent_log.txt"
set "REQ=%~dp0DEPLOY_REQUEST.flag"
set "CLREQ=%~dp0CL_DEPLOY_REQUEST.flag"
set "RESULT=%~dp0DEPLOY_RESULT.txt"
set "CLRESULT=%~dp0CL_DEPLOY_RESULT.txt"

if not exist "%REQ%" if not exist "%CLREQ%" exit /b 0

call "%~dp0git_unlock.bat" >nul 2>&1

:: ---------------- MarketSquare ----------------
if exist "%REQ%" (
    echo %date% %time%  REQUEST seen: >>"%LOG%"
    type "%REQ%" >>"%LOG%"
    if exist "%~dp0TSL_READY.flag" del /q "%~dp0TSL_READY.flag" >nul 2>&1
    call "%~dp0nightly_tsl.bat" >>"%LOG%" 2>&1
    set "RC=%errorlevel%"
    if exist "%~dp0TSL_READY.flag" (
        findstr /b /c:"BLOCKED" "%~dp0TSL_READY.flag" >nul 2>&1
        if not errorlevel 1 (
            echo %date% %time%  BLOCKED - request kept, retry next tick >>"%LOG%"
            goto :cl
        )
        findstr /b /c:"FAILED" "%~dp0TSL_READY.flag" >nul 2>&1
        if not errorlevel 1 (
            > "%RESULT%" echo FAILED %date% %time% - see autodeploy_agent_log.txt / nightly_tsl_log.txt
            type "%REQ%" >>"%RESULT%"
            del /q "%REQ%" >nul 2>&1
            echo %date% %time%  FAILED - request closed >>"%LOG%"
            goto :cl
        )
    )
    > "%RESULT%" echo SHIPPED %date% %time% rc=%RC%
    type "%REQ%" >>"%RESULT%"
    del /q "%REQ%" >nul 2>&1
    echo %date% %time%  SHIPPED rc=%RC% - request closed >>"%LOG%"
)

:cl
:: ---------------- CityLauncher ----------------
if exist "%CLREQ%" (
    echo %date% %time%  CL REQUEST seen: >>"%LOG%"
    type "%CLREQ%" >>"%LOG%"
    set "UNATTENDED=1"
    call "%~dp0..\CityLauncher\deploy_citylauncher.bat" <nul >>"%LOG%" 2>&1
    set "CLRC=%errorlevel%"
    set "UNATTENDED="
    if "%CLRC%"=="0" (
        > "%CLRESULT%" echo SHIPPED %date% %time%
        type "%CLREQ%" >>"%CLRESULT%"
        del /q "%CLREQ%" >nul 2>&1
        echo %date% %time%  CL SHIPPED - request closed >>"%LOG%"
    ) else (
        echo %date% %time%  CL FAILED rc=%CLRC% - request kept, retry next tick >>"%LOG%"
    )
)
exit /b 0
