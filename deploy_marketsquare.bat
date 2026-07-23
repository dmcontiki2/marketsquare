@echo off
title MarketSquare · Deploying to Server...
color 0A

:: ════════════════════════════════════════════════════════════
::  deploy_marketsquare.bat
::  MarketSquare · Deploy Script v3
::  Copies latest HTML + BEA files to Hetzner server
::  and VERIFIES each step completed successfully.
::  Place this file in: C:\Users\David\Projects\MarketSquare
::  Run whenever you want to push changes live.
::
::  Always save your working files as:
::    marketsquare.html        (buyer app)
::    marketsquare_admin.html  (admin tool)
::    bea_main.py              (BEA backend)
::  Version numbers live inside the file — not in the filename.
:: ════════════════════════════════════════════════════════════

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare

echo.
echo  ============================================================
echo   MARKETSQUARE  ^|  Deploying to trustsquare.co...
echo   %DATE% %TIME%
echo  ============================================================
echo.

:: ── Pre-flight: check all three files exist ───────────────
:: -- [0b] PRE-DEPLOY CHANGE SCAN (monitoring, added 9 Jul 2026) ----------------
:: Detective control for the multi-session concurrency gap: reports what is about
:: to go live + flags files another session may have changed since; logs every run
:: to deploy_audit.log. NON-FATAL BY DESIGN (same rule as the Step 7 auto-commit):
:: default warn mode never aborts. Set PREDEPLOY_MODE=strict to ABORT on a torn file.
echo  [0b] Pre-deploy change scan (monitoring)...
python "%PROJECT%\predeploy_check.py" || py "%PROJECT%\predeploy_check.py"
set SCANRC=%errorlevel%
if /I "%PREDEPLOY_MODE%"=="strict" if not "%SCANRC%"=="0" (
    echo  ABORT: pre-deploy scan flagged a dangerous change ^(strict mode^). See deploy_audit.log + DEPLOY_REVIEW flag.
    pause
    exit /b 1
)
echo.

echo  Checking local files...
if not exist "%PROJECT%\marketsquare.html" (
    echo  ERROR: marketsquare.html not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\marketsquare_admin.html" (
    echo  ERROR: marketsquare_admin.html not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\bea_main.py" (
    echo  ERROR: bea_main.py not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\assets\service-worker.js" (
    echo  ERROR: service-worker.js not found in %PROJECT%\assets
    pause
    exit /b 1
)
if not exist "%PROJECT%\ms.js" (
    echo  ERROR: ms.js not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\ms.css" (
    echo  ERROR: ms.css not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\auth.py" (
    echo  ERROR: auth.py not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\database.py" (
    echo  ERROR: database.py not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\storage.py" (
    echo  ERROR: storage.py not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\payments.py" (
    echo  ERROR: payments.py not found in %PROJECT%
    pause
    exit /b 1
)
if not exist "%PROJECT%\scripts\sync_assets.ps1" (
    echo  ERROR: scripts\sync_assets.ps1 not found - asset hash-sync helper missing.
    pause
    exit /b 1
)
echo  All required files found locally.
echo.

:: ── Step 0: Auto-bump cache-buster (?v=N) on ms.js + ms.css ──
:: The browser caches each ?v= URL forever (nginx 'immutable'), so a deploy only
:: reaches users when the version number changes. Bumped automatically here so it
:: is never a manual step. Only the buyer app loads ms.js / ms.css.
echo  [0/7] Bumping cache-buster version on ms.js and ms.css...
powershell -NoProfile -Command ^
  "$f = '%PROJECT%\marketsquare.html';" ^
  "$c = Get-Content -Raw -LiteralPath $f;" ^
  "$c = [regex]::Replace($c, 'ms\.js\?v=(\d+)', { 'ms.js?v=' + ([int]$args[0].Groups[1].Value + 1) });" ^
  "$c = [regex]::Replace($c, 'ms\.css\?v=(\d+)', { 'ms.css?v=' + ([int]$args[0].Groups[1].Value + 1) });" ^
  "Set-Content -NoNewline -LiteralPath $f -Value $c;" ^
  "$jsv = [regex]::Match($c, 'ms\.js\?v=(\d+)').Groups[1].Value;" ^
  "$cssv = [regex]::Match($c, 'ms\.css\?v=(\d+)').Groups[1].Value;" ^
  "Write-Host ('  ms.js -> v=' + $jsv + '   ms.css -> v=' + $cssv)"
if %errorlevel% neq 0 (
    echo  ERROR: version bump failed. Aborting so we do not ship a stale-cached asset.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 1: Deploy buyer app ──────────────────────────────
:: -- assets FIRST: ms.js + ms.css MUST land before the HTML that references ?v=N
:: -- otherwise Cloudflare pins the OLD js to the NEW version key (the 15-Jun cache bug).
echo  [1a/7] Uploading static assets FIRST - ms.js and ms.css...
scp "%PROJECT%\ms.js" %SERVER%:%REMOTE%/static/ms.js
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for ms.js. Check SSH connection.
    pause
    exit /b 1
)
scp "%PROJECT%\ms.css" %SERVER%:%REMOTE%/static/ms.css
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for ms.css. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

echo  [1/6] Deploying buyer app (marketsquare.html -^> index.html)...
scp "%PROJECT%\marketsquare.html" %SERVER%:%REMOTE%/index.html
REM legal pages (terms.html is GENERATED from eula_clean.html - regenerate before deploy if EULA changed)
scp "%PROJECT%\privacy.html" %SERVER%:%REMOTE%/privacy.html
scp "%PROJECT%\terms.html" %SERVER%:%REMOTE%/terms.html
scp "%PROJECT%\support.html" %SERVER%:%REMOTE%/support.html
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for buyer app. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 2: Deploy admin tool ─────────────────────────────
echo  [2/6] Deploying admin tool (marketsquare_admin.html -^> admin.html)...
scp "%PROJECT%\marketsquare_admin.html" %SERVER%:%REMOTE%/admin.html
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for admin tool. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3: Deploy service worker (Wishlist Web Push) ────
echo  [3/6] Deploying service worker (service-worker.js -^> service-worker.js)...
scp "%PROJECT%\assets\service-worker.js" %SERVER%:%REMOTE%/service-worker.js
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for service-worker.js. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3c: Deploy static assets (ms.js + ms.css -> /static/) ──
echo  [3c] Deploying static assets (ms.js, ms.css -^> /static/)...
scp "%PROJECT%\ms.js" %SERVER%:%REMOTE%/static/ms.js
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for ms.js. Check SSH connection.
    pause
    exit /b 1
)
scp "%PROJECT%\ms.css" %SERVER%:%REMOTE%/static/ms.css
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for ms.css. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3d: Deploy SUPER exemplar photos (assets/super -> /static/super/) ──
:: JNR-FIX-4 (22 Jul 2026): exemplar photos previously uploaded by hand and drifted.
:: Permanent step so listing photo sets always ship with the site.
echo  [3d] Deploying SUPER exemplar photos (assets\super -^> /static/super/)...
:: ASSET-SYNC (22 Jul 2026): hash-sync uploads only new/changed files (was: full re-upload every deploy)
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1" -LocalDir "%PROJECT%\assets\super" -Filter *.jpg -RemoteDir %REMOTE%/static/super -Server %SERVER%
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for assets\super photos. Check SSH connection.
    pause
    exit /b 1
)
ssh -n %SERVER% "chmod 644 %REMOTE%/static/super/*.jpg"
echo  Done.
echo.

:: ── Step 3e: ONE-SHOT super-seller data fix (runs only while flag file exists) ──
:: JNR-FIX-1/5 (22 Jul 2026, David-approved): specialist seller per category +
:: price units on rate-based exemplars. Guarded by RUN_SUPER_FIX_ONCE.flag;
:: deletes the flag after a successful apply so this NEVER re-runs.
if exist "%PROJECT%\RUN_SUPER_FIX_ONCE.flag" (
    echo  [3e] ONE-SHOT: super-seller/category + price-unit fix...
    scp "%PROJECT%\scripts\fix_super_sellers.py" %SERVER%:%REMOTE%/fix_super_sellers.py
    if %errorlevel% neq 0 (
        echo  ERROR: SCP failed for fix_super_sellers.py - fix NOT run, flag kept.
    ) else (
        echo  --- dry run ---
        ssh -n %SERVER% "cd %REMOTE% && python3 fix_super_sellers.py"
        echo  --- apply ---
        ssh -n %SERVER% "cd %REMOTE% && python3 fix_super_sellers.py --apply"
        if %errorlevel% equ 0 (
            del "%PROJECT%\RUN_SUPER_FIX_ONCE.flag"
            echo  [OK] Super-seller fix applied - one-shot flag removed.
        ) else (
            echo  [FAIL] apply returned an error - flag kept, investigate before next deploy.
        )
    )
    echo.
)

:: ── Step 3b: Deploy World Heritage data (wonders.json) ────
echo  [3b] Deploying Wonders data (wonders.json -^> wonders.json)...
scp "%PROJECT%\wonders.json" %SERVER%:%REMOTE%/wonders.json
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for wonders.json. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 3e: Deploy demo data (demo_listings.json + demo_sellers.json) ──
:: The BEA serves /demo-listings + /demo-sellers from these files (cached in-process),
:: so edits to demo content only go live once the file is on the box AND the BEA is
:: restarted. Previously these were NOT auto-deployed, so demo-data edits silently
:: never reached production (the demo-property heritage-link + NY-amenities drift,
:: fixed 18 Jun, traced to exactly this gap). They land BEFORE the BEA restart so the
:: in-process demo cache reloads atomically with the restart.
echo  [3e-pre] Validating demo POIs (cross-city contamination guard)...
python "%PROJECT%\scripts\validate_demo_pois.py"
if %errorlevel% neq 0 (
    echo  ERROR: demo POI validation FAILED - a listing has wrong-city/implausible amenities.
    echo         Fix demo_listings.json ^(regenerate via scripts\regen_pois^) before deploying.
    pause
    exit /b 1
)
echo  [3e] Deploying demo data (demo_listings.json; demo_sellers.json is server-managed)...
scp "%PROJECT%\demo_listings.json" %SERVER%:%REMOTE%/demo_listings.json
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for demo_listings.json. Check SSH connection.
    pause
    exit /b 1
)

echo  [3f] Deploying feature videos - the how-to set the app plays...
:: mkdir removed 5 Jul - dir exists and serves; the bare ssh line wedged a run for 7+ min
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1" -LocalDir "%PROJECT%\videos" -Filter *.mp4 -RemoteDir %REMOTE%/static/videos -Server %SERVER%
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for videos. Check SSH connection.
    pause
    exit /b 1
)
ssh -n -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 %SERVER% "mkdir -p %REMOTE%/static/videos && chmod 755 %REMOTE%/static/videos && chmod 644 %REMOTE%/static/videos/*.mp4"

:: -- LEGAL-STEP-1: legal must-have cards (country/category, Step 6 of 6 in SELL flow)
echo  [3d] Deploying legal must-have cards (assets\legal-must-haves -^> /static/legal-must-haves/)...
ssh -n %SERVER% "mkdir -p %REMOTE%/static/legal-must-haves/ZA %REMOTE%/static/legal-must-haves/US %REMOTE%/static/legal-must-haves/UK %REMOTE%/static/legal-must-haves/AU"
scp "%PROJECT%\agency_import_guide.html" %SERVER%:%REMOTE%/static/agency-import-guide.html
:: AGENT-SVC (19 Jul 2026): agency playbook PDF - console 'User manual' button links it; was uploaded manually before
scp "%PROJECT%\TrustSquare_Agency_Playbook.pdf" %SERVER%:%REMOTE%/static/TrustSquare_Agency_Playbook.pdf
scp "%PROJECT%\agents_as_a_service.html" %SERVER%:%REMOTE%/static/agents-as-a-service.html
:: PHOTO-ANON-1 (20 Jul 2026): generic per-vertical agent scenes - cards never show a person pre-intro
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1" -LocalDir "%PROJECT%\assets\agent-stock" -Filter * -RemoteDir %REMOTE%/static/agent-stock -Server %SERVER%
:: BRAND-PHOTO-1 (20 Jul 2026): Higgsfield brand photos - home category tiles + sell-flow tiles (self-hosted, no hotlinks)
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1" -LocalDir "%PROJECT%\assets\brand-photos" -Filter *.jpg -RemoteDir %REMOTE%/static/brand-photos -Server %SERVER%
powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1" -LocalDir "%PROJECT%\assets\sf-tiles" -Filter *.jpg -RemoteDir %REMOTE%/static -Server %SERVER%
ssh -n %SERVER% "chmod 644 %REMOTE%/static/agent-stock/* %REMOTE%/static/brand-photos/*.jpg %REMOTE%/static/sf_cat_*.jpg"
scp "%PROJECT%\assets\legal-must-haves\legal-cards.js" %SERVER%:%REMOTE%/static/legal-must-haves/legal-cards.js
for %%C in (ZA US UK AU) do powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT%\scripts\sync_assets.ps1" -LocalDir "%PROJECT%\assets\legal-must-haves\%%C" -Filter *.png -RemoteDir %REMOTE%/static/legal-must-haves/%%C -Server %SERVER%
ssh -n %SERVER% "chmod 755 %REMOTE%/static/legal-must-haves %REMOTE%/static/legal-must-haves/* && chmod 644 %REMOTE%/static/legal-must-haves/*/*.png"

:: -- DOC-SYNC-1 (17 Jul 2026, David/Session-141 counter drift): dashboard docs ship with EVERY deploy.
:: -- /dashboard/summary parses currentSession from the SERVER copy of STATUS.md; when these
:: -- four docs lag, the cockpit lies (it showed 139 for a month after 140 was consumed).
echo  [3e] Syncing dashboard docs (STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS -^> server)...
scp "%PROJECT%\STATUS.md" %SERVER%:%REMOTE%/STATUS.md
scp "%PROJECT%\CHANGELOG.md" %SERVER%:%REMOTE%/CHANGELOG.md
scp "%PROJECT%\BACKLOG.md" %SERVER%:%REMOTE%/BACKLOG.md
scp "%PROJECT%\AUDIT_PROGRESS.md" %SERVER%:%REMOTE%/AUDIT_PROGRESS.md
ssh -n %SERVER% "o=$(md5sum %REMOTE%/static/videos/expedition-dossier-howto.mp4 | cut -d\" \" -f1); s=$(curl -s --max-time 25 https://trustsquare.co/static/videos/expedition-dossier-howto.mp4?vchk=$RANDOM | md5sum | cut -d\" \" -f1); if [ \"$o\" = \"$s\" ]; then echo \"   [OK] videos: served bytes match origin - CDN fresh\"; else echo \"   [FAIL] videos: served differs from origin - CDN stale or wrong path\"; fi"
echo  Done.

:: demo_sellers.json is intentionally SERVER-MANAGED - the single source of truth lives
:: ONLY on the box, on purpose. It was de-bloated out of the FEA (it used to be hardcoded
:: there), and keeping a local + server copy caused constant drift, so by deliberate
:: decision it is NOT kept in the repo for now. Demo data is purged at launch and may later
:: be promoted to permanent repo-tracked data. Do NOT "fix" the absence by committing a
:: local copy - that reintroduces the exact drift this decision removed.
if exist "%PROJECT%\demo_sellers.json" (
    echo  [INFO] Local demo_sellers.json found - deploying it to the server.
    scp "%PROJECT%\demo_sellers.json" %SERVER%:%REMOTE%/demo_sellers.json
    if %errorlevel% neq 0 (
        echo  ERROR: SCP failed for demo_sellers.json. Check SSH connection.
        pause
        exit /b 1
    )
) else (
    echo  [INFO] demo_sellers.json is server-managed - not in local repo by design, nothing to deploy.
)
echo  Done.
echo.

:: ── Step 3d: Deploy backend modules (auth/database/storage/payments) ──
:: These four modules are imported by main.py but were previously NOT auto-deployed
:: (server-only). O2 audit fix: sync them here, guarded. auth.py is fail-closed
:: (refuses to start if MS_API_KEY is unset) — MS_API_KEY is confirmed set in the
:: systemd unit environment, so this is live-safe. They land BEFORE the BEA restart
:: below so the restart picks up the new modules atomically.
echo  [3d] Deploying backend modules (auth.py, database.py, storage.py, payments.py)...
scp "%PROJECT%\auth.py" %SERVER%:%REMOTE%/auth.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for auth.py. Check SSH connection.
    pause
    exit /b 1
)
scp "%PROJECT%\database.py" %SERVER%:%REMOTE%/database.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for database.py. Check SSH connection.
    pause
    exit /b 1
)
scp "%PROJECT%\storage.py" %SERVER%:%REMOTE%/storage.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for storage.py. Check SSH connection.
    pause
    exit /b 1
)
scp "%PROJECT%\payments.py" %SERVER%:%REMOTE%/payments.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for payments.py. Check SSH connection.
    pause
    exit /b 1
)
:: S3 (CC-004) — AI paid-feed tier-gate + non-rolling grant modules. Imported by
:: main.py; must land BEFORE the BEA restart so the gate + sweep ship atomically.
scp "%PROJECT%\ai_service_tiers.py" %SERVER%:%REMOTE%/ai_service_tiers.py
scp "%PROJECT%\ai_provider.py" %SERVER%:%REMOTE%/ai_provider.py
if errorlevel 1 (
    echo  ERROR: SCP failed for ai_provider.py ^(AI provider seam^). Check SSH connection.
)
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for ai_service_tiers.py. Check SSH connection.
    pause
    exit /b 1
)
scp "%PROJECT%\launch_redemption.py" %SERVER%:%REMOTE%/launch_redemption.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for launch_redemption.py. Check SSH connection.
    pause
    exit /b 1
)

:: AGENT-SVC (19 Jul 2026): professional-agents module - bea_main imports it; BEA cannot boot without it
scp "%PROJECT%\estate_agents.py" %SERVER%:%REMOTE%/estate_agents.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for estate_agents.py. Check SSH connection.
    pause
    exit /b 1
)
echo  Done.
echo.

:: ── Step 4: Deploy BEA + restart ──────────────────────────
echo  [3g] Ensuring SEARCH-AI env drop-in (idempotent)...
ssh -n -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 %SERVER% "mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=SEARCH_AI_ENABLED=1\nEnvironment=SEARCH_AI_DRYRUN=0\nEnvironment=SEARCH_AI_DAILY_USD=1.0\n' > /etc/systemd/system/marketsquare.service.d/search-ai.conf && systemctl daemon-reload && echo SEARCH-AI-ENV-OK"
echo  Done.
echo.

echo  [3h] Demand-loop flip: dry-run ON, import RM-5 pool (idempotent)...
ssh -n -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 %SERVER% "mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=DEMAND_LOOP_ENABLED=1\nEnvironment=DEMAND_LOOP_DRYRUN=1\nEnvironment=DEMAND_RM5_DB=/var/www/citylauncher/data/prospects.db\nEnvironment=DEMAND_FROM_EMAIL=TrustSquare <hello@mail.trustsquare.co>\nEnvironment=DEMAND_SWEEP_ON_BOOT=1\n' > /etc/systemd/system/marketsquare.service.d/demand.conf && systemctl daemon-reload && echo DEMAND-ENV-OK"
echo  Done.
echo.

echo  [4/6] Deploying BEA backend (bea_main.py -^> main.py)...
scp "%PROJECT%\bea_main.py" %SERVER%:%REMOTE%/main.py
if %errorlevel% neq 0 (
    echo  ERROR: SCP failed for BEA. Check SSH connection.
    pause
    exit /b 1
)
echo  SCP done. Restarting BEA service...
ssh -n %SERVER% "systemctl restart marketsquare"
if %errorlevel% neq 0 (
    echo  ERROR: BEA service restart failed. Check server with:
    echo    ssh root@178.104.73.239 "journalctl -u marketsquare -n 30"
    pause
    exit /b 1
)
echo  BEA restarted. Waiting for startup...
timeout /t 5 /nobreak >nul
echo  Done.
echo.

:: ── Step 5: Reload nginx ──────────────────────────────────
echo  [5/6] Reloading nginx...
ssh -n %SERVER% "nginx -s reload"
if %errorlevel% neq 0 (
    echo  WARNING: nginx reload may have failed. Check server manually.
) else (
    echo  Done.
)
echo.

:: ── Step 5b: Purge Cloudflare edge cache ──
echo  [5b] Purging Cloudflare cache...
ssh -n %SERVER% "curl -sf -m 20 -X POST http://localhost:8000/admin/purge-cache >nul 2>&1" && echo   [OK] Cloudflare purge requested || echo   [WARN] Cloudflare purge failed - purge manually if users see stale assets

:: -- Step 5c: Re-warm the tutor-video edge cache (purge above evicted them) --
:: The tutor .mp4s are large; on a COLD Cloudflare cache the first mobile viewer
:: pulls the whole file from origin and the video just spins (the 22-Jul tester bug).
echo  [5c] Warming tutor-video edge cache so first view is instant...
ssh -n %SERVER% "bash %REMOTE%/warm_videos.sh" && echo   [OK] tutor videos warmed (all HIT) || echo   [WARN] video warm failed - run warm_video_cache.sh manually
echo.

:: ── Step 6: Verify deploy on server ──────────────────────
echo  [6/6] Verifying deploy on server...
ssh -n -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 %SERVER% "journalctl -u marketsquare --since '90 seconds ago' --no-pager | grep 'DEMAND' | tail -3"

echo.

ssh -n %SERVER% "grep -q 'listings/mine' %REMOTE%/main.py && echo   [OK] BEA: new routes confirmed in main.py || echo   [FAIL] BEA: old main.py still on server - SCP may have failed"

ssh -n %SERVER% "grep -q 'tuppence/balance' %REMOTE%/main.py && echo   [OK] BEA: tuppence/balance endpoint confirmed || echo   [FAIL] BEA: missing endpoint - redeploy needed"
ssh -n %SERVER% "grep -q 'requires_paid_feed' %REMOTE%/ai_service_tiers.py && echo   [OK] BEA: S3 paid-feed gate present || echo   [FAIL] BEA: ai_service_tiers.py stale - redeploy needed"
ssh -n %SERVER% "grep -q 'grant_expiry' %REMOTE%/launch_redemption.py && echo   [OK] BEA: non-rolling grant sweep present || echo   [FAIL] BEA: launch_redemption.py stale - redeploy needed"

ssh -n %SERVER% "grep -q 'wishlist/feed' %REMOTE%/main.py && echo   [OK] BEA: wishlist feed endpoints confirmed || echo   [FAIL] BEA: wishlist endpoints missing - redeploy needed"

ssh -n %SERVER% "systemctl is-active marketsquare >nul 2>&1 && echo   [OK] BEA service is active || echo   [FAIL] BEA service is NOT active - check journalctl"

ssh -n %SERVER% "test -f %REMOTE%/auth.py && test -f %REMOTE%/database.py && test -f %REMOTE%/storage.py && test -f %REMOTE%/payments.py && test -f %REMOTE%/ai_service_tiers.py && test -f %REMOTE%/launch_redemption.py && echo   [OK] BEA: backend modules auth,database,storage,payments,ai_service_tiers,launch_redemption present || echo   [FAIL] BEA: one or more backend modules missing - redeploy needed"

ssh -n %SERVER% "test -f %REMOTE%/demo_listings.json && echo   [OK] Demo: demo_listings.json present on server || echo   [FAIL] Demo: demo_listings.json missing - redeploy needed"
ssh -n %SERVER% "test -f %REMOTE%/demo_sellers.json && echo   [OK] Demo: demo_sellers.json present on server - server-managed single source || echo   [WARN] Demo: demo_sellers.json MISSING on server - this is the ONLY copy, /demo-sellers will be empty"

:: -- Admin freshness check (21 Jun): hash-compare the deployed admin.html to the LOCAL
:: -- build instead of grepping for a feature marker. The old check grepped admin.html
:: -- for 'dev-tools' - a tab that was later removed - so it false-FAILED ("old admin.html
:: -- still on server") on every deploy even though the file was perfectly up to date.
:: -- An md5 match proves byte-for-byte that the live file IS exactly what you just built,
:: -- and never goes stale. (Mirrors the 6b live-ms.js hash check.)
set ADMIN_MD5=HASH_CAPTURE_FAILED
for /f "usebackq delims=" %%H in (`powershell -NoProfile -Command "(Get-FileHash -Algorithm MD5 -LiteralPath '%PROJECT%\marketsquare_admin.html').Hash.ToLower()"`) do set ADMIN_MD5=%%H
ssh -n %SERVER% "md5sum %REMOTE%/admin.html | grep -q '%ADMIN_MD5%' && echo   [OK] Admin: live admin.html matches local build || echo   [FAIL] Admin: deployed admin.html does NOT match local build - redeploy needed"

ssh -n %SERVER% "grep -q 'view-showcase' %REMOTE%/admin.html && echo   [OK] Admin: showcase tab confirmed || echo   [FAIL] Admin: showcase tab missing - redeploy needed"

ssh -n %SERVER% "grep -q 'screen-edit-listing' %REMOTE%/index.html && echo   [OK] Buyer app: new index.html confirmed on server || echo   [FAIL] Buyer app: old index.html still on server"

ssh -n %SERVER% "grep -q 'wlBootToken\|wishlist-feed' %REMOTE%/index.html && echo   [OK] Buyer app: wishlist feed UI confirmed || echo   [FAIL] Buyer app: wishlist UI missing - redeploy needed"

ssh -n %SERVER% "test -f %REMOTE%/service-worker.js && echo   [OK] Service worker confirmed on server || echo   [FAIL] service-worker.js missing - redeploy needed"

ssh -n %SERVER% "grep -q 'local-market/listings' %REMOTE%/main.py && echo   [OK] BEA: Local Market endpoints confirmed || echo   [FAIL] BEA: Local Market endpoints missing - redeploy needed"

ssh -n %SERVER% "grep -q 'trust-score/breakdown' %REMOTE%/main.py && echo   [OK] BEA: Trust Score Hub endpoint confirmed || echo   [FAIL] BEA: Trust Score Hub endpoint missing - redeploy needed"

ssh -n %SERVER% "grep -q 'screen-local-market' %REMOTE%/index.html && echo   [OK] Buyer app: Local Market page confirmed || echo   [FAIL] Buyer app: Local Market page missing - redeploy needed"

ssh -n %SERVER% "grep -q 'lm-eula-modal' %REMOTE%/admin.html && echo   [OK] Admin: Local Market form + EULA modal confirmed || echo   [FAIL] Admin: Local Market form missing - redeploy needed"

ssh -n %SERVER% "grep -q 'tsh-panel' %REMOTE%/admin.html && echo   [OK] Admin: Trust Score Hub UI confirmed || echo   [FAIL] Admin: Trust Score Hub missing - redeploy needed"

ssh -n %SERVER% "for i in 1 2 3 4 5; do curl -s http://localhost:8000/health | grep -qE 'status.*ok' && { echo '   [OK] BEA /health reports status ok'; break; }; [ $i -eq 5 ] && echo '   [FAIL] BEA /health not ok - check service restart'; sleep 2; done"

ssh -n %SERVER% "test -f %REMOTE%/ai_provider.py && echo   [OK] BEA: ai_provider.py AI-swap-seam present || echo   [FAIL] BEA: ai_provider.py MISSING - AI_ACTIVE swap falls back to Anthropic"

ssh -n %SERVER% "grep -q 'ai/example/{function_id}' %REMOTE%/main.py && echo   [OK] BEA: /ai/example route present - free example buttons fixed || echo   [FAIL] BEA: /ai/example route MISSING - example buttons still broken"

ssh -n %SERVER% "test -f %REMOTE%/static/ms.js && echo   [OK] static/ms.js present on server || echo   [FAIL] static/ms.js missing - redeploy needed"
ssh -n %SERVER% "grep -oE 'ms\.js\?v=[0-9]+' %REMOTE%/index.html | head -1 | sed 's/^/   [INFO] served buyer app references /'"

:: -- Step 6b: CDN content check - catch stale Cloudflare BEFORE the browser does
echo.
echo  [6b] Verifying the LIVE ms.js through Cloudflare matches your build...
powershell -NoProfile -Command ^
  "$ErrorActionPreference='SilentlyContinue';" ^
  "$html = Get-Content -Raw -LiteralPath '%PROJECT%\marketsquare.html';" ^
  "$jsv = [regex]::Match($html, 'ms\.js\?v=(\d+)').Groups[1].Value;" ^
  "$local = (Get-FileHash -Algorithm MD5 -LiteralPath '%PROJECT%\ms.js').Hash;" ^
  "$tmp = Join-Path $env:TEMP ('ms_live_' + $jsv + '.js');" ^
  "Remove-Item $tmp -ErrorAction SilentlyContinue;" ^
  "try { Invoke-WebRequest -UseBasicParsing -Headers @{ 'Accept-Encoding' = 'identity' } -Uri ('https://trustsquare.co/static/ms.js?v=' + $jsv) -OutFile $tmp } catch {};" ^
  "if (Test-Path $tmp) { $live = (Get-FileHash -Algorithm MD5 -LiteralPath $tmp).Hash } else { $live = 'FETCH_FAILED' };" ^
  "if ($local -eq $live) { Write-Host ('   [OK] LIVE ms.js matches your build  md5=' + $local.Substring(0,8)) } else { Write-Host ('   [FAIL] LIVE ms.js does NOT match  local=' + $local.Substring(0,8) + '  live=' + $live); Write-Host '          Cloudflare is serving stale - just re-run this script; the auto ?v bump fixes it.' }"
echo.

:: -- Step 6c: BIT self-test (the full functional + negative health check) --
echo.
echo  [6c] Running BIT self-test against the live site...
python "%PROJECT%\..\trustsquare-bit-agent\bit_cycle.py"
if errorlevel 2 (
  echo   [FAIL] BIT: a CRITICAL ^(S1^) marker failed - see the failing ids above. Investigate before relying on this deploy.
) else if errorlevel 1 (
  echo   [WARN] BIT: a major ^(S2^) marker failed - a feature/guardrail is down. See ids above; dashboard shows amber.
) else (
  echo   [OK] BIT: all self-test markers PASS - dashboard updated green.
)
echo.

:: ── Step 7: Auto-commit the deployed working tree ─────────
:: ROOT-CAUSE FIX for FEA-DRIFT (recurring since 2 Jun: ms.js/ms.css/HTML edited
:: and pushed live but never committed, because "commit after deploy" was a manual
:: step a human had to remember). Commits cannot be made reliably from the Cowork
:: sandbox (its .git lives on a FUSE mount that blocks unlink -> git lock/index
:: fails, GIT-INDEX-1), so the commit MUST happen here, on Windows, where git is
:: native. Making the deploy itself commit means deploying == committing: the drift
:: is now structurally impossible, not a thing anyone has to remember.
:: Driven by PowerShell (not batch if/!var!) so it needs no delayed expansion and
:: is non-fatal by design: a git hiccup must never fail an already-successful deploy.
echo.
:: ── Step 6b: Purge Cloudflare edge cache (added 22 Jul 2026, David-approved) ──
:: New bytes under same filenames (photos, ms.js) otherwise serve stale from the
:: edge until TTL. The endpoint exists for exactly this moment; now it is called
:: automatically, every deploy, as the docstring always claimed.
echo  [6b] Purging Cloudflare edge cache...
curl -s -m 25 -X POST "https://trustsquare.co/admin/purge-cache"
echo.
echo  Done.
echo.

:: Stale-lock sweep (22 Jul 2026): a leftover .git\index.lock from a crashed git op
:: made step 7 no-op silently (SilentlyContinue swallowed it). No git runs during
:: this script, so any lock here is stale by definition - safe to remove.
if exist "%PROJECT%\.git\index.lock" (
    echo    [WARN] Stale .git\index.lock found - removing so auto-commit can run.
    del /f "%PROJECT%\.git\index.lock"
)
echo  [7/7] Auto-committing the deployed working tree (FEA-DRIFT guard)...
powershell -NoProfile -Command ^
  "$ErrorActionPreference='SilentlyContinue';" ^
  "Set-Location -LiteralPath '%PROJECT%';" ^
  "git rev-parse --is-inside-work-tree *> $null;" ^
  "if ($LASTEXITCODE -ne 0) { Write-Host '   [WARN] %PROJECT% is not a git repo - skipping auto-commit.'; exit 0 };" ^
  "$dirty = (git status --porcelain);" ^
  "if (-not $dirty) { Write-Host '   [OK] Working tree already clean - nothing to commit.'; exit 0 };" ^
  "git add -A *> $null;" ^
  "$stamp = Get-Date -Format 'yyyy-MM-dd HH:mm';" ^
  "git commit -m ('Deploy auto-commit ' + $stamp + ' (FEA-DRIFT guard: source synced with live)') *> $null;" ^
  "if ($LASTEXITCODE -ne 0) { Write-Host '   [WARN] git commit reported nothing committed - check git status.'; exit 0 };" ^
  "Write-Host '   [OK] Committed all deployed changes locally.';" ^
  "git rev-parse --abbrev-ref '@{u}' *> $null;" ^
  "if ($LASTEXITCODE -ne 0) { Write-Host '   [INFO] No upstream tracking branch - commit is local only (fine).'; exit 0 };" ^
  "git push *> $null;" ^
  "if ($LASTEXITCODE -eq 0) { Write-Host '   [OK] Pushed to remote.' } else { Write-Host '   [WARN] git push failed - commit is safe locally; push manually when able.' }"
echo.
echo.
echo  ============================================================
echo   DEPLOY COMPLETE
echo  ============================================================
echo.
echo  trustsquare.co        ^|  buyer app updated
echo  trustsquare.co/admin  ^|  admin tool updated
echo  BEA backend           ^|  restarted and verified
echo.
echo  If any [FAIL] lines appear above, that file did not deploy.
echo  Re-run this script or manually SCP the failing file.
echo.
echo  Opening sites in browser to verify (cache-busted)...
timeout /t 2 /nobreak >nul
start "" "https://trustsquare.co?v=%random%"
start "" "https://trustsquare.co/admin.html?v=%random%"
echo.
timeout /t 6 /nobreak >nul
exit
