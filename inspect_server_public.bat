@echo off
setlocal
set SERVER=root@178.104.73.239
set OUT=%~dp0server_public_report.txt
set SSHOPTS=-o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3

echo ============================================================ > "%OUT%"
echo  READ-ONLY INSPECT: why /support is 401 + public surfaces >> "%OUT%"
echo ============================================================ >> "%OUT%"

echo [1] nginx config - every location and auth_basic around support/terms/privacy...
ssh %SSHOPTS% %SERVER% "nginx -T 2>/dev/null | grep -n -B3 -A6 -i -E 'support|auth_basic|location /terms|location /privacy' | head -120" >> "%OUT%" 2>&1

echo [2] webroot support files...
ssh %SSHOPTS% %SERVER% "ls -la /var/www/marketsquare/support* 2>/dev/null; ls -la /var/www/*/support* 2>/dev/null | head -10" >> "%OUT%" 2>&1

echo [3] local curl checks from the box itself...
ssh %SSHOPTS% %SERVER% "curl -s -o /dev/null -w 'direct /support: %%{http_code}\n' http://127.0.0.1/support; curl -s -o /dev/null -w 'direct /terms: %%{http_code}\n' http://127.0.0.1/terms" >> "%OUT%" 2>&1

echo.
type "%OUT%"
echo.
echo  Done - report in server_public_report.txt. Claude reads it next.
pause >nul
