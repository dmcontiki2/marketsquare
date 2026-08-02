@echo off
title MarketSquare · Deploy Collectables Tutor Video
color 0A

:: ════════════════════════════════════════════════════════════
::  deploy_collectables_video.bat   (v2 - hardened)
::  Uploads ONLY the Collectables tutor video to Hetzner and
::  purges the Cloudflare cache so the new cut shows live.
::  Single static file -- no service restart, no backend change.
::  File deployed: videos\collectables-advert-howto.mp4  (v2-FINAL, 57s)
::  Server path:   /var/www/marketsquare/static/videos/collectables-advert-howto.mp4
::  NOTE: ssh uses -n (stdin from NUL) so the verify/purge steps
::        cannot hang waiting on console input.
:: ════════════════════════════════════════════════════════════

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set LOCALVID=%PROJECT%\videos\collectables-advert-howto.mp4
set REMOTEDIR=/var/www/marketsquare/static/videos
set REMOTEVID=%REMOTEDIR%/collectables-advert-howto.mp4
set SSHOPTS=-o BatchMode=yes -o ConnectTimeout=15

echo.
echo  ============================================================
echo   Deploying Collectables tutor video to trustsquare.co
echo   %DATE% %TIME%
echo  ============================================================
echo.

if not exist "%LOCALVID%" (
    echo  ERROR: %LOCALVID% not found.
    pause
    exit /b 1
)
for %%A in ("%LOCALVID%") do echo  Local file: %%~nxA  (%%~zA bytes)
echo.

echo  [1/3] Uploading video (~4.8 MB)...
ssh -n %SSHOPTS% %SERVER% "mkdir -p %REMOTEDIR%"
scp %SSHOPTS% "%LOCALVID%" %SERVER%:%REMOTEVID%
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed. Check SSH connection / key.
    pause
    exit /b 1
)
echo  Done.
echo.

echo  [2/3] Verifying on server (size should be 4868905 bytes)...
ssh -n %SSHOPTS% %SERVER% "ls -l %REMOTEVID%"
echo.

echo  [3/3] Purging Cloudflare cache so the new video shows immediately...
ssh -n %SSHOPTS% %SERVER% "curl -s -m 20 -X POST http://localhost:8000/admin/purge-cache"
echo.
echo  Cloudflare purge requested (expect {"purged":true} above).
echo.

echo  ============================================================
echo   DEPLOY COMPLETE
echo  ============================================================
echo.
echo  Opening the live video (cache-busted) to verify...
timeout /t 2 /nobreak >nul
start "" "https://trustsquare.co/static/videos/collectables-advert-howto.mp4?v=%random%"
echo.
echo  Then open the app and tap Video Tutor on the Collectables feature.
echo.
echo  (You can close this window now -- the upload is already complete.)
pause
