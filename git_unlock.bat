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
REM GIT-LOCK-6 (25 Sep 2026, DW-154): "/aged" = the every-tick sweep run by autodeploy_agent.bat.
REM The sandbox's git runs inside the VM, where tasklist cannot see it, so a lock can belong to a
REM LIVE sandbox commit even when no git.exe runs here. The tick therefore clears a top-level or
REM ref lock only once it is older than 15 minutes (a commit holds one for seconds), and never
REM touches loose-object temps or the stale_locks asides - those stay with the full sweep below.
if /i "%~1"=="/aged" goto :aged
for %%L in (index.lock HEAD.lock packed-refs.lock) do call :clearone %%L
REM GIT-LOCK-3 (16 Aug 2026): next-index-*.lock joins the class, and the host
REM sweep deletes what the SANDBOX could only rename aside (FUSE blocks unlink
REM there; scripts/git_unlock.py renames stale locks into .git\stale_locks\),
REM plus the orphaned loose-object temps failed FUSE unlinks leave behind.
for %%F in (.git\next-index-*.lock) do del /f /q "%%F" >nul 2>&1
REM GIT-LOCK-5 (16 Sep 2026, DW-123): REF LOCKS join the class, on BOTH lanes.
REM A commit takes a lock beside every ref it updates - .git\refs\heads\<branch>.lock -
REM and a stranded one blocks every later commit on that branch with
REM   fatal: cannot lock ref 'HEAD': Unable to create '...main.lock': File exists
REM That is exactly what stopped a commit on 14 Sep while BOTH unlock tools reported
REM 'nothing to sweep': neither this bat nor scripts/git_unlock.py looked one directory
REM down into .git\refs. Recursive by design - tags and remote refs strand the same way,
REM and a hand-maintained list of branch names is a list somebody forgets to update.
REM Still gated by the git.exe check above, so this can never race a live commit.
for /r ".git\refs" %%F in (*.lock) do del /f /q "%%F" >nul 2>&1

if exist ".git\stale_locks" rd /s /q ".git\stale_locks" >nul 2>&1
del /f /q ".git\HEAD.lock.stale-*" >nul 2>&1
for /r ".git\objects" %%F in (tmp_obj_*) do del /f /q "%%F" >nul 2>&1
exit /b %RC%

:aged
echo %date% %time% aged sweep
REM Enumerate with cmd (the same for /r the full sweep proves on every run), judge each
REM file's age in PowerShell. A first cut enumerated in PowerShell too and saw 0 locks while
REM a probe lock sat in .git\refs\heads (08:35 tick, 25 Sep) - cause not visible from here.
for %%L in (index.lock HEAD.lock packed-refs.lock) do if exist ".git\%%L" call :agedone ".git\%%L"
for /r ".git\refs" %%F in (*.lock) do call :agedone "%%F"
exit /b 0

:agedone
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f=Get-Item -LiteralPath '%~1' -Force; if($f.LastWriteTime -lt (Get-Date).AddMinutes(-15)){ Remove-Item -LiteralPath $f.FullName -Force; 'cleared aged ' + $f.FullName } else { 'kept (young) ' + $f.FullName + ' ' + $f.LastWriteTime }"
exit /b 0

:clearone
if not exist ".git\%1" exit /b 0
del /f /q ".git\%1" >nul 2>&1
if exist ".git\%1" ( echo  WARN: could not remove .git\%1 & set RC=1 ) else ( echo  cleared stale .git\%1 )
exit /b 0
