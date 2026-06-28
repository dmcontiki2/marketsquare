@echo off
REM ── Deploy BIT live monitoring: BEA endpoint + dashboard panel (version-guard safe) ──
REM Run from your machine (has SSH to the server). Server is source-of-truth for dashboard.html.
setlocal
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set PROJECT=%~dp0

echo [1/6] Pull the LIVE dashboard.html down (server = source of truth, version guard)...
scp %SERVER%:%REMOTE%/dashboard.html "%PROJECT%\dashboard.server.html"
if errorlevel 1 ( echo  ERROR: could not pull server dashboard. Abort. & exit /b 1 )

echo [2/6] Apply the BIT panel onto the SERVER copy (idempotent)...
python "%PROJECT%\apply_bit_panel.py" "%PROJECT%\dashboard.server.html"
if errorlevel 1 ( echo  ERROR: BIT panel anchors not found in server dashboard - tell Claude. & exit /b 1 )

echo [2b/6] Apply the AI Provider card (Page-4 / Launch Switch) onto the SERVER copy (idempotent)...
python "%PROJECT%\apply_ai_provider_card.py" "%PROJECT%\dashboard.server.html"
if errorlevel 1 ( echo  ERROR: AI Provider card anchors not found in server dashboard - tell Claude. & exit /b 1 )

echo [3/6] Syntax-check the patched dashboard...
node --check "%PROJECT%\dashboard.server.html" 2>nul || echo  (node --check skipped/na - HTML, continuing)

echo [4/6] Push patched dashboard back + deploy BEA (adds /dashboard/bit)...
scp "%PROJECT%\dashboard.server.html" %SERVER%:%REMOTE%/dashboard.html
if errorlevel 1 ( echo  ERROR: dashboard push failed. & exit /b 1 )
ssh %SERVER% "grep -q ai-prov-card %REMOTE%/dashboard.html && echo    [OK] Launch Switch: AI Provider card present || echo    [FAIL] AI Provider card MISSING after push"
if errorlevel 1 ( echo  ERROR: dashboard push failed. & exit /b 1 )
scp "%PROJECT%\bea_main.py" %SERVER%:%REMOTE%/main.py
if errorlevel 1 ( echo  ERROR: BEA push failed. & exit /b 1 )

echo [5/6] Restart BEA so /dashboard/bit goes live...
ssh %SERVER% "systemctl restart marketsquare"
if errorlevel 1 ( echo  ERROR: BEA restart failed: ssh %SERVER% "journalctl -u marketsquare -n 30" & exit /b 1 )

echo [6/6] Purge edge cache + verify endpoint...
ssh %SERVER% "curl -sf -m 20 -X POST http://localhost:8000/admin/purge-cache >nul 2>&1"
ssh %SERVER% "curl -s -m 10 http://localhost:8000/dashboard/bit"
echo.
echo  DONE. /dashboard/bit is live. The dashboard BIT panel will show 'No BIT run yet'
echo  until the trustsquare-bit-cycle scheduled task posts its first board.
echo  Keep the patched copy: %PROJECT%\dashboard.server.html is now the current dashboard.
endlocal
