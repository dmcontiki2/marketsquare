#!/usr/bin/env python3
"""
propagate_requirements.py — make the requirement mirrors GENERATED, not hand-edited (P1).

Copies the single canonical PRINCIPLE_REQUIREMENTS.md to every mirror listed in canon.yml
and verifies md5 identity. Run this after editing the canonical; never edit a mirror by hand.

Exit 0 = all mirrors identical (synced or already in line).  Exit 1 = a mirror dir is missing.
Run:  python scripts/propagate_requirements.py
"""
import os, sys, hashlib, shutil, yaml
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
def resolve(rel):
    cands = [os.path.normpath(os.path.join(ROOT, rel))]
    if rel.startswith("../"):
        cands.append(os.path.normpath(os.path.join(ROOT, "..", "Projects", rel[3:])))
    for c in cands:
        if os.path.isdir(os.path.dirname(c)): return c
    return None
def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()
canon = yaml.safe_load(open(os.path.join(ROOT, "canon.yml"), encoding="utf-8").read())
canonical = os.path.join(ROOT, canon["requirements_canonical"])
if not os.path.exists(canonical):
    print("FATAL: canonical not found:", canonical); sys.exit(1)
base = md5(canonical); print(f"canonical: {canon['requirements_canonical']}  md5={base[:8]}")
synced = already = missing = 0
for rel in canon.get("requirements_mirrors", []):
    p = resolve(rel)
    if p is None:
        print(f"  [MISS] {rel} — target dir not found"); missing += 1; continue
    if os.path.exists(p) and md5(p) == base:
        print(f"  [ok]   {rel} (identical)"); already += 1; continue
    shutil.copyfile(canonical, p)
    ok = md5(p) == base
    print(f"  [{'sync' if ok else 'FAIL'}] {rel}"); synced += 1 if ok else 0
print(f"\n{already} already in line · {synced} synced · {missing} missing-dir")
sys.exit(1 if missing else 0)
