#!/usr/bin/env python3
"""
cc_age_check.py — surface change-control (CC) packages open too long (P6, for the daily brief).

Parses CHANGE_REGISTER.md: a CC is "resolved" if its Stage says LANDED/ACCEPTED/CLOSED/DONE/
SUPERSEDED; otherwise it is open. Open CCs older than THRESHOLD days are surfaced so a staged
package can't sit forgotten (CC-001/002 once sat 9-11 days).

Always exits 0 (informational). Prints the aged list for the morning brief.
Run:  python scripts/cc_age_check.py
"""
import os, re, sys, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
THRESHOLD = 7
MONTHS = {m: i for i, m in enumerate(
    ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
text = open(os.path.join(ROOT, "CHANGE_REGISTER.md"), encoding="utf-8").read()
today = datetime.date.today()
RESOLVED = ("LANDED", "ACCEPTED", "CLOSED", "DONE", "SUPERSEDED")
# split into CC sections
parts = re.split(r'\n##\s+(CC-\d+[^\n]*)\n', text)
aged, open_recent, resolved = [], [], []
for i in range(1, len(parts), 2):
    header, body = parts[i], parts[i+1]
    cid = re.match(r'(CC-\d+)', header).group(1)
    mstage = re.search(r'\*\*Stage:\*\*\s*([^\n]+)', body)
    stage = (mstage.group(1) if mstage else "")[:70]
    is_resolved = any(k in (stage.upper()) for k in RESOLVED)
    md = re.search(r'Opened:\*?\*?\s*(\d{1,2})\s+([A-Za-z]{3})[a-z]*\s+(\d{4})', body)
    if md is None:
        continue  # not a real CC package (e.g. an interaction note) — skip
    days = None
    if md:
        d = datetime.date(int(md.group(3)), MONTHS.get(md.group(2)[:3].title(), 1), int(md.group(1)))
        days = (today - d).days
    if is_resolved:
        resolved.append(cid)
    elif days is not None and days > THRESHOLD:
        aged.append((cid, days, stage))
    else:
        open_recent.append(cid)
print("Change-control ageing (threshold {}d, today {}):".format(THRESHOLD, today))
if aged:
    for cid, days, stage in sorted(aged, key=lambda x: -x[1]):
        print(f"  ⏳ {cid} — open {days}d — {stage.strip()}")
else:
    print("  none aged ✓")
print(f"  (resolved: {', '.join(resolved) or '-'} · recent-open: {', '.join(open_recent) or '-'})")
sys.exit(0)
