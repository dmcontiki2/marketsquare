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

set "HQ=%~dp0host_queue"

:: HOST-QUEUE-1 (RUL-095): permission-backed requests Claude cannot run from the sandbox
:: (git push with David's credentials, DB-writing bats). Allowlist + permission line enforced
:: by the worker; results in host_queue\done\. Runs BEFORE deploys so a push lands first.
if exist "%HQ%\*.req" (
    call "%~dp0git_unlock.bat" >nul 2>&1
    python "%~dp0scripts\host_queue_worker.py" >>"%LOG%" 2>&1
)

:: ---------------------------------------------------------------------------
:: FW-SELFHEAL-SCHEDULED-1 (5 Sep 2026, maintenance loop). RG-0099 (SSH lockout)
:: rotted on 26 Aug, 2 Sep and again today: the Hetzner SSH allowlist held a dead
:: home IP after a router reset, so port 22 timed out for BOTH David and every
:: session. The cure existed the whole time (hetzner_fw_selfheal.py, RG-0188 proves
:: it is executable) -- NOTHING RAN IT. A remedy that only a human remembers is not
:: a fix, it is a chore. This host shares the egress the allowlist must name, and
:: this agent already ticks every 20 min, so the healer belongs here: idempotent,
:: a no-op when the IP is already right, and it can never widen access to anyone
:: but the machine that ran it. Deliberately BEFORE the no-request early exit, and
:: its exit code is discarded so a Hetzner API hiccup can never block a deploy.
if exist "%~dp0.secrets\hetzner_token.txt" (
    python "%~dp0scripts\hetzner_fw_selfheal.py" >>"%~dp0fw_selfheal_log.txt" 2>&1
    ver >nul
)

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
