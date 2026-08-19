@echo off
REM ── ONETAP-1 (RUL-028) ── Google sign-in credentials -> server .env, restart BEA.
REM NOT in git (handles a secret).
REM
REM SELF-CORRECTING: this REPLACES any existing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
REM lines rather than refusing when they are already present. The first version refused
REM to double-add, which meant a mis-paste could not be fixed by re-running it (19 Aug
REM 2026: the secret got pasted into the Client ID prompt and the script had no way back).
REM
REM VALIDATES the two values before touching the server, because they are easy to swap:
REM   Client ID     ends with .apps.googleusercontent.com
REM   Client secret starts with GOCSPX-
setlocal EnableDelayedExpansion
set SERVER=root@178.104.73.239
set ENVF=/var/www/marketsquare/.env

echo.
echo   ONETAP-1 - Google sign-in credentials
echo   =====================================
echo   Client ID     looks like  869589580243-xxxx.apps.googleusercontent.com
echo   Client secret looks like  GOCSPX-xxxxxxxxxxxxxxxx
echo.

:askid
set "GID="
set /p GID="Paste the Google CLIENT ID: "
if "!GID!"=="" ( echo   Nothing entered - aborting. & pause & exit /b 1 )
echo !GID! | find /i "apps.googleusercontent.com" >nul
if errorlevel 1 (
  echo.
  echo   [!] That does not look like a Client ID - it must end with
  echo       .apps.googleusercontent.com
  echo       ^(if it starts with GOCSPX- you have pasted the SECRET here^)
  echo.
  goto askid
)

:asksecret
set "GSEC="
set /p GSEC="Paste the Google CLIENT SECRET: "
if "!GSEC!"=="" ( echo   Nothing entered - aborting. & pause & exit /b 1 )
echo !GSEC! | find /i "GOCSPX-" >nul
if errorlevel 1 (
  echo.
  echo   [!] That does not look like a Client secret - it should start with GOCSPX-
  echo.
  goto asksecret
)

echo.
echo Removing any previous Google lines, then writing the correct ones...
ssh %SERVER% "sed -i '/^GOOGLE_CLIENT_ID=/d; /^GOOGLE_CLIENT_SECRET=/d' %ENVF% && echo GOOGLE_CLIENT_ID=!GID! >> %ENVF% && echo GOOGLE_CLIENT_SECRET=!GSEC! >> %ENVF%"

echo.
echo Verifying (expect exactly 1 and 1):
ssh %SERVER% "grep -c '^GOOGLE_CLIENT_ID=' %ENVF%; grep -c '^GOOGLE_CLIENT_SECRET=' %ENVF%"

echo.
echo Sanity check (expect id ends googleusercontent.com, secret starts GOCSPX-):
ssh %SERVER% "grep '^GOOGLE_CLIENT_ID=' %ENVF% | sed 's/.*\(............................\)$/  id ends ...\1/'; grep -o '^GOOGLE_CLIENT_SECRET=GOCSPX-' %ENVF% || echo '  [!] secret does NOT start with GOCSPX- - re-run this script'"

echo.
echo Restarting BEA so the env is loaded...
ssh %SERVER% "systemctl restart marketsquare && sleep 4 && curl -s http://localhost:8000/health"

echo.
echo Proving the lane is live (want google:true):
ssh %SERVER% "sleep 2; curl -s http://localhost:8000/auth/providers"

echo.
echo   google:true  -^> open https://trustsquare.co in a private window; the
echo                   "Continue with Google" button appears on the sign-in screen.
echo   google:false -^> a value is empty or wrong. Just run this script again -
echo                   it overwrites, so re-running is always safe.
echo.
pause
endlocal
