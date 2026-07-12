@echo off
title Check TrustSquare server config
color 0B
set SERVER=root@178.104.73.239
echo(
echo   Checking TrustSquare server config (read-only, changes nothing)...
echo(
ssh %SERVER% "p=$(systemctl show -p MainPID --value marketsquare); if grep -aq 'MS_JWT_SECRET=ms_jwt_secret_change_me' /proc/$p/environ; then echo '  [X] MS_JWT_SECRET: still the DEFAULT value - INSECURE, set a real one'; elif grep -aq 'MS_JWT_SECRET=' /proc/$p/environ; then echo '  [OK] MS_JWT_SECRET: set to a real value'; else echo '  [X] MS_JWT_SECRET: NOT SET - service is using the insecure built-in default'; fi; if grep -aq -e 'RESEND_API_KEY=' -e 'GMAIL_APP_PASSWORD=' /proc/$p/environ; then echo '  [OK] Email transport: configured (sign-in links will send)'; else echo '  [X] Email transport: NOT configured (sign-in links will NOT send)'; fi"
echo(
echo   Done. Nothing was changed on the server.
echo(
pause
