#!/bin/bash
# audit_env_file.sh - prove Paystack auth + audit /etc/environment. NO SECRET VALUES.
fp() { printf '%s' "$1" | sha256sum | cut -c1-8; }

echo "  === 1. does the new Paystack key authenticate? ==="
p=$(systemctl show -p MainPID --value marketsquare)
l=$(tr '\0' '\n' < /proc/$p/environ | grep '^PAYSTACK_SECRET_KEY=' | head -1 | cut -d= -f2-)
code=$(curl -s -o /dev/null -w '%{http_code}' https://api.paystack.co/transaction/totals -H "Authorization: Bearer $l")
echo "  [--] Paystack replied HTTP $code"
case "$code" in
  200) echo "  [OK] AUTH PASSED - payments are back up on the new key" ;;
  401) echo "  [X]  KEY REJECTED - still broken" ;;
  *)   echo "  [?]  unexpected code $code" ;;
esac

echo
echo "  === 2. what else is sitting in /etc/environment? ==="
e=/etc/environment
if [ ! -f "$e" ]; then echo "  [OK] no /etc/environment file"; exit 0; fi
echo "  [--] permissions: $(stat -c '%a  owner=%U  group=%G' $e)"
case "$(stat -c %a $e)" in
  644|664|666|755) echo "  [!!] WORLD-READABLE - any user or process on this box can read it" ;;
  600|640) echo "  [OK] not world-readable" ;;
esac
echo "  [--] secret-looking entries (name + fingerprint only):"
n=0
while IFS= read -r line; do
  case "$line" in \#*|"") continue;; esac
  k=$(printf '%s' "$line" | cut -d= -f1 | tr -d ' "')
  v=$(printf '%s' "$line" | cut -d= -f2- | tr -d '"')
  case "$k" in
    *KEY*|*SECRET*|*TOKEN*|*PASSWORD*|*SALT*|*PASS*)
      echo "      $k  fingerprint $(fp "$v")"; n=$((n+1)) ;;
    *) echo "      $k  (not secret-shaped: PATH-like, left alone)" ;;
  esac
done < "$e"
echo "  [--] $n secret-shaped entr(y/ies) in a box-wide file"
