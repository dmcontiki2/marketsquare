@echo off
REM ============================================================================
REM PEER_REVIEW.bat - one-click independent peer review (GPT-5.6, READ-ONLY).
REM   Double-click        : reviews the current core design set (edit DEFAULT below)
REM   Drag files onto it  : reviews exactly those files
REM Report lands in Records\PEER_REVIEW_<date>.md and opens in Notepad.
REM Needs OPENAI_API_KEY - put it in a .env file beside this .bat (gitignored) as:
REM   OPENAI_API_KEY=sk-...
REM Cost: ~$0.02-0.06 per review on the default Terra model. No git writes here,
REM so no git_unlock needed (GIT-LOCK-1 applies to committers only).
REM ============================================================================
setlocal
cd /d "%~dp0"
set FILES=%*
if "%FILES%"=="" set FILES=AI_AUTO_FAILOVER_P2_DESIGN.md AI_SWAP_ARCHITECTURE.md ai_provider.py
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
%PY% scripts\peer_review.py %FILES%
if not %errorlevel%==0 goto :fail
for /f "delims=" %%f in ('dir /b /o-d Records\PEER_REVIEW_*.md 2^>nul') do (start "" notepad "Records\%%f" & goto :opened)
:opened
echo.
echo Peer review complete - report opened in Notepad. Bring it to Claude to discuss.
pause
exit /b 0
:fail
echo.
echo Peer review did NOT run - see message above (missing key = add .env with OPENAI_API_KEY=sk-...).
pause
exit /b 1
