#!/usr/bin/env python3
"""peer_pack_ai.py v3 — build the Peer's evidence extract (5 Aug 2026).

WHY: peer_review.py caps input at 120 KB/file; bea_main.py is 850 KB. This builds a
TARGETED extract, each line prefixed with its REAL line number so citations stay
checkable. v3 adds: admin-auth dependency, transactions schema (database.py), the
user-facing copy excerpts (marketsquare.html card, dashboard VIZ legend), and a
COMPUTED TOTALITY EVIDENCE section (grep-derived; the Peer should treat it as the
Author's claim and spot-check via requested line ranges — a targeted extract cannot
prove a negative over the whole file).
Regenerated fresh on every PEER_AUDIT_AI_SERVICES.bat run. Stdlib only.
Output: Records/PEER_PACK_BEA_EXTRACT.md (overwritten each run).
"""
import os, re, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (file, section label, anchor regex, lines)
SECTIONS = [
    ("bea_main.py", "Admin auth dependency (used by /admin/ai-* endpoints)", r"def _require_admin_or_key", 30),
    ("bea_main.py", "Breaker wiring at BEA startup (attach + alert hook)", r"import ai_breaker as _ai_brk", 22),
    ("database.py", "transactions table schema (Tuppence ledger)", r"CREATE TABLE IF NOT EXISTS transactions", 25),
    ("bea_main.py", "ai_spend_config schema + ceiling columns", r"CREATE TABLE IF NOT EXISTS ai_spend_config", 70),
    ("bea_main.py", "Spend logging, alerting, cost ceiling", r"def _log_ai_spend", 160),
    ("bea_main.py", "Active provider switch + pin/override (TTL decay)", r"AI_OVERRIDE_TTL_HOURS", 60),
    ("bea_main.py", "Tuppence helpers (deduct / balance / pre-flight require)", r"def _deduct_tuppence", 50),
    ("bea_main.py", "AI1 Listing Rewrite (full endpoint)", r"async def ai_listing_rewrite", 100),
    ("bea_main.py", "AI2 Seller Audit (full endpoint)", r"async def ai_seller_audit", 115),
    ("bea_main.py", "AI3 Price Check (charge logic + integrity model)", r"async def ai_price_check", 260),
    ("bea_main.py", "AI4 Yield (deliver-then-charge reference)", r"async def ai_yield_calc", 200),
    ("bea_main.py", "AI5 Batch Cards (full endpoint)", r"async def ai_batch_card_listings", 150),
    ("bea_main.py", "KYC identity verification (vision, cost-guarded)", r"async def _sonnet_verify_identity", 110),
    ("bea_main.py", "/admin/ai-restore + /flags provider block", r'@app\.post\("/admin/ai-restore"\)', 150),
    ("bea_main.py", "/admin/ai-spend summary endpoint", r'@app\.get\("/admin/ai-spend/summary"\)', 55),
    ("bea_main.py", "Scoreboard nightly wiring + HEARTBEAT-1 idle-recovery loop", r"SCOREBOARD-1 \(3 Aug 2026\)", 110),
    ("marketsquare.html", "AI Services help card copy (user-facing, F3 vendor-neutral fix)", r"AI Listing Rewrite", 55),
    ("dashboard.server.html", "VIZ map legend naming Sonnet (F4 context: display text, not a call site)", r"Task tiers:\s+haiku sky", 45),
]

def main():
    cache = {}
    def flines(name):
        if name not in cache:
            cache[name] = open(os.path.join(REPO, name), encoding="utf-8",
                               errors="replace").read().splitlines()
        return cache[name]

    bea = flines("bea_main.py")
    out = ["# PEER PACK — targeted evidence extract (v3)",
           "",
           "*Generated %s UTC. Each line keeps its REAL line number in its source file so*"
           % datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
           "*citations are checkable. If a section you need is absent, name the exact file and*",
           "*line range as a finding and it will be supplied next run.*", ""]

    out += ["## COMPUTED TOTALITY EVIDENCE (Author-derived greps over the full bea_main.py — "
            "treat as claims; spot-check by requesting ranges)", ""]
    hosts = {h: sum(h in ln for ln in bea) for h in
             ("api.anthropic.com", "api.openai.com", "api.scaleway.ai")}
    out.append("- Vendor inference hosts named in bea_main.py (%d lines): %s"
               % (len(bea), hosts))
    gates_old = [i + 1 for i, ln in enumerate(bea) if "if not ANTHROPIC_API_KEY" in ln]
    gates_new = [i + 1 for i, ln in enumerate(bea) if "any_lane_configured()" in ln and "if not" in ln]
    out.append("- Old vendor-specific gates ('if not ANTHROPIC_API_KEY') remaining: %s" % (gates_old or "NONE"))
    out.append("- Vendor-neutral gates ('if not ai_provider.any_lane_configured()'): %d at lines %s"
               % (len(gates_new), gates_new))
    calls = [i + 1 for i, ln in enumerate(bea) if "ai_provider.complete" in ln]
    out.append("- Every line invoking ai_provider.complete: %s" % calls)
    deducts = [i + 1 for i, ln in enumerate(bea) if "_deduct_tuppence(" in ln and "def " not in ln]
    out.append("- Every _deduct_tuppence call line: %s" % deducts)
    out.append("")

    for fname, label, pat, n in SECTIONS:
        rx = re.compile(pat)
        try:
            lines = flines(fname)
        except OSError as e:
            out += ["## " + label, "", "_FILE NOT READABLE: %s (%s)_" % (fname, e), ""]
            continue
        idx = next((i for i, ln in enumerate(lines) if rx.search(ln)), None)
        out.append("## %s — from %s" % (label, fname))
        out.append("")
        if idx is None:
            out.append("_ANCHOR NOT FOUND: %s — report this as a finding._" % pat)
            out.append("")
            continue
        start = max(0, idx - 2)
        out.append("```")
        for j in range(start, min(len(lines), start + n)):
            out.append("%6d  %s" % (j + 1, lines[j]))
        out.append("```")
        out.append("")
    dest = os.path.join(REPO, "Records", "PEER_PACK_BEA_EXTRACT.md")
    body = "\n".join(out) + "\n"
    open(dest, "w", encoding="utf-8", newline="").write(body)
    print("extract written: %s (%d KB)" % (dest, len(body) // 1024))

if __name__ == "__main__":
    main()
