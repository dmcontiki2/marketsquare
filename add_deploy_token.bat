@echo off
setlocal
cd /d "%~dp0"
set SRV=root@178.104.73.239
echo ============================================================
echo   TrustSquare - mint the deploy-hook token (MS_DEPLOY_TOKEN)
echo   Nothing secret is ever printed to this window.
echo ============================================================
echo.
echo [1/4] Minting the token on the server (root-only systemd drop-in)...
ssh -o ConnectTimeout=15 %SRV% "set -e; mkdir -p /etc/systemd/system/marketsquare.service.d; TOK=$(openssl rand -hex 24); printf '[Service]\nEnvironment=MS_DEPLOY_TOKEN=%%s\n' \"$TOK\" > /etc/systemd/system/marketsquare.service.d/deploy-token.conf; chmod 600 /etc/systemd/system/marketsquare.service.d/deploy-token.conf; printf 'MS_DEPLOY_TOKEN=%%s\n' \"$TOK\" > /root/ts_deploy_token_latest.txt; chmod 600 /root/ts_deploy_token_latest.txt; systemctl daemon-reload; systemctl restart marketsquare"
if errorlevel 1 goto :fail
echo.
echo [2/4] Health check after restart...
curl -s -o nul -w "%%{http_code}" https://trustsquare.co/health > "%TEMP%\ts_hc.txt"
set /p HC=<"%TEMP%\ts_hc.txt"
del "%TEMP%\ts_hc.txt" >nul 2>&1
if not "%HC%"=="200" (
  echo   !! /health answered %HC% - if this stays non-200, tell Claude. Token NOT collected.
  goto :end
)
echo   /health 200 - service healthy.
echo.
echo [3/4] Collecting the token into .secrets\deploy_keys.txt ...
scp %SRV%:/root/ts_deploy_token_latest.txt "%TEMP%\ts_dt.txt"
if errorlevel 1 goto :nofile
if not exist ".secrets" mkdir ".secrets"
findstr /v /b "MS_DEPLOY_TOKEN=" ".secrets\deploy_keys.txt" > "%TEMP%\ts_dk.txt" 2>nul
type "%TEMP%\ts_dt.txt" >> "%TEMP%\ts_dk.txt"
move /y "%TEMP%\ts_dk.txt" ".secrets\deploy_keys.txt" >nul
del "%TEMP%\ts_dt.txt" >nul 2>&1
echo   saved (old MS_DEPLOY_TOKEN line, if any, replaced).
echo.
echo [4/4] Wiping the server-side copy...
ssh %SRV% "rm -f /root/ts_deploy_token_latest.txt"
echo   done.
echo.
echo ============================================================
echo   Hook armed. It answers 503 until the next deploy ships the
echo   router include - fail-closed by design, not a fault.
echo   From then on Claude sessions deploy over 443, no clicks.
echo ============================================================
goto :end
:nofile
echo   No token file came back - nothing saved locally. Paste this window to Claude.
goto :end
:fail
echo   Server step failed - nothing changed. Paste this window to Claude.
:end
echo.
pause
