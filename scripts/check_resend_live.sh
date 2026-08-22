#!/bin/bash
# check_resend_live.sh - does the key the server holds still authenticate to Resend?
# Empty-body send probe (INFRA-RESEND-1): 422 = auth PASSED, nothing sent.
# 401/403 = key is dead. PRINTS NO SECRET VALUES.
f=/etc/systemd/system/marketsquare.service.d/resend.conf
v=$(grep -o 'RESEND_API_KEY=.*' "$f" | head -1 | cut -d= -f2-)
if [ -z "$v" ]; then echo "  [X]  no key found in resend.conf"; exit 1; fi
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST https://api.resend.com/emails \
        -H "Authorization: Bearer $v" -H "Content-Type: application/json" -d '{}')
echo "  [--] Resend replied HTTP $code"
case "$code" in
  422) echo "  [OK] AUTH PASSED - the new key is live and able to send. Nothing was sent." ;;
  401|403) echo "  [X]  KEY REJECTED - the server is holding a dead key. Mail is DOWN." ;;
  000) echo "  [?]  no reply - network/DNS problem reaching Resend, not a key verdict" ;;
  *) echo "  [?]  unexpected code - tell Claude" ;;
esac
