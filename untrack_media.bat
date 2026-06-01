@echo off
REM ── Stop tracking listing media (keeps files on disk) ──────────────
REM Removes already-committed media from git tracking WITHOUT deleting
REM the actual files (--cached). This does NOT rewrite history — the
REM old copies still exist in past commits (a separate cleanup step),
REM but from here forward git stops versioning them. Run Windows-side.

cd /d "%~dp0"

echo.
echo === Untracking Kronberg/ media folder (files stay on disk) ===
git rm -r --cached --ignore-unmatch "Kronberg" 2>nul

echo.
echo === Untracking stray media files by extension ===
for %%E in (jpg jpeg png gif webp avif mp4 mov MOV avi mkv heic HEIC) do (
  git rm -r --cached --ignore-unmatch "*.%%E" 2>nul
)

echo.
echo === Staging the .gitignore update too ===
git add .gitignore

echo.
echo === Committing ===
git commit -m "Untrack listing media; gitignore Kronberg + media (invariant #4)"

echo.
echo === Pushing ===
git push

echo.
echo Done. Media files remain on disk; git no longer tracks them going forward.
echo (Old copies still live in history until a dedicated rewrite session.)
echo Press any key to close.
pause >nul
