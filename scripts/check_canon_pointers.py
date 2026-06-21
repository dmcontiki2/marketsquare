#!/usr/bin/env python3
"""
check_canon_pointers.py — drift guard for TrustSquare CANON POINTERS & doc integrity.

Companion to check_pricing_canon.py (which guards the pricing numbers). This one reads
canon.yml (the single machine-readable source) and asserts the docs match it:
  1. the 5 PRINCIPLE_REQUIREMENTS copies are all present and md5-identical (no divergence),
  2. version pointers in the docs name the CANON versions (Codex/briefing) — no stale ones,
  3. no drift-marker strings (legacy prices, retired threshold, old Codex names) survive,
  4. LEGAL_VERSIONS.md agrees with canon.yml.

Exit 0 = in line.  Exit 1 = drift (each mismatch is printed).
Run:  python scripts/check_canon_pointers.py
"""
import os, sys, hashlib, yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # MarketSquare/

def resolve(rel):
    """Find a path that is relative to ROOT, tolerating Windows (siblings under Projects/)
    and the sandbox (siblings mounted under ../Projects/)."""
    cands = [os.path.normpath(os.path.join(ROOT, rel))]
    if rel.startswith("../"):
        cands.append(os.path.normpath(os.path.join(ROOT, "..", "Projects", rel[3:])))
    for c in cands:
        if os.path.exists(c):
            return c
    return None

def read(p):
    try: return open(p, encoding="utf-8").read()
    except (FileNotFoundError, TypeError): return None

def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

fails = []
def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if (detail and not ok) else ""))
    if not ok: fails.append(name)

canon = yaml.safe_load(read(os.path.join(ROOT, "canon.yml")) or "{}")
V = canon.get("versions", {})
print("TrustSquare canon-pointer check\n" + "=" * 44)

# 1. Requirements mirror integrity (P1)
print("\n1. Requirements: one source, identical mirrors:")
canonical = os.path.join(ROOT, canon.get("requirements_canonical", "PRINCIPLE_REQUIREMENTS.md"))
base = md5(canonical) if os.path.exists(canonical) else None
check("canonical PRINCIPLE_REQUIREMENTS.md present", base is not None)
for rel in canon.get("requirements_mirrors", []):
    p = resolve(rel)
    if not p:
        print(f"  [skip] {rel} (not found on this host)"); continue
    check(f"mirror == canonical: {rel}", base is not None and md5(p) == base, "md5 differs")

# 2. Version pointers name the CANON (P2)
print("\n2. Version pointers match canon.yml:")
req = read(canonical) or ""
check(f"requirements names Codex {V.get('codex')}", V.get("codex","") in req)
check(f"requirements names briefing {V.get('agent_briefing')}", V.get("agent_briefing","") in req)
check("requirements carries no _DRAFT Codex pointer", "v4_8_DRAFT" not in req)
for rel in ["CLAUDE.md", "../Codices/CLAUDE.md"]:
    p = resolve(rel) if rel.startswith("..") else os.path.join(ROOT, rel)
    s = read(p)
    if s is None:
        print(f"  [skip] {rel} (not found)"); continue
    check(f"{rel} names canon Codex (not v4_5)", V.get("codex","") in s and "Codex_v4_5.docx" not in s)

# 3. No drift markers survive anywhere live (P2/P8)
print("\n3. No drift markers in live docs:")
scan = [canonical, os.path.join(ROOT, "PRICING_CANON.md"), os.path.join(ROOT, "CLAUDE.md")]
scan += [resolve(r) for r in canon.get("requirements_mirrors", [])]
scan += [resolve("../Codices/CLAUDE.md")]
blobs = [(os.path.relpath(p, ROOT), read(p)) for p in scan if p and read(p) is not None]
for marker in canon.get("drift_markers", []):
    hits = [rel for rel, b in blobs if marker in b]
    check(f"absent: {marker!r}", not hits, "in " + ", ".join(hits))

# 4. LEGAL_VERSIONS.md agrees with canon.yml (P10)
print("\n4. Legal/version register agrees with canon.yml:")
lv = read(os.path.join(ROOT, "LEGAL_VERSIONS.md"))
if lv is None:
    check("LEGAL_VERSIONS.md present", False)
else:
    for k in ("codex", "requirements", "agent_briefing", "eula", "ip_brief", "whitepaper"):
        v = str(V.get(k, ""))
        check(f"register lists {k} = {v}", v in lv, "missing/mismatched")

# 5. Codex canon artifact present
print("\n5. Canon artifacts present:")
check(f"{V.get('codex')} on disk", os.path.exists(os.path.join(ROOT, V.get("codex",""))))

print("\n" + "=" * 44)
if fails:
    print(f"DRIFT DETECTED — {len(fails)} check(s) failed. Update the source to match canon.yml, then re-run.")
    sys.exit(1)
print("ALL IN LINE ✓  docs ↔ canon.yml agree; mirrors identical.")
sys.exit(0)
