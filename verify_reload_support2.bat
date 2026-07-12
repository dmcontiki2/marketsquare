@echo off
setlocal
set SERVER=root@178.104.73.239
set OUT=%~dp0support_reload_report2.txt
set SSHOPTS=-o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3

echo ============================================================ > "%OUT%"
echo  VERIFY SUPPORT BLOCKS + EXPLICIT nginx test and reload >> "%OUT%"
echo ============================================================ >> "%OUT%"

echo [1] What do the support blocks look like NOW in the active config...
ssh %SSHOPTS% %SERVER% "sed -n '/location = \/support/,/}/p' /etc/nginx/sites-enabled/marketsquare" >> "%OUT%" 2>&1

echo [2] nginx -t FULL output...
ssh %SSHOPTS% %SERVER% "nginx -t; echo exit=$?" >> "%OUT%" 2>&1

echo [3] Explicit reload + status...
ssh %SSHOPTS% %SERVER% "systemctl reload nginx; echo reload_exit=$?; systemctl is-active nginx" >> "%OUT%" 2>&1

echo [4] Public check from the box...
ssh %SSHOPTS% %SERVER% "curl -s -o /dev/null -w 'public /support: %%{http_code}\n' https://trustsquare.co/support" >> "%OUT%" 2>&1

echo.
type "%OUT%"
echo.
echo  Done - Claude reads support_reload_report2.txt next.
pause >nul
