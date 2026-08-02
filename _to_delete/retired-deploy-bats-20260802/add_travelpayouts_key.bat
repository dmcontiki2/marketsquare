@echo off
setlocal
echo ==================================================
echo  TP-FLIGHTS-1 one-shot: token + panel row to live
echo  (built by Claude 01 Aug 2026 - mirrors add_resend_key.bat
echo   + the SCAN-29 targeted backend deploy recipe)
echo ==================================================
set SERVER=root@178.104.73.239
set REMOTE=/var/www/marketsquare
set PROJECT=C:\Users\David\Projects\MarketSquare
set EXPECT_MD5=2016cf432e57eeeacd12bfb9497e35ac

if not exist "%PROJECT%\.secrets\tp_token.txt" (
  echo ERROR: .secrets\tp_token.txt missing - tell Claude.
  pause & exit /b 1
)
set /p TOKEN=<"%PROJECT%\.secrets\tp_token.txt"

echo [1/5] Drift guard: server main.py must match Claude's pre-edit copy...
set SRVMD5=
ssh -o ConnectTimeout=15 %SERVER% "md5sum %REMOTE%/main.py | awk '{printf $1}'" > "%TEMP%\tp_srvmd5.txt"
if %errorlevel% neq 0 ( echo ERROR: could not reach server for md5 - tell Claude. & pause & exit /b 1 )
set /p SRVMD5=<"%TEMP%\tp_srvmd5.txt"
del "%TEMP%\tp_srvmd5.txt" >nul 2>&1
if not "%SRVMD5%"=="%EXPECT_MD5%" (
  echo ERROR: server main.py md5 %SRVMD5% does not match expected %EXPECT_MD5%.
  echo Server drifted since Claude's edit - DO NOT ship. Tell Claude.
  pause & exit /b 1
)
echo   [OK] parity confirmed.

echo [2/5] Writing TRAVELPAYOUTS_TOKEN drop-in (owner-only, chmod 600)...
ssh -o ConnectTimeout=15 %SERVER% "umask 077 && mkdir -p /etc/systemd/system/marketsquare.service.d && printf '[Service]\nEnvironment=TRAVELPAYOUTS_TOKEN=%TOKEN%\n' > /etc/systemd/system/marketsquare.service.d/travelpayouts.conf && chmod 600 /etc/systemd/system/marketsquare.service.d/travelpayouts.conf && systemctl daemon-reload && echo TP-ENV-OK"
if %errorlevel% neq 0 ( echo ERROR: env write failed - tell Claude. & pause & exit /b 1 )

echo [3/5] Shipping bea_main.py -^> main.py (backup + AST gate + atomic swap)...
scp "%PROJECT%\bea_main.py" %SERVER%:%REMOTE%/main.py.new
if %errorlevel% neq 0 ( echo ERROR: scp failed - tell Claude. & pause & exit /b 1 )
ssh -o ConnectTimeout=15 %SERVER% "python3 -m py_compile %REMOTE%/main.py.new && cp %REMOTE%/main.py %REMOTE%/main.py.bak-tpflights2-20260801 && mv %REMOTE%/main.py.new %REMOTE%/main.py && chmod 644 %REMOTE%/main.py && echo SWAP-OK"
if %errorlevel% neq 0 ( echo ERROR: AST gate or swap failed - nothing replaced. Tell Claude. & pause & exit /b 1 )

echo [4/5] Restarting BEA...
ssh -o ConnectTimeout=15 %SERVER% "systemctl restart marketsquare && sleep 3 && systemctl is-active marketsquare"
if %errorlevel% neq 0 (
  echo ERROR: restart failed. ROLLBACK: ssh %SERVER% then
  echo   cp %REMOTE%/main.py.bak-tpflights2-20260801 %REMOTE%/main.py ^&^& systemctl restart marketsquare
  pause & exit /b 1
)

echo [5/5] Verifying health + env inside the service...
ssh -o ConnectTimeout=15 %SERVER% "for i in 1 2 3 4 5; do curl -s -m 10 http://localhost:8000/health | grep -qE 'status.*ok' && { echo '   [OK] /health ok'; break; }; [ $i -eq 5 ] && { echo '   [FAIL] /health not ok'; exit 1; }; sleep 2; done && systemctl show marketsquare -p Environment | grep -q TRAVELPAYOUTS_TOKEN && echo    [OK] TRAVELPAYOUTS_TOKEN visible to the service"
if %errorlevel% neq 0 ( echo ERROR: verify failed - tell Claude BEFORE closing this window. & pause & exit /b 1 )

set TOKEN=
echo.
echo ==================================================
echo  DONE. Close this window and tell Claude: "TP shipped".
echo ==================================================
pause
