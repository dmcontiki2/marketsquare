@echo off
title MarketSquare - Media Push (the media lane - binaries only, never code)
color 0B
setlocal EnableExtensions

:: ============================================================================
::  media_push.bat  -  THE MEDIA LANE  (DEPLOY-CONSOLIDATION-1, 2 Aug 2026)
::
::  Git ignores binary media (*.jpg *.png *.mp4, the Agency Playbook PDF, the
::  n8n email templates), so the mirror - and therefore the ONE deploy engine -
::  never carries them. This script is the single, hash-gated lane that ships
::  them: every section rides scripts/sync_assets.ps1 (remote md5s read once,
::  only CHANGED files upload - RG-0021).
::
::  RULES:
::   - Media only. This lane NEVER carries code (ms.js, *.py, index/admin html).
::     RG-0023 trips red if code sneaks in here.
::   - Rarely needed: run after adding/refreshing photos, videos, phone cards,
::     legal cards or email templates. Code releases NEVER need this.
:: ============================================================================

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set SYNC=powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1"

cd /d "%PROJECT%" || (echo  ERROR: project folder not found & pause & exit /b 1)

echo.
echo  ============================================================
echo   MEDIA PUSH  (hash-gated: only changed files upload)
echo   %DATE% %TIME%
echo  ============================================================

echo  [1/7] SUPER exemplar photos (assets\super to /static/super)...
%SYNC% -LocalDir "%PROJECT%\assets\super" -Filter *.jpg -RemoteDir %REMOTE%/static/super -Server %SERVER%

echo  [2/7] Feature/tutor videos (videos to /static/videos)...
%SYNC% -LocalDir "%PROJECT%\videos" -Filter *.mp4 -RemoteDir %REMOTE%/static/videos -Server %SERVER%

echo  [3/7] Email images - phone cards + heroes (CityLauncher to /static)...
set PHONESRC=C:\Users\David\Projects\CityLauncher\emailer\assets
if exist "%PHONESRC%" %SYNC% -LocalDir "%PHONESRC%" -Filter "phone_*.jpg" -RemoteDir %REMOTE%/static -Server %SERVER%
:: EMAIL-HERO-1 (2 Aug 2026): the template hero/illustration images were in NO lane - 404 live.
if exist "%PHONESRC%" %SYNC% -LocalDir "%PHONESRC%" -Filter "email_*.jpg" -RemoteDir %REMOTE%/static -Server %SERVER%
if exist "%PHONESRC%" %SYNC% -LocalDir "%PHONESRC%" -Filter "email_*.png" -RemoteDir %REMOTE%/static -Server %SERVER%

echo  [4/7] Legal must-have cards (PNGs per country)...
for %%C in (ZA US UK AU) do (
    if exist "%PROJECT%\assets\legal-must-haves\%%C" %SYNC% -LocalDir "%PROJECT%\assets\legal-must-haves\%%C" -Filter *.png -RemoteDir %REMOTE%/static/legal-must-haves/%%C -Server %SERVER%
)

echo  [5/7] Agency Playbook PDF...
if exist "%PROJECT%\TrustSquare_Agency_Playbook.pdf" %SYNC% -LocalDir "%PROJECT%" -Filter TrustSquare_Agency_Playbook.pdf -RemoteDir %REMOTE%/static -Server %SERVER%

echo  [6/7] n8n email templates (untracked HTML)...
if exist "%PROJECT%\n8n\email_templates" %SYNC% -LocalDir "%PROJECT%\n8n\email_templates" -Filter *.html -RemoteDir %REMOTE%/email_templates -Server %SERVER%

echo  [7/7] Permissions + CDN purge + video re-warm...
ssh -n -o ConnectTimeout=15 %SERVER% "chmod 755 %REMOTE%/static/super %REMOTE%/static/videos %REMOTE%/static/legal-must-haves %REMOTE%/static/legal-must-haves/* 2>/dev/null; chmod 644 %REMOTE%/static/super/*.jpg %REMOTE%/static/videos/*.mp4 %REMOTE%/static/legal-must-haves/*/*.png %REMOTE%/static/phone_*.jpg 2>/dev/null; true"
ssh -n -o ConnectTimeout=15 %SERVER% "cd %REMOTE% && KEY=$(grep -oP '(?<=^ADMIN_KEY=).*' .env 2>/dev/null); curl -sf -m 20 -X POST -H 'x-admin-key: '$KEY http://localhost:8000/admin/purge-cache >/dev/null 2>&1" && echo   [OK] CDN purge requested || echo   [WARN] CDN purge failed - purge manually if stale
ssh -n -o ConnectTimeout=15 %SERVER% "test -f %REMOTE%/warm_videos.sh && bash %REMOTE%/warm_videos.sh" && echo   [OK] videos re-warmed || echo   [WARN] video warm skipped/failed

echo.
echo  ============================================================
echo   MEDIA PUSH COMPLETE
echo  ============================================================
pause
exit /b 0
