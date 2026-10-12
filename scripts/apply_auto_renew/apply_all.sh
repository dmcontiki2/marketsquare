#!/bin/bash
# AUTO-RENEW-1 (RUL-224, 12 Oct 2026): apply every patch to the repo, in order.
# Each patch is an asserted-unique string replacement, keeps a .bak-autorenew-<ts> copy, verifies itself
# (py_compile / node --check / JSON parse / tail check) and is idempotent: a file that already carries the
# change is skipped. Usage:  bash scripts/apply_auto_renew/apply_all.sh [repo root]
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${1:-$(cd "$HERE/../.." && pwd)}"
export AR_TS="${AR_TS:-$(date -u +%Y%m%d-%H%M%S)}"
cd "$HERE"
for p in p1_payments p2_bea p3_route_policy p4_ms_js p5_dashboard p6_ledger p7_rulings p8_docs; do
  echo "== $p"; python3 "$p.py" "$ROOT"
done
