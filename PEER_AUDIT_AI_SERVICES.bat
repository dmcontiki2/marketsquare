@echo off
REM ============================================================================
REM PEER_AUDIT_AI_SERVICES.bat v3 - Phase 2 of the internal AI services audit.
REM v3 (5 Aug 2026): closes the Peer's 'could not verify' list where files CAN
REM close it - fresh targeted extract (peer_pack_ai.py v3: endpoints, helpers,
REM schemas, admin auth, user-facing copy, computed totality evidence with real
REM line numbers), plus privacy policy, drill + golden-set artifacts, breaker
REM tests, price card, funnel snapshot. Live-runtime claims (keys on server,
REM tests passing, live routing) are NOT file-verifiable - that leg belongs to
REM QA (ledger/BIT/drills), per the five-role review model.
REM Needs OPENAI_API_KEY in .env beside this .bat. Cost ballpark ~$0.15-0.25.
REM READ-ONLY: writes only the extract + Records\PEER_REVIEW_<date>_full.md.
REM ============================================================================
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
%PY% scripts\peer_pack_ai.py
if not %errorlevel%==0 goto :fail
%PY% scripts\peer_review.py --lens full --focus "Second-vendor audit of the internal AI services, round 2. The Author's Phase-1 report is the first file; its findings F1-F5 were ACTED ON same day and the extract shows the POST-fix code. PEER_PACK_BEA_EXTRACT.md carries the application evidence you previously lacked: real line numbers, endpoint bodies, schemas, admin auth, user-facing copy, and a COMPUTED TOTALITY EVIDENCE section (Author-derived greps - treat as claims, spot-check by naming line ranges). For each of F1-F5: CONFIRM the fix is correct and complete, or REFUTE with evidence. Re-judge your three round-1 headline findings against this packet: (1) probe claiming - HEARTBEAT-1 now calls claim_probe; also judge the scoreboard's nightly unclaimed force-probe. (2) cost bounding - the Correction-2 rails and ceilings are now visible; the currency pre-dispatch reservation remains open P2b work. (3) multi-processor privacy - privacy.html now carries the AI-processor disclosure; judge its adequacy and the open KYC fallback-pinning decision. Then hunt for what the Author missed. Name any absent evidence as a finding with the exact file and line range." "Records\AI_SERVICES_AUDIT_2026-08-05.md" "Records\PEER_PACK_BEA_EXTRACT.md" ai_provider.py ai_breaker.py ai_service_tiers.py ai_scoreboard.py test_ai_breaker.py ai_price_card.json ai_funnel_snapshot.json AI_AUTO_FAILOVER_P2_DESIGN.md privacy.html "Records\DRILL_T0_SEAM_2026-08-01.md" "Records\GOLDEN_SET_OPENAI_2026-08-01.md"
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
