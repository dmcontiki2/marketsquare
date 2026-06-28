@echo off
REM ── Is the SERVER current with my local build? One honest check. Run anytime. ──
setlocal
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set PROJECT=%~dp0
echo ============================================================
echo  DEPLOY FRESHNESS CHECK  (local build vs what's live)
echo ============================================================

echo.
echo [1] ai_provider.py (the AI swap seam) on server?
ssh %SERVER% "test -f %REMOTE%/ai_provider.py && echo    [OK] present || echo    [MISSING] - run deploy_marketsquare.bat (AI_ACTIVE swap is inert without it)"

echo.
echo [2] BEA has the live ai_active flag + Page-4 endpoint?
ssh %SERVER% "grep -q '_ts_active_provider' %REMOTE%/main.py && echo    [OK] live-provider seam present || echo    [STALE] - main.py predates the Page-4 switch; run deploy_marketsquare.bat"
ssh %SERVER% "grep -q 'ai_active must be' %REMOTE%/main.py && echo    [OK] /admin/flags accepts ai_active || echo    [STALE] - run deploy_marketsquare.bat"

echo.
echo [3] Dashboard has the Page-4 AI Provider card?
ssh %SERVER% "grep -q 'ai-prov-card' %REMOTE%/dashboard.html && echo    [OK] Page-4 AI Provider card present || echo    [MISSING] - run deploy_bit_monitoring.bat (ships dashboard.html)"

echo.
echo [4] Does the live BEA actually answer with the provider state?
ssh %SERVER% "curl -s http://localhost:8000/flags | grep -q 'ai_provider' && echo    [OK] /flags reports ai_provider || echo    [STALE] - BEA not restarted with new main.py"

echo.
echo ============================================================
echo  Any [MISSING]/[STALE] above = re-run that deploy script.
echo  All [OK] = server matches your local build.
echo ============================================================
endlocal
