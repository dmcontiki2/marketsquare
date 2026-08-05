#!/usr/bin/env python3
"""peer_pack_ai.py — build the Peer's bea_main.py evidence extract (5 Aug 2026).

WHY: peer_review.py caps input at 120 KB/file, 400 KB total — bea_main.py is 850 KB,
so shipping it whole truncates at ~14% and crowds out everything else (the Peer's own
complaint, 5 Aug 2026: application-level findings could not be confirmed). This builds
a TARGETED extract of every AI-relevant section, each line prefixed with its REAL line
number in bea_main.py so the Peer's citations stay checkable. Regenerated fresh on
every PEER_AUDIT_AI_SERVICES.bat run — it can never go stale.
Stdlib only. Output: Records/PEER_PACK_BEA_EXTRACT.md (overwritten each run).
"""
import os, re, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "bea_main.py")

SECTIONS = [
    ("Breaker wiring at BEA startup (attach + alert hook)", r"import ai_breaker as _ai_brk", 22),
    ("ai_spend_config schema + ceiling columns", r"CREATE TABLE IF NOT EXISTS ai_spend_config", 70),
    ("Spend logging, alerting, cost ceiling", r"def _log_ai_spend", 160),
    ("Active provider switch + pin/override (TTL decay)", r"AI_OVERRIDE_TTL_HOURS", 60),
    ("Tuppence helpers (deduct / balance / pre-flight require)", r"def _deduct_tuppence", 50),
    ("AI1 Listing Rewrite (full endpoint)", r"async def ai_listing_rewrite", 100),
    ("AI2 Seller Audit (full endpoint)", r"async def ai_seller_audit", 115),
    ("AI3 Price Check (charge logic + integrity model)", r"async def ai_price_check", 260),
    ("AI4 Yield (deliver-then-charge reference)", r"async def ai_yield_calc", 200),
    ("AI5 Batch Cards (full endpoint)", r"async def ai_batch_card_listings", 150),
    ("KYC identity verification (vision, cost-guarded)", r"async def _sonnet_verify_identity", 110),
    ("/admin/ai-restore + /flags provider block", r'@app\.post\("/admin/ai-restore"\)', 150),
    ("/admin/ai-spend summary endpoint", r'@app\.get\("/admin/ai-spend/summary"\)', 55),
    ("Scoreboard nightly wiring + HEARTBEAT-1 idle-recovery loop", r"SCOREBOARD-1 \(3 Aug 2026\)", 110),
]

def main():
    lines = open(SRC, encoding="utf-8", errors="replace").read().splitlines()
    out = ["# PEER PACK — bea_main.py targeted extract",
           "",
           "*Generated %s UTC from bea_main.py (%d lines). Each line keeps its REAL line number*"
           % (datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"), len(lines)),
           "*so citations are checkable against the repo. Sections chosen for the AI services audit;*",
           "*anything outside them is available on request — say which line range you need.*", ""]
    grepped = [i + 1 for i, ln in enumerate(lines) if "any_lane_configured()" in ln and "if not" in ln]
    out += ["## Vendor-neutral endpoint gates (F1 fix) — all occurrences",
            "", "Lines gating with `if not ai_provider.any_lane_configured():` -> " + str(grepped), ""]
    for label, pat, n in SECTIONS:
        rx = re.compile(pat)
        idx = next((i for i, ln in enumerate(lines) if rx.search(ln)), None)
        out.append("## " + label)
        out.append("")
        if idx is None:
            out.append("_ANCHOR NOT FOUND: %s — report this as a finding._" % pat)
            out.append("")
            continue
        start = max(0, idx - 2)
        out.append("```python")
        for j in range(start, min(len(lines), start + n)):
            out.append("%6d  %s" % (j + 1, lines[j]))
        out.append("```")
        out.append("")
    dest = os.path.join(REPO, "Records", "PEER_PACK_BEA_EXTRACT.md")
    open(dest, "w", encoding="utf-8", newline="").write("\n".join(out) + "\n")
    print("extract written: %s (%d KB)" % (dest, len("\n".join(out)) // 1024))

if __name__ == "__main__":
    main()
