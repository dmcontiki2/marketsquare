@echo off
title MarketSquare - Release (go live)
color 0A
:: ════════════════════════════════════════════════════════════════════════════
::  release.bat  ·  "GO LIVE"
::
::  Publishes your CURRENT committed code as the live release. It pushes the
::  commit to the mirror's "deploy" ref; the server (set up once by
::  activate_autodeploy.bat) notices within ~2 minutes and deploys it, with a
::  health check and automatic rollback if the app does not come up.
::
::  This replaces running the full deploy_marketsquare.bat. It does no scp and
::  opens no long console - one push, the server does the rest.
::
::  TIP: commit your work first (the normal deploy_marketsquare.bat auto-commits;
::  if you are using release.bat instead, commit manually before running this).
:: ════════════════════════════════════════════════════════════════════════════

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239

cd /d "%PROJECT%" || (echo  ERROR: project folder not found: %PROJECT% & pause & exit /b 1)

echo.
echo  Publishing current commit to the live "deploy" ref...
git log -1 --oneline
echo.
git push origin HEAD:deploy
if errorlevel 1 (
    echo.
    echo  ERROR: push failed. Nothing was released. Common causes:
    echo    - uncommitted changes ^(commit first^), or
    echo    - no network / auth to GitHub.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   RELEASE PUBLISHED - the server will deploy within ~2 minutes.
echo  ============================================================
echo.
echo   Watch it:   ssh %SERVER% "tail -f /var/log/marketsquare-deploy.log"
echo   Verify:     start "" "https://trustsquare.co/health"
echo.
echo   If the new build fails its health check, the server rolls back
echo   automatically and the previous release stays live.
echo.
pause
