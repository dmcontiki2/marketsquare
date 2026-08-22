#!/bin/bash
# check_email_keys.sh - which Resend key does each holder use? PRINTS NO SECRET VALUES.
# Only an 8-char sha256 fingerprint, enough to compare, useless to an attacker.
fp() { printf '%s' "$1" | sha256sum | cut -c1-8; }

echo "  --- holder 1: main service drop-in ---"
f=/etc/systemd/system/marketsquare.service.d/resend.conf
if [ -f "$f" ]; then
  v=$(grep -o 'RESEND_API_KEY=.*' "$f" | head -1 | cut -d= -f2-)
  echo "  [OK] resend.conf        fingerprint $(fp "$v")  (written $(stat -c %y "$f" | cut -d. -f1))"
else
  echo "  [X]  resend.conf MISSING"
fi

echo "  --- holder 2: running process (what is actually in force) ---"
p=$(systemctl show -p MainPID --value marketsquare)
v=$(tr '\0' '\n' < /proc/$p/environ | grep '^RESEND_API_KEY=' | head -1 | cut -d= -f2-)
if [ -n "$v" ]; then echo "  [OK] live process       fingerprint $(fp "$v")"; else echo "  [X]  live process has NO Resend key"; fi

echo "  --- holder 3: dormancy service env file ---"
e=/var/www/marketsquare/.env
if [ -f "$e" ]; then
  v=$(grep '^RESEND_API_KEY=' "$e" | head -1 | cut -d= -f2- | tr -d '"'"'"'"')
  if [ -n "$v" ]; then echo "  [!!] .env HAS a Resend key  fingerprint $(fp "$v")"; else echo "  [OK] .env exists, no Resend key in it"; fi
else
  echo "  [OK] no /var/www/marketsquare/.env file"
fi
echo "  [--] dormancy timer     : $(systemctl is-enabled tuppence-dormancy.timer 2>/dev/null || echo not-installed)"

echo "  --- any other holder on the box ---"
grep -rl 'RESEND_API_KEY' /etc/systemd/system/ 2>/dev/null | sed 's/^/  [--] /'
