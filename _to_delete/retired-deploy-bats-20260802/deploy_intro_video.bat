@echo off
:: deploy_intro_video.bat - targeted single-file ship: the introductions video only
:: Built 12 Jul 2026 by Claude (/ship). Mirrors deploy_marketsquare.bat conventions:
:: ssh -n everywhere (7 Jul stdin lesson), server-side backup, CF purge, md5 self-check.
set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare

echo  [1/4] Server-side backup of the live introduction.mp4...
ssh -n -o ConnectTimeout=15 %SERVER% "cp %REMOTE%/static/videos/introduction.mp4 %REMOTE%/static/videos/introduction.mp4.bak-%date:~-4%%date:~-7,2%%date:~-10,2% 2>/dev/null || true"

echo  [2/4] Uploading new introduction.mp4...
scp "%PROJECT%\videos\introduction.mp4" %SERVER%:%REMOTE%/static/videos/introduction.mp4
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed. Check SSH connection.
    pause
    exit /b 1
)
ssh -n %SERVER% "chmod 644 %REMOTE%/static/videos/introduction.mp4"

echo  [3/4] Purging Cloudflare cache...
ssh -n %SERVER% "curl -sf -m 20 -X POST http://localhost:8000/admin/purge-cache >nul 2>&1" && echo   [OK] purge requested || echo   [WARN] purge failed - purge manually if stale

echo  [4/4] Self-check: served bytes vs origin...
ssh -n %SERVER% "o=$(md5sum %REMOTE%/static/videos/introduction.mp4 | cut -d\" \" -f1); s=$(curl -s --max-time 25 https://trustsquare.co/static/videos/introduction.mp4?vchk=$RANDOM | md5sum | cut -d\" \" -f1); if [ \"$o\" = \"$s\" ]; then echo \"   [OK] served bytes match origin - CDN fresh\"; else echo \"   [FAIL] served differs - CDN stale, purge manually\"; fi"
echo  Done. Tell Claude to run the live smoke test.
