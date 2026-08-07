#!/bin/bash
echo "=== 1. IS pillow-heif INSTALLED IN THE APP'S PYTHON? (TS-0025 root cause) ==="
PY=$(systemctl show -p ExecStart marketsquare 2>/dev/null | grep -oE '/[^ ]*python[0-9.]*' | head -1)
[ -z "$PY" ] && PY=python3
echo "app python: $PY"
$PY -c "import pillow_heif, PIL; print('pillow_heif OK ->', pillow_heif.__version__, '| Pillow', PIL.__version__)" 2>&1 | tail -3
echo "--- what the app itself reports ---"
journalctl -u marketsquare --no-pager 2>/dev/null | grep -iE "heif|heic" | tail -5
echo
echo "=== 2. THE 502 ON /listings?city=Pretoria (TS-0026) ==="
journalctl -u marketsquare --since "2026-08-07 06:00" --no-pager 2>/dev/null | grep -B12 -iE "Traceback|Internal Server" | tail -40
echo "--- nginx upstream errors today ---"
tail -60 /var/log/nginx/error.log 2>/dev/null | grep -iE "upstream|timed out|502" | tail -12
echo
echo "=== 3. THE RESEND 422 (sign-in email 'from' field) ==="
grep -E "^(DEMAND_FROM_EMAIL|SUPPORT_FROM_EMAIL|RELAY_FROM)=" /var/www/marketsquare/.env 2>/dev/null | sed 's/^/  raw: [/;s/$/]/'
echo
echo "=== 4. deploy freshness (did today's failed deploy leave drift?) ==="
ls -l --time-style=+%Y-%m-%d_%H:%M /var/www/marketsquare/main.py 2>/dev/null
grep -c "RELAY-FROM-1" /var/www/marketsquare/main.py 2>/dev/null | sed 's/^/  RELAY-FROM-1 present on server: /'
