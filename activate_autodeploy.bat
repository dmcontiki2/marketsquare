@echo off
title MarketSquare - Activate Auto-Deploy (one time)
color 0B
:: ════════════════════════════════════════════════════════════════════════════
::  activate_autodeploy.bat  ·  RUN ONCE
::
::  This is the SINGLE manual step to switch on hands-free deploys. It:
::    1. commits + pushes your project to the GitHub mirror (so the server can
::       pull the auto-deploy files)
::    2. copies the installer to the server and runs it once (installs a systemd
::       timer that polls the mirror every 2 min and deploys when you publish)
::
::  It deploys NOTHING by itself. After this, "go live" = double-click release.bat
::  (or, from any session, python deploy_web.py). See ACTIVATION.md.
::
::  Uses your existing SSH key on THIS machine. No secret ever leaves your PC.
:: ════════════════════════════════════════════════════════════════════════════

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239

echo.
echo  ============================================================
echo   ACTIVATE AUTO-DEPLOY  (one-time setup)
echo  ============================================================
echo.

cd /d "%PROJECT%" || (echo  ERROR: project folder not found: %PROJECT% & pause & exit /b 1)

:: -- Step 1: make sure the mirror has the auto-deploy files --------------------
echo  [1/3] Committing and pushing the project to the mirror...
call "%~dp0git_unlock.bat"
git add -A
git commit -m "Activate Phase 3 auto-deploy (ops/autodeploy)" 1>nul 2>nul
git push origin HEAD:main
if errorlevel 1 (
    echo  WARNING: git push to main reported a problem. If it says "up to date", that is fine.
    echo           If it failed for another reason, fix it and re-run - the server needs the
    echo           ops\autodeploy files on the mirror before it can install them.
)
echo.

:: -- Step 2: copy the installer to the server ---------------------------------
echo  [2/3] Copying the installer to the server...
scp "%PROJECT%\ops\autodeploy\install_autodeploy.sh" %SERVER%:/tmp/install_autodeploy.sh
if errorlevel 1 (
    echo  ERROR: scp failed. Check your SSH connection to %SERVER%.
    pause
    exit /b 1
)
echo.

:: -- Step 3: run the installer once -------------------------------------------
echo  [3/3] Installing the auto-deploy timer on the server...
ssh %SERVER% "bash /tmp/install_autodeploy.sh"
if errorlevel 1 (
    echo  ERROR: the installer reported a problem. Read its output above.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   AUTO-DEPLOY INSTALLED
echo  ============================================================
echo.
echo   The server now checks the mirror every 2 minutes.
echo   To push your first release live, double-click:  release.bat
echo   (or from any session:  python deploy_web.py)
echo.
echo   Watch a deploy:  ssh %SERVER% "tail -f /var/log/marketsquare-deploy.log"
echo.
pause
