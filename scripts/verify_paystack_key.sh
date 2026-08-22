#!/bin/bash
# verify_paystack_key.sh - after rotation. PRINTS NO SECRET VALUES.
fp() { printf '%s' "$1" | sha256sum | cut -c1-8; }
d=/etc/systemd/system/marketsquare.service.d
a=$(grep -ho 'PAYSTACK_SECRET_KEY=.*'     $d/*.conf 2>/dev/null | head -1 | cut -d= -f2-)
b=$(grep -ho 'PAYSTACK_WEBHOOK_SECRET=.*' $d/*.conf 2>/dev/null | head -1 | cut -d= -f2-)
p=$(systemctl show -p MainPID --value marketsquare)
l=$(tr '\0' '\n' < /proc/$p/environ | grep '^PAYSTACK_SECRET_KEY=' | head -1 | cut -d= -f2-)
echo "  [--] service          : $(systemctl is-active marketsquare)"
[ -n "$a" ] && echo "  [OK] SECRET_KEY       fingerprint $(fp "$a")" || echo "  [X]  PAYSTACK_SECRET_KEY not on disk"
[ -n "$b" ] && echo "  [OK] WEBHOOK_SECRET   fingerprint $(fp "$b")" || echo "  [X]  PAYSTACK_WEBHOOK_SECRET not on disk"
[ -n "$l" ] && echo "  [OK] live process     fingerprint $(fp "$l")" || echo "  [X]  live process has NO Paystack key"
if [ -n "$a" ] && [ "$a" = "$b" ] && [ "$a" = "$l" ]; then echo "  [OK] all three MATCH - one key, everywhere, loaded"; else echo "  [X]  MISMATCH - the three do not agree"; fi
case "$l" in sk_live*) echo "  [OK] it is a LIVE key (real payments will grant entitlements)";;
             sk_test*) echo "  [!!] it is a TEST key - entitlement gate will refuse to grant";;
             *) echo "  [?]  unrecognised key prefix";; esac
code=$(curl -s -o /dev/null -w '%{http_code}' https://api.paystack.co/transaction/totals -H "Authorization: Bearer $l")
echo "  [--] Paystack replied HTTP $code"
case "$code" in 200) echo "  [OK] AUTH PASSED - the new key is live and working";;
                401) echo "  [X]  KEY REJECTED - Paystack does not accept this key";;
                *) echo "  [?]  unexpected - tell Claude";; esac
