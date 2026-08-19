#!/bin/bash
# ONETAP-1 / ENVKEY-1 diagnostic. Run ON THE SERVER. Read-only, changes nothing.
cd /var/www/marketsquare || exit 1
echo "=============================================="
echo " 1. Are the credentials on disk?"
echo "=============================================="
printf '   GOOGLE_CLIENT_ID lines     : %s\n' "$(grep -c '^GOOGLE_CLIENT_ID=' .env)"
printf '   GOOGLE_CLIENT_SECRET lines : %s\n' "$(grep -c '^GOOGLE_CLIENT_SECRET=' .env)"
if grep -q '^GOOGLE_CLIENT_ID=.*apps\.googleusercontent\.com' .env; then
  echo "   client id SHAPE            : ok (ends apps.googleusercontent.com)"
else
  echo "   client id SHAPE            : *** WRONG *** - not a client id (secret pasted here?)"
fi
if grep -q '^GOOGLE_CLIENT_SECRET=GOCSPX-' .env; then
  echo "   client secret SHAPE        : ok (starts GOCSPX-)"
else
  echo "   client secret SHAPE        : *** WRONG *** - does not start GOCSPX-"
fi

echo
echo "=============================================="
echo " 2. Is the ENVKEY fix deployed?"
echo "=============================================="
N=$(grep -c 'envkey' main.py)
printf '   envkey() calls in main.py  : %s\n' "$N"
if grep -q 'ai_provider.envkey(cfg\["client_id_env"\])' main.py; then
  echo "   OAuth lane uses envkey     : YES - fix is deployed"
else
  echo "   OAuth lane uses envkey     : NO  - fix NOT deployed yet, run the deploy"
fi

echo
echo "=============================================="
echo " 3. Does the RUNNING process see the .env?"
echo "=============================================="
PID=$(systemctl show -p MainPID --value marketsquare)
printf '   main pid                   : %s\n' "$PID"
if [ -r "/proc/$PID/environ" ]; then
  ENVN=$(tr '\0' '\n' < "/proc/$PID/environ")
  printf '   process has GOOGLE_CLIENT_ID: %s\n' "$(echo "$ENVN" | grep -c '^GOOGLE_CLIENT_ID=')"
  printf '   process has RESEND_API_KEY  : %s\n' "$(echo "$ENVN" | grep -c '^RESEND_API_KEY=')"
  echo
  echo "   (0 = systemd is NOT exporting .env, which is ENVKEY-1 and means"
  echo "    envkey() is REQUIRED. It also means Resend has been dark and all"
  echo "    mail has been going out via the Gmail SMTP fallback.)"
else
  echo "   cannot read /proc/$PID/environ"
fi

echo
echo "=============================================="
echo " 4. What the app reports"
echo "=============================================="
echo -n "   /auth/providers : "; curl -s http://localhost:8000/auth/providers; echo
echo -n "   /health         : "; curl -s http://localhost:8000/health; echo
echo
echo "=============================================="
echo " 5. Live commit"
echo "=============================================="
git -C /var/www/marketsquare log --oneline -1 2>/dev/null || echo "   (not a git checkout - placed by manifest)"
