@echo off
title TrustSquare - Frontend Cache-Bust Deploy
cd /d C:\Users\David\Projects\MarketSquare
echo ============================================================
echo  Frontend deploy  (bump FIRST, assets, HTML, purge, then VERIFY delivery)
echo ============================================================
echo [0/5] Bumping cache-buster version (ms.js?v / ms.css?v) in marketsquare.html...
powershell -NoProfile -Command "$f='C:\Users\David\Projects\MarketSquare\marketsquare.html'; $c=Get-Content -Raw -LiteralPath $f; $c=[regex]::Replace($c,'ms\.js\?v=(\d+)',{'ms.js?v='+([int]$args[0].Groups[1].Value+1)}); $c=[regex]::Replace($c,'ms\.css\?v=(\d+)',{'ms.css?v='+([int]$args[0].Groups[1].Value+1)}); Set-Content -NoNewline -LiteralPath $f -Value $c; Write-Host ('  bumped -> ms.js?v=' + [regex]::Match($c,'ms\.js\?v=(\d+)').Groups[1].Value + '  ms.css?v=' + [regex]::Match($c,'ms\.css\?v=(\d+)').Groups[1].Value)"
if %errorlevel% neq 0 (
    echo  ERROR: version bump failed. Aborting so we do not ship a stale-cached asset.
    pause
    exit /b 1
)
echo [1/5] ms.js  -^> /static/ms.js
scp ms.js root@178.104.73.239:/var/www/marketsquare/static/ms.js
echo [2/5] ms.css -^> /static/ms.css
scp ms.css root@178.104.73.239:/var/www/marketsquare/static/ms.css
echo [3/5] marketsquare.html -^> index.html
scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
echo [4/5] Purging Cloudflare edge cache ...
curl.exe -s -X POST https://trustsquare.co/admin/purge-cache
echo.
echo [5/5] Verifying the NEW version actually reached users (catches a silent stale-serve)...
powershell -NoProfile -Command "$f='C:\Users\David\Projects\MarketSquare\marketsquare.html'; $local=[regex]::Match((Get-Content -Raw -LiteralPath $f),'ms\.js\?v=(\d+)').Groups[1].Value; try { $r=Invoke-WebRequest -UseBasicParsing -Uri ('https://trustsquare.co/?nocache=' + (Get-Random)); $live=[regex]::Match($r.Content,'ms\.js\?v=(\d+)').Groups[1].Value } catch { $live='FETCH_FAILED' }; if ($local -eq $live) { Write-Host ('   [OK] live index now references ms.js?v=' + $local + ' - browsers WILL refetch the new build') } else { Write-Host ('   [FAIL] live index references v=' + $live + ' but you built v=' + $local + ' - index upload did not reach users; re-run this script') }"
echo.
echo DONE. If [5/5] shows [OK], the fix is live for everyone. Window closes in 25s.
timeout /t 25 /nobreak >nul
