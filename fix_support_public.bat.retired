@echo off
setlocal
set SERVER=root@178.104.73.239
set OUT=%~dp0fix_support_report.txt
set SSHOPTS=-o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3

echo ============================================================ > "%OUT%"
echo  MAKE /support PUBLIC + ship current support.html >> "%OUT%"
echo ============================================================ >> "%OUT%"

echo [1] Locate config, back it up, drop the two auth includes for support only...
ssh %SSHOPTS% %SERVER% "F=$(grep -rl 'location = /support' /etc/nginx/sites-enabled /etc/nginx/sites-available /etc/nginx/conf.d 2>/dev/null | head -1); echo config: $F; cp $F $F.bak-support-20260706; sed -i '/location = \/support {/,/}/{/include snippets\/internal_auth.conf;/d}; /location = \/support.html {/,/}/{/include snippets\/internal_auth.conf;/d}' $F; grep -c 'internal_auth' $F" >> "%OUT%" 2>&1

echo [2] nginx -t safety gate - auto-restore on failure...
ssh %SSHOPTS% %SERVER% "if nginx -t 2>&1 | grep -q successful; then systemctl reload nginx && echo '   [OK] config valid - nginx reloaded'; else F=$(ls /etc/nginx/sites-enabled/*.bak-support-20260706 /etc/nginx/sites-available/*.bak-support-20260706 2>/dev/null | head -1); B=${F%.bak-support-20260706}; cp $F $B; systemctl reload nginx; echo '   [FAIL] config test failed - RESTORED backup, nothing changed'; fi" >> "%OUT%" 2>&1

echo [3] Ship the CURRENT refund-free support.html...
scp "%~dp0support.html" %SERVER%:/var/www/marketsquare/support.html >> "%OUT%" 2>&1
ssh %SSHOPTS% %SERVER% "chmod 644 /var/www/marketsquare/support.html; ls -la /var/www/marketsquare/support.html" >> "%OUT%" 2>&1

echo [4] Verify from the box via the public URL...
ssh %SSHOPTS% %SERVER% "curl -s -o /dev/null -w 'public /support: %%{http_code}\n' https://trustsquare.co/support; curl -s https://trustsquare.co/support | grep -c -i refund | xargs echo 'refund mentions:'" >> "%OUT%" 2>&1

echo.
type "%OUT%"
echo.
echo  Done - Claude verifies externally next.
pause >nul
