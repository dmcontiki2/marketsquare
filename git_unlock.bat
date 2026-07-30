@echo off
REM ============================================================================
REM  git_unlock.bat  -  clear a STALE .git\index.lock before any git write.
REM
REM  WHY: this repo has several git writers (manual commit.bat, the nightly
REM  checkpoint task, the deploy auto-commit, and the daily-loop sandbox). When
REM  two overlap or one is interrupted, git leaves a 0-byte .git\index.lock that
REM  then blocks the NEXT commit ("Unable to create index.lock: File exists").
REM  On the FUSE-mounted sandbox that lock cannot be removed at all, so it sits
REM  there until a human deletes it. This helper removes it automatically.
REM
REM  SAFE: it only deletes the lock when NO git.exe is currently running, so it
REM  can never yank the lock out from under a live commit. A lock with no git
REM  process behind it is by definition stale and safe to remove.
REM  Called first by every commit path in this repo.
REM ============================================================================
cd /d "%~dp0"
if not exist ".git\index.lock" exit /b 0
tasklist /fi "imagename eq git.exe" 2>nul | find /i "git.exe" >nul
if not errorlevel 1 (
  echo  git.exe is running - leaving .git\index.lock in place ^(not stale^).
  exit /b 0
)
del /f /q ".git\index.lock" >nul 2>&1
if exist ".git\index.lock" ( echo  WARN: could not remove .git\index.lock & exit /b 1 )
echo  cleared stale .git\index.lock
exit /b 0
