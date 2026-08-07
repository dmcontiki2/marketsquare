@echo off
REM GATE_STATUS.bat - READ-ONLY diagnosis of why migration 007 (the pre-launch token gate)
REM has never taken effect. Changes NOTHING. Writes everything to gate_status_log.txt so
REM Claude can read it through the folder bridge (no window-watching needed).
setlocal
cd /d "%~dp0"
set SERVER=root@178.104.73.239
echo run %date% %time% > gate_status_log.txt
ssh %SERVER% "echo '--- migrations_done (007?) ---'; grep -n '007' /var/www/marketsquare/.migrations_done 2>/dev/null || echo 'NOT RECORDED (would retry on next deploy)'; echo '--- GATE-ENFORCE-1 marker in nginx? ---'; grep -rl 'GATE-ENFORCE-1' /etc/nginx/sites-enabled/ /etc/nginx/sites-available/ 2>/dev/null || echo 'MARKER ABSENT (never applied)'; echo '--- candidate site files ---'; grep -rl 'trustsquare.co' /etc/nginx/sites-enabled/ /etc/nginx/sites-available/ /etc/nginx/conf.d/ 2>/dev/null; echo '--- catch-all blocks (the anchor 007 looks for) ---'; grep -rn -A2 'location / {' /etc/nginx/sites-enabled/ 2>/dev/null | head -40; echo '--- is 007 on the server at all? ---'; ls -la /var/www/marketsquare/migrations/007* 2>/dev/null || echo 'migration file not on server'; echo '--- last post_deploy migration output ---'; tail -25 /var/www/marketsquare/.deploy_log 2>/dev/null || echo 'no .deploy_log'" >> gate_status_log.txt 2>&1
echo exitcode %errorlevel% >> gate_status_log.txt
