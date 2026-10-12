#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 6/8 -- scripts/regression_ledger.py: RG-0964 (the machinery, LOCKED), RG-0965 (EXECUTED proof,
LOCKED), RG-0966 (LIVE, OPEN until deployed). Appended after the last entry; nothing renumbered, nothing weakened."""
import os, py_compile, ast
from patchlib import load, save, rep, root

HERE = os.path.dirname(os.path.abspath(__file__))
R = root()
P = os.path.join(R, "scripts", "regression_ledger.py")
s, crlf, orig = load(P)
if '"RG-0964"' in s:
    print("regression_ledger.py already carries RG-0964 -- skipped")
    raise SystemExit(0)
for rid in ("RG-0964", "RG-0965", "RG-0966"):
    assert rid not in s, rid + " is already taken"
block = open(os.path.join(HERE, "ledger_block.txt"), encoding="utf-8").read()
s = rep(s, "\ndef _server_vantage_wrap():\n", "\n" + block + "def _server_vantage_wrap():\n")
ast.parse(s)
save(P, s, crlf, orig)
py_compile.compile(P, doraise=True)
print("regression_ledger.py OK (ast + py_compile)")
