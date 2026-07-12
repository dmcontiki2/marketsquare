@echo off
:: commit_checkpoint.bat - bank the current working tree into git WITHOUT deploying.
:: Safe + reversible: commits LOCALLY only. Nothing is scp'd, nothing goes live.
:: Use it to collapse accumulated uncommitted changes into a rollback point
:: (e.g. when the pre-deploy scan shows a large 'dirty' count).
cd /d "%~dp0"
where git >nul 2>&1 || ( echo  git is not on PATH - cannot commit here. & pause & exit /b 1 )
git rev-parse --is-inside-work-tree >nul 2>&1 || ( echo  Not a git repo. & pause & exit /b 1 )
echo  ============================================================
echo   CHECKPOINT COMMIT  (no deploy - local git only)
echo  ============================================================
echo.
echo  These files will be banked:
echo.
git status --short
echo.
set /p OK=Commit ALL of the above as a checkpoint? (y/N): 
if /I not "%OK%"=="y" ( echo  Cancelled - nothing committed. & pause & exit /b 0 )
git add -A
git commit -m "Checkpoint %date% %time% (manual, no deploy)"
echo.
echo  Done - working tree banked in git.
echo   - see it:   git log -1
echo   - undo it:  git reset --soft HEAD~1   (keeps your files, just un-commits)
echo.
pause
