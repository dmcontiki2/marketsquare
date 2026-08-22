#!/bin/bash
# harden_env_file.sh - stop /etc/environment being world-readable. NO SECRET VALUES.
e=/etc/environment
[ -f "$e" ] || { echo "  [OK] no /etc/environment"; exit 0; }
echo "  [--] before: $(stat -c '%a owner=%U' $e)"
cp -a "$e" "$e.bak-$(date +%Y%m%d-%H%M%S)"
chmod 600 "$e"
echo "  [--] after : $(stat -c '%a owner=%U' $e)"
[ "$(stat -c %a $e)" = "600" ] && echo "  [OK] no longer world-readable" || echo "  [X]  chmod did not take"

echo "  [--] who else could have read it (non-root users with a login shell):"
awk -F: '$3>=1000 && $7 !~ /nologin|false/ {print "      " $1}' /etc/passwd | head -20
awk -F: '$3>=1000 && $7 !~ /nologin|false/' /etc/passwd | grep -q . || echo "      (none - only root has a login shell)"

echo "  [--] service still healthy after the change:"
echo "      marketsquare: $(systemctl is-active marketsquare)"
code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health)
echo "      /health     : HTTP $code"

echo "  [--] JWT secret (the forge-an-admin-token risk):"
p=$(systemctl show -p MainPID --value marketsquare)
v=$(tr '\0' '\n' < /proc/$p/environ | grep '^MS_JWT_SECRET=' | head -1 | cut -d= -f2-)
if [ -z "$v" ]; then echo "      [X] not set - service using built-in default"
elif [ "$v" = "ms_jwt_secret_change_me" ]; then echo "      [X] STILL THE FACTORY DEFAULT"
else echo "      [--] set, fingerprint $(printf '%s' "$v" | sha256sum | cut -c1-8), length ${#v}"; fi
