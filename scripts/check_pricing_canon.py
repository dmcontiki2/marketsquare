#!/usr/bin/env python3
"""
check_pricing_canon.py — drift guard for TrustSquare pricing.

The running code constants are the authority. This reads them, checks them against
the canonical values in PRICING_CANON.md, and confirms the key derived docs (A7
requirements, EULA) carry the CURRENT numbers and not RETIRED ones.

Exit 0 = everything in line.  Exit 1 = drift (the mismatch is printed).
Run:  python scripts/check_pricing_canon.py
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)            # MarketSquare/
PROJ = os.path.dirname(ROOT)            # Projects/ (siblings: Codices, AdvertAgent, CityLauncher)

# ---- CANONICAL VALUES (must mirror PRICING_CANON.md) ----
EXPECTED_SELLER = {"free": (0, 2), "starter": (5, 10), "pro": (20, 30), "agency": (0, 10)}  # tier: (usd, slots)
EXPECTED_TUP    = {"starter": 2, "pro": 10}     # monthly Tuppence
EXPECTED_BUYER  = (5, 90)                        # Global usd, zar
EXPECTED_BADGE  = ("pro",)

fails = []
def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if (detail and not ok) else ""))
    if not ok: fails.append(name)
def read(p):
    try: return open(p, encoding="utf-8").read()
    except FileNotFoundError: return None

print("TrustSquare pricing-canon check\n" + "=" * 42)
bea = read(os.path.join(ROOT, "bea_main.py")) or ""
lr  = read(os.path.join(ROOT, "launch_redemption.py")) or ""

print("\n1. Code constants (the authority):")
for tier, (usd, slots) in EXPECTED_SELLER.items():
    m = re.search(rf'"{tier}":\s*\{{[^}}]*"slot_limit":\s*(\d+)[^}}]*"usd":\s*(\d+)', bea)
    got = (int(m.group(2)), int(m.group(1))) if m else None
    check(f"seller {tier} = ${usd} / {slots} slots", got == (usd, slots), f"code={got}")
mu = re.search(r'WISHLIST_GLOBAL_USD\s*=\s*(\d+)', bea)
mz = re.search(r'WISHLIST_GLOBAL_ZAR\s*=\s*(\d+)', bea)
got = (int(mu.group(1)) if mu else None, int(mz.group(1)) if mz else None)
check(f"buyer Global = ${EXPECTED_BUYER[0]} / R{EXPECTED_BUYER[1]}", got == EXPECTED_BUYER, f"code={got}")
seg = lr.split("TIER_TUPPENCE_MONTHLY", 1)[-1][:220]
for tier, t in EXPECTED_TUP.items():
    m = re.search(rf'"{tier}":\s*(\d+)', seg)
    check(f"{tier} monthly = {t}T", bool(m) and int(m.group(1)) == t, f"code={m.group(1) if m else '??'}")
mq = re.search(r'QUALIFYING_TIERS\s*=\s*\(([^)]*)\)', lr)
qt = tuple(x.strip().strip('"\'') for x in mq.group(1).split(",") if x.strip()) if mq else ()
check(f"badge mints on {EXPECTED_BADGE}", qt == EXPECTED_BADGE, f"code={qt}")

print("\n2. PRICING_CANON.md mirrors the code:")
canon = read(os.path.join(ROOT, "PRICING_CANON.md")) or ""
check("canon: Pro $20 / 30 / 10T", all(x in canon for x in ["$20", "30", "10T"]))
check("canon: Starter $5 / 10 / 2T", all(x in canon for x in ["$5", "10", "2T"]))
check("canon: buyer Global $5 / R90", "Global" in canon and "$5" in canon and "R90" in canon)
check("canon: badge on $20 Pro", '$20 Pro' in canon and 'QUALIFYING_TIERS = ("pro",)' in canon)

print("\n3. Derived docs in line (current present, retired absent):")
a7 = [os.path.join(ROOT, "docs/PRINCIPLE_REQUIREMENTS.md"),
      os.path.join(PROJ, "Codices/PRINCIPLE_REQUIREMENTS.md"),
      os.path.join(PROJ, "AdvertAgent/PRINCIPLE_REQUIREMENTS.md"),
      os.path.join(PROJ, "CityLauncher/PRINCIPLE_REQUIREMENTS.md")]
for p in a7:
    s = read(p)
    if s is None: print(f"  [skip] {os.path.relpath(p, PROJ)} (not found)"); continue
    check(f"A7 {os.path.relpath(p, PROJ)}", "Global: $5/mo" in s and "$15/mo · 50/day" not in s)
for p in [os.path.join(ROOT, "eula_clean.html"), os.path.join(ROOT, "eula_raw.html")]:
    s = read(p)
    if s is None: print(f"  [skip] {os.path.basename(p)}"); continue
    check(f"EULA {os.path.basename(p)}", "Global — $5/month" in s and "Premium — $15/month" not in s)

print("\n" + "=" * 42)
if fails:
    print(f"DRIFT DETECTED — {len(fails)} check(s) failed. Fix the source to match PRICING_CANON.md, then re-run.")
    sys.exit(1)
print("ALL IN LINE ✓  code ↔ PRICING_CANON.md ↔ derived docs agree.")
sys.exit(0)
