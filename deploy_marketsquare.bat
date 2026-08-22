@echo off
title MarketSquare - Release (ONE deploy: publish the deploy ref)
color 0A
setlocal EnableExtensions EnableDelayedExpansion

:: ============================================================================
::  deploy_marketsquare.bat  -  ONE-DEPLOY PUSH WRAPPER  (v4, 2 Aug 2026)
::
::  DEPLOY-CONSOLIDATION-1: the 44KB per-file copy engine that lived here is
::  RETIRED (preserved at deploy_marketsquare.bat.bak-onedeploy-20260802).
::  There is now exactly ONE deploy engine: the server itself
::  (ops/autodeploy/server_deploy.sh). It pulls the "deploy" ref from the GitHub
::  mirror, places files by the allowlist manifest (ops/autodeploy/
::  deploy_manifest.txt), bumps the cache-buster MONOTONICALLY (an older version
::  number can never be pushed over live), restarts, purges the CDN,
::  health-checks and AUTO-ROLLS-BACK on failure, then runs the post-deploy
::  hook (seed + one-time migrations).
::
::  This wrapper only: gates -> commit -> publish the ref -> verify.
::  /ship, /TSL, /start and a bare double-click all land here, so every path
::  rides the same engine. Binary media (photos/videos/PDF) ships separately
::  via media_push.bat - the media lane never carries code.
::
::  Rollback: git revert the bad commit, run this again (see ONE_DEPLOY.md).
:: ============================================================================

set PROJECT=C:\Users\David\Projects\MarketSquare
set SERVER=root@178.104.73.239

cd /d "%PROJECT%" || (echo  ERROR: project folder not found: %PROJECT% & pause & exit /b 1)

set "PYEXE="
where python >nul 2>&1 && set "PYEXE=python"
if not defined PYEXE where py >nul 2>&1 && set "PYEXE=py"

echo.
echo  ============================================================
echo   MARKETSQUARE  RELEASE  (one deploy: publish the deploy ref)
echo   %DATE% %TIME%
echo  ============================================================
echo.

:: -- [1/6] Stale git lock self-heal (RG-0015 class) --------------------------
call "%PROJECT%\git_unlock.bat"

:: -- [2/6] Cache-buster autobump for changed child statics (maps -> ms.js) ---
:: The server bumps index.html's ms.js/ms.css ?v= itself (monotonic). This bump
:: covers the CHILD references INSIDE ms.js (tour maps etc.) before we commit.
if defined PYEXE %PYEXE% "%PROJECT%\scripts\autobump.py"

:: -- SESSION-COUNTER-1 (22 Aug 2026): recompute the session number from the
::    status.d/changelog.d fragments BEFORE the compilers archive them, so the
::    JSON this release ships is current. Replaces the prose regex that pinned
::    the dashboard badge to 155 for three weeks.
if defined PYEXE if exist "%PROJECT%\scripts\session_counter.py" %PYEXE% "%PROJECT%\scripts\session_counter.py" --quiet

:: -- CHANGELOG-COLLISION-1 (2 Aug 2026): fold pending changelog.d/ fragments into
:: -- CHANGELOG.md (the ONE writer) so the record rides this release commit. Sessions
:: -- drop fragments, never rewrite CHANGELOG.md directly - see scripts/changelog_compile.py.
if defined PYEXE if exist "%PROJECT%\scripts\changelog_compile.py" %PYEXE% "%PROJECT%\scripts\changelog_compile.py"
:: -- same discipline for STATUS.md (STATUS-COLLISION-1, 5 Aug 2026): fold status.d/.
if defined PYEXE if exist "%PROJECT%\scripts\status_compile.py" %PYEXE% "%PROJECT%\scripts\status_compile.py"

:: -- [3/6] Gates: pre-deploy scan + deploy lock + CM/DB gate -----------------
set "TSL_LOCK_HELD="
if not defined PYEXE (
    echo  [3/6] WARN: python not found - gates skipped, continuing.
    goto :gates_done
)
%PYEXE% "%PROJECT%\predeploy_check.py"
set SCANRC=%errorlevel%
if /I "%PREDEPLOY_MODE%"=="strict" if not "%SCANRC%"=="0" (
    echo  ABORT: pre-deploy scan flagged a dangerous change - strict mode. See deploy_audit.log.
    pause
    exit /b 1
)
if not exist "%PROJECT%\tsl_gate.py" goto :gates_done
%PYEXE% "%PROJECT%\tsl_gate.py" acquire
if errorlevel 1 (
    echo  ABORT: another TrustSquare release is already running - lock held.
    echo  If you are certain none is, delete "%PROJECT%\.tsl.lock" and retry.
    pause
    exit /b 1
)
set "TSL_LOCK_HELD=1"
%PYEXE% "%PROJECT%\tsl_gate.py" gate
if errorlevel 1 (
    if /I "%TSL_MODE%"=="strict" (
        echo  ABORT: CM+DB gate not clean - strict mode. Fix the gate findings first.
        %PYEXE% "%PROJECT%\tsl_gate.py" release
        pause
        exit /b 1
    )
    echo  [3/6] WARN: CM+DB gate reported findings - releasing anyway - warn mode.
)
:gates_done

:: -- [4/6] Commit the working tree (deploying == committing, FEA-DRIFT guard) -
:: DW-026 FIX (7 Aug 2026): "git commit" returns errorlevel 1 for TWO different
:: things - "nothing to commit" (benign) and "the commit FAILED" (catastrophic).
:: This step treated both as benign and pushed anyway. On 7 Aug a stale .git/HEAD.lock
:: made the commit fail, the batch pushed the PREVIOUS commit as the deploy ref, the
:: server deployed that, health-checked green and reported SUCCESS - a whole session's
:: work never shipped and nothing said so. Staged-ness tells them apart: after a
:: successful commit the index is clean; after a failed one the changes are still there.
git add -A
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Release %DATE% %TIME%" >nul 2>&1
    git diff --cached --quiet
    if errorlevel 1 (
        echo  ERROR: the commit FAILED - your changes are STILL STAGED.
        echo         NOTHING was released. Do not re-run until this is cleared.
        echo         Usual cause is a stale git lock left by a dead process:
        echo            del /f /q .git\HEAD.lock
        echo            del /f /q .git\index.lock
        echo         Then run this again. ^(DW-026^)
        goto :release_lock_fail
    )
    echo  [4/6] Committed the working tree.
) else (
    echo  [4/6] Working tree already clean - releasing the current commit.
)
git log -1 --oneline

:: -- [5/6] Publish: mirror backup + the deploy ref ---------------------------
echo  [5/6] Pushing to the mirror - backup ref main...
git push origin HEAD:main
echo  [5/6] Publishing the deploy ref - THIS is the deploy...
git push origin HEAD:deploy
if errorlevel 1 (
    echo  ERROR: publish failed. NOTHING was released. Common causes:
    echo    - no network / GitHub auth, or a non-fast-forward - see message above.
    goto :release_lock_fail
)
echo.
echo   PUBLISHED. The server deploys it within ~2 minutes - with health check,
echo   monotonic cache-buster, auto-rollback, then seed + migrations hook.
echo.

:: -- [6/6] Verify: wait for the server tick, then md5-compare local vs live --
echo  [6/6] Waiting ~3 minutes for the server to apply and settle...
timeout /t 180 /nobreak >nul
curl.exe -s -m 15 https://trustsquare.co/health | find "ok" >nul && echo   [OK] /health answers ok || echo   [WARN] /health not confirming - check now
if defined PYEXE (
    set "DRIFTLINE="
    for /f "delims=" %%D in ('%PYEXE% "%PROJECT%\check_deploy_drift.py" 2^>nul') do if not defined DRIFTLINE set "DRIFTLINE=%%D"
    echo   !DRIFTLINE!
    echo !DRIFTLINE! | find /i "clean" >nul
    if errorlevel 1 (
        echo   [WAIT] Not clean yet - one more 2-minute server tick...
        timeout /t 120 /nobreak >nul
        %PYEXE% "%PROJECT%\check_deploy_drift.py"
        echo   If still ahead: watch  ssh %SERVER% "tail -20 /var/log/marketsquare-deploy.log"
    ) else (
        echo   [OK] Local and live match - release landed.
    )
)

if defined TSL_LOCK_HELD if defined PYEXE %PYEXE% "%PROJECT%\tsl_gate.py" release
echo.
echo  ============================================================
echo   RELEASE COMPLETE
echo  ============================================================
pause
exit /b 0

:release_lock_fail
if defined TSL_LOCK_HELD if defined PYEXE %PYEXE% "%PROJECT%\tsl_gate.py" release
pause
exit /b 1
