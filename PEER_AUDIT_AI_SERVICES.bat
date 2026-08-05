@echo off
REM ============================================================================
REM PEER_AUDIT_AI_SERVICES.bat v2 - Phase 2 of the internal AI services audit.
REM v2 (5 Aug 2026): answers the Peer's packet complaint - bea_main.py cannot ship
REM whole (850 KB vs the 120 KB/file cap), so scripts\peer_pack_ai.py now builds a
REM FRESH targeted extract (real line numbers) on every run, and the packet gains
REM the price card, the breaker test suite and the funnel snapshot.
REM Needs OPENAI_API_KEY in .env beside this .bat. Cost ballpark ~$0.10-0.20.
REM READ-ONLY: writes only the extract + Records\PEER_REVIEW_<date>_full.md.
REM ============================================================================
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
%PY% scripts\peer_pack_ai.py
if not %errorlevel%==0 goto :fail
%PY% scripts\peer_review.py --lens full --focus "Second-vendor audit of the internal AI services. The Author's Phase-1 report is the first file (findings F1-F5, all five since ACTED ON same day: F1 any-lane gates, F2 deliver-then-charge, F3 neutral copy, F5 heartbeat - the extract shows the POST-fix code). PEER_PACK_BEA_EXTRACT.md carries the application evidence you previously lacked, with real bea_main.py line numbers. For each finding: CONFIRM the fix is correct and complete, or REFUTE with evidence. Verify especially: the any_lane_configured gate class, the deliver-then-charge transaction shape (race windows? double-charge? charge lost on 402-after-delivery?), the HEARTBEAT-1 loop (concurrency, cost bounding, T3 hourly cadence), and hunt for what the Author missed. If a section you need is absent, name the exact line range as a finding." "Records\AI_SERVICES_AUDIT_2026-08-05.md" "Records\PEER_PACK_BEA_EXTRACT.md" ai_provider.py ai_breaker.py ai_service_tiers.py ai_scoreboard.py test_ai_breaker.py ai_price_card.json ai_funnel_snapshot.json AI_AUTO_FAILOVER_P2_DESIGN.md
if not %errorlevel%==0 goto :fail
for /f "delims=" %%f in ('dir /b /o-d Records\PEER_REVIEW_*_full.md 2^>nul') do (start "" notepad "Records\%%f" & goto :opened)
:opened
echo.
echo Peer audit complete - report opened in Notepad. Bring it to Claude to discuss.
pause
exit /b 0
:fail
echo.
echo Peer audit did NOT run - see message above (missing key = add .env with OPENAI_API_KEY=sk-...).
pause
exit /b 1
