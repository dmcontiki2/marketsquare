@echo off
REM WHATBROKE.bat v3 - READ-ONLY. Prints on screen AND saves whatbroke_<time>.txt
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py -3)
%PY% scripts\whatbroke.py
echo.
echo ==== window stays open - copy anything above if Claude needs it ====
pause
