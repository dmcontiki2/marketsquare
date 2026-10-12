#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 3/8 -- route_policy.json: declare the three new routes (SEC-GATE-1)."""
import os, json
from patchlib import load, save, rep, root

R = root()
P = os.path.join(R, "route_policy.json")
s, crlf, orig = load(P)
if "/payment/seller-subscription/cancel" in s:
    print("route_policy.json already declares the cancel route -- skipped")
    raise SystemExit(0)
n_before = len(json.loads(s)["routes"])
s = rep(s, '''  {
   "key": "GET /payment/seller-subscription/verify",
   "level": "public",
   "hide": [
    "email"
   ]
  },
''', '''  {
   "key": "GET /payment/seller-subscription/verify",
   "level": "public",
   "hide": [
    "email"
   ]
  },
  {
   "key": "POST /payment/seller-subscription/cancel",
   "level": "user",
   "bind": [
    {
     "name": "email",
     "in": "json"
    }
   ],
   "note": "AUTO-RENEW-1 (RUL-224, 12 Oct 2026): Cancel renewal. Acts only as the signed-in session -- a typed email is rewritten to it, so nobody can stop another seller's renewal."
  },
  {
   "key": "POST /payment/seller-subscription/resume",
   "level": "user",
   "bind": [
    {
     "name": "email",
     "in": "json"
    }
   ],
   "note": "AUTO-RENEW-1 (RUL-224, 12 Oct 2026): Renew again (undo a Cancel renewal while the paid period runs). Acts only as the signed-in session."
  },
  {
   "key": "POST /admin/auto-renew/plans",
   "level": "admin",
   "note": "AUTO-RENEW-1 (RUL-224, 12 Oct 2026): maintenance -- make or adopt the Paystack plan per paid tier. Admin credential only; called by scripts/paystack_plans_sync.py."
  },
''')
d = json.loads(s)
keys = [r["key"] for r in d["routes"]]
assert len(keys) == len(set(keys)) == n_before + 3, "route keys not unique or count off"
save(P, s, crlf, orig)
print("route_policy.json OK (%d -> %d routes, valid JSON, keys unique)" % (n_before, len(keys)))
