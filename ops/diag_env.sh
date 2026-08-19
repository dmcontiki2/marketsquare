#!/bin/bash
# ENVKEY-1 audit. Run ON THE SERVER. READ-ONLY - prints NO secret values, only names.
# Answers one question definitively: which credentials does the RUNNING process actually
# have, and which exist only in .env where a bare os.getenv() will never see them?
cd /var/www/marketsquare || exit 1
PID=$(systemctl show -p MainPID --value marketsquare)
echo "main pid: $PID"
echo
echo "=== how does the unit supply env? ==="
systemctl cat marketsquare 2>/dev/null | grep -iE "^(Environment|EnvironmentFile)" || echo "  (no Environment/EnvironmentFile lines at all)"
echo
echo "=== per-credential: in .env?  in the live process? ==="
printf "  %-26s %-8s %-10s %s\n" NAME IN_ENV IN_PROCESS VERDICT
tr '\0' '\n' < "/proc/$PID/environ" 2>/dev/null | cut -d= -f1 | sort -u > /tmp/_procenv
for n in PAYSTACK_SECRET_KEY MS_ADMIN_PASSWORD MS_JWT_SECRET RESEND_API_KEY \
         GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET GMAIL_APP_PASSWORD ADMIN_KEY \
         MS_ADMIN_KEY MS_MAINT_KEY MS_REVIEW_SECRET EMAIL_INBOUND_SECRET \
         RELAY_INBOUND_SECRET CF_CACHE_TOKEN ANTHROPIC_API_KEY OPENAI_API_KEY \
         TRAVELPAYOUTS_TOKEN HETZNER_S3_ACCESS_KEY HETZNER_S3_SECRET_KEY \
         PAYSTACK_WEBHOOK_SECRET ALLOW_TEST_PAYMENTS; do
  ine=$(grep -c "^$n=" .env 2>/dev/null)
  inp=$(grep -c "^$n$" /tmp/_procenv 2>/dev/null)
  if   [ "$ine" -gt 0 ] && [ "$inp" -gt 0 ]; then v="ok"
  elif [ "$ine" -gt 0 ] && [ "$inp" -eq 0 ]; then v="*** .env only - bare os.getenv sees NOTHING ***"
  elif [ "$ine" -eq 0 ] && [ "$inp" -gt 0 ]; then v="process only (set in the unit)"
  else v="absent everywhere"; fi
  printf "  %-26s %-8s %-10s %s\n" "$n" "$ine" "$inp" "$v"
done
rm -f /tmp/_procenv
echo
echo "=== money path posture ==="
if grep -q '^PAYSTACK_SECRET_KEY=sk_live' .env 2>/dev/null; then echo "  .env holds a LIVE Paystack key"
elif grep -q '^PAYSTACK_SECRET_KEY=sk_test' .env 2>/dev/null; then echo "  .env holds a TEST Paystack key - real payments will NOT credit"
else echo "  no PAYSTACK_SECRET_KEY line in .env"; fi
echo -n "  app self-check: "; curl -s "http://localhost:8000/health" >/dev/null && echo "BEA responding" || echo "BEA NOT responding"
