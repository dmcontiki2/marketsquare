@echo off
REM ============================================================================
REM  git_unlock.bat  -  clear STALE .git lock files before any git write.
REM
REM  WHY: this repo has several git writers (manual commit.bat, the nightly
REM  checkpoint task, the deploy auto-commit, and the daily-loop sandbox). When
REM  two overlap or one is interrupted, git leaves a 0-byte lock file that then
REM  blocks the NEXT write ("Unable to create ...lock: File exists"). On the
REM  FUSE-mounted sandbox those locks cannot be removed at all, so they sit
REM  there until a human deletes them. This helper removes them automatically.
REM
REM  GIT-LOCK-2 (11 Aug 2026): extended from index.lock to the CLASS -- a sandbox
REM  commit succeeded but left .git\HEAD.lock behind (FUSE blocks unlink), which
REM  would have blocked the next commit exactly like index.lock always did.
REM  Now clears index.lock, HEAD.lock and packed-refs.lock by the same rule.
REM
REM  SAFE: locks are only deleted when NO git.exe is currently running, so this
REM  can never yank a lock out from under a live commit. A lock with no git
REM  process behind it is by definition stale and safe to remove.
REM  Called first by every commit path in this repo.
REM ============================================================================
cd /d "%~dp0"
tasklist /fi "imagename eq git.exe" 2>nul | find /i "git.exe" >nul
if not errorlevel 1 (
  echo  git.exe is running - leaving any .git locks in place ^(not stale^).
  exit /b 0
)
set RC=0
for %%L in (index.lock HEAD.lock packed-refs.lock) do call :clearone %%L
exit /b %RC%

:clearone
if not exist ".git\%1" exit /b 0
del /f /q ".git\%1" >nul 2>&1
if exist ".git\%1" ( echo  WARN: could not remove .git\%1 & set RC=1 ) else ( echo  cleared stale .git\%1 )
exit /b 0
