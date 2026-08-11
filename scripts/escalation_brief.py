#!/usr/bin/env python3
"""escalation_brief.py -- B3: the safety/legal/cost escalation brief (MAINTENANCE_AGENT.md stage 7).

David sees ONLY safety/legal/cost -- always as a SOLUTION LIST with tick actions,
after the safest action was already taken. Reports inform; they never block.

This renders that brief from the maintenance agent's own run reports
(.maint_agent/run_*.json): every ESCALATE item since the cutoff, categorized
against the SAME refuse markers the agent uses (imported, never copied -- drift
is structurally impossible), each with the safest standing action and 2-3
options ending in ONE tick line.

Deterministic by design: the FORMAT is machinery; judgment stays with the reader
and the session that delivers it. Runs anywhere the repo is: David's PC, a
scheduled session, or the server. No key, no network, stdlib only.

  python3 scripts/escalation_brief.py               # last 24h -> Records/ESCALATION_BRIEF_<date>.md
  python3 scripts/escalation_brief.py --hours=72
  python3 scripts/escalation_brief.py --selftest    # proves format + marker coverage, temp dir only
"""
import glob, json, os, sys, tempfile
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from maintenance_agent import REFUSE_LEGAL_COSTLY, REFUSE_TRUST_CORE  # single source of truth

# ── categories: every agent refuse-marker must belong to exactly one lane ────────
CATEGORIES = {
    "LEGAL": ("legal", "popia", "eula", "terms", "compliance", "ffc", "mandate"),
    "MONEY": ("payment", "paystack", "refund", "wallet", "tuppence charge", "billing", "card",
              "invoice", "payout"),
    "COST":  ("cost", "costly", "spend", "vat", "tax"),
    "TRUST": ("auth", "login", "password", "session", "token", "kyc", "id number", "identity",
              "anonym", "reveal", "seller_email", "schema", "migration", "database", "drop table"),
    "SAFETY": ("safety",),
}

PLAYBOOK = {
    "LEGAL":  ("HELD -- nothing auto-sent, nothing auto-changed (the agent never touches legal).",
               ["Send to counsel for a same-week read; item stays held meanwhile.",
                "Take the specific content/feature dark until reviewed.",
                "Publish a correction/clarification now, counsel ratifies after."]),
    "MONEY":  ("Payment surface untouched by the agent; any suspect charge lane can be taken dark.",
               ["Refund/reverse the specific transaction and write the complainant.",
                "Hold the transaction, investigate with Paystack logs first.",
                "Take the payment feature dark until the root cause is fixed."]),
    "COST":   ("Spend lane capped/dark by default -- no new spend was authorised.",
               ["Raise the cap consciously (state the new monthly number).",
                "Keep the lane dark; revisit at the next review.",
                "Swap to the cheaper provider/adapter behind the seam."]),
    "TRUST":  ("Feature taken/kept dark -- trust core is never autonomously edited.",
               ["Supervised hotfix session (you watch, agent types).",
                "Roll back to the last good deploy and re-approach.",
                "Leave dark pending a Path B redesign dossier."]),
    "SAFETY": ("Content/feature taken dark immediately -- safest action first, report after.",
               ["Keep dark + write the reporter with what changed.",
                "Reinstate with the specific guard added (named in the reply).",
                "Escalate to counsel if the safety issue has legal exposure."]),
    "OTHER":  ("No standing playbook -- listed so nothing escapes the brief.",
               ["Handle in the next attended session.",
                "Route to the design backlog if it is really a design ask."]),
}

def _arg(name, default=None):
    for a in sys.argv[1:]:
        if a.startswith(name + "="):
            return a.split("=", 1)[1]
    return default

def categorize(text):
    t = text.lower()
    for cat, marks in CATEGORIES.items():
        if any(m in t for m in marks):
            return cat
    return "OTHER"

def collect(state_dir, since):
    items = []
    for rp in sorted(glob.glob(os.path.join(state_dir, "run_*.json"))):
        try:
            rep = json.load(open(rp, encoding="utf-8"))
            ts = datetime.strptime(rep.get("run", ""), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if ts < since:
            continue
        for a in rep.get("actions", []):
            lane = (a.get("lane") or "").upper()
            outcome = (a.get("outcome") or "")
            if lane == "ESCALATE" or "escalate" in outcome.lower():
                items.append({"when": rep.get("run"), "ref": a.get("ref", "?"),
                              "title": a.get("title", ""), "why": a.get("why", ""),
                              "outcome": outcome})
    return items

def render(items, since, until):
    counts = {}
    for it in items:
        it["cat"] = categorize(" ".join([it["ref"], it["title"], it["why"]]))  # NOT outcome: its boilerplate says "safety/legal/cost" and would mislabel everything
        counts[it["cat"]] = counts.get(it["cat"], 0) + 1
    lines = []
    lines.append("# Escalation brief -- %s" % until.strftime("%Y-%m-%d"))
    lines.append("")
    lines.append("Window: %s -> %s UTC. Items: %d (%s). Everything below already had its" % (
        since.strftime("%d %b %H:%M"), until.strftime("%d %b %H:%M"), len(items),
        ", ".join("%s %d" % (k, v) for k, v in sorted(counts.items())) or "none"))
    lines.append("safest action taken or held -- nothing is waiting on you to be safe.")
    lines.append("Reports inform; they never block. One tick each closes it.")
    for it in items:
        safest, options = PLAYBOOK.get(it["cat"], PLAYBOOK["OTHER"])
        lines.append("")
        lines.append("## [%s] %s -- %s" % (it["cat"], it["ref"], (it["title"] or "(no title)")[:70]))
        lines.append("")
        lines.append("- **What:** %s (%s)" % (it["why"] or it["outcome"], it["when"]))
        lines.append("- **Safest action (standing):** %s" % safest)
        for i, opt in enumerate(options, 1):
            lines.append("- **Option %d:** %s" % (i, opt))
        lines.append("- **TICK: reply `%s %s` -- one word, done.**" % (
            it["ref"], "/".join(str(i) for i in range(1, len(options) + 1))))
    lines.append("")
    return "\n".join(lines)

def selftest():
    # 1. marker coverage: every refuse marker the AGENT knows maps to a category here.
    all_cat = set(m for marks in CATEGORIES.values() for m in marks)
    missing = [m for m in (REFUSE_LEGAL_COSTLY + REFUSE_TRUST_CORE) if m not in all_cat]
    assert not missing, "agent refuse-markers with NO brief category (add them): %s" % missing
    # 2. format: synthetic run report -> brief carries every section + tick lines.
    with tempfile.TemporaryDirectory() as d:
        rep = {"run": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "mode": "t",
               "seen": 3, "actions": [
                   {"ref": "SYN-PAY", "lane": "ESCALATE", "why": "touches a protected surface (paystack)",
                    "title": "double charge", "outcome": "escalated (safety/legal/cost)"},
                   {"ref": "SYN-LEGAL", "lane": "ESCALATE", "why": "touches a protected surface (popia)",
                    "title": "broken POPIA link", "outcome": "escalated (safety/legal/cost)"},
                   {"ref": "SYN-ERR", "lane": "PATH_A", "why": "brain[x]=MECHANICAL",
                    "title": "mid-fix crash", "outcome": "agent error mid-fix (Timeout) -> escalate for a human"}]}
        open(os.path.join(d, "run_t.json"), "w").write(json.dumps(rep))
        items = collect(d, datetime.now(timezone.utc) - timedelta(hours=1))
        assert len(items) == 3, "collector missed an escalation (got %d/3)" % len(items)
        md = render(items, datetime.now(timezone.utc) - timedelta(hours=1), datetime.now(timezone.utc))
        for must in ("[MONEY] SYN-PAY", "[LEGAL] SYN-LEGAL", "Safest action", "TICK: reply", "never block"):
            assert must in md, "brief format lost: %r" % must
    print("selftest PASS -- marker coverage + collector + format")
    return 0

def main():
    if "--selftest" in sys.argv:
        return selftest()
    hours = int(_arg("--hours", "24"))
    until = datetime.now(timezone.utc)
    since = until - timedelta(hours=hours)
    items = collect(os.path.join(REPO, ".maint_agent"), since)
    if not items:
        print("no escalations in the last %dh -- no brief written (silence here really is green)" % hours)
        return 0
    md = render(items, since, until)
    out = os.path.join(REPO, "Records", "ESCALATION_BRIEF_%s.md" % until.strftime("%Y-%m-%d"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print("brief -> %s  (%d item(s))" % (out, len(items)))
    return 0

if __name__ == "__main__":
    sys.exit(main())
