#!/usr/bin/env python3
"""rulings_check.py -- a ruling is not made until the canon reflects it.

Born 15 Aug 2026, the day the launch date -- expressly reviewed and fixed across several
sessions -- turned out never to have reached the canonical files. The regression ledger
answers "is a fix still fixed". This answers the sibling question the project never asked:
"is a RULING still reflected where the next session will read?"

The failure mode is specific to how sessions work: David rules in conversation; the session
ends; the next session reads the FILES as truth. If the ruling never landed, the machinery is
not merely ignorant of it -- it will actively report its absence as fact ("launch date STILL
NEEDED"), and David becomes the only integration layer. That is the blind spot, and no human
should have to be the patch for it.

Exit 0 = every ruling reflected.  1 = drift.  2 = register unreadable.

    python3 scripts/rulings_check.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PROJECTS = os.path.dirname(REPO)
REGISTER = os.path.join(REPO, "RULINGS.md")

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"


def _read(path):
    p = path if os.path.isabs(path) else os.path.join(REPO, path)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


# Each ruling: list of (file, [must_contain...], [must_NOT_contain...])
# Keep assertions grep-simple AND WRAP-SAFE: needles must not span a line wrap. Four of the
# first run's seven FAILs were this checker's own needles breaking on 80-col wraps -- a
# checker wrong on day one teaches the right lesson: verify the checker before the canon.
REFLECTIONS = {
 "RUL-027": [
   ("bea_main.py", ["GATE-NOLOCK-1", "def _grant_review_cookie", "/review/claim-code",
                    "admin-master/", "admin-team/"], []),
   ("migrations/025_gate_nolock.py", ["GATE-NOLOCK-1", "/admin/login"], []),
   ("marketsquare.html", ["gate-otp-block", "gateClaimCode"],
                         ["Incorrect reviewer code. Please check it and try again."]),
   ("dashboard.server.html", ["GATE-NOLOCK-1"], ["Locked by the pre-launch gate"]),
   ("scripts/regression_ledger.py", ["RG-0107", "RG-0108",
                                     "rg_gate_admin_never_locked"], []),
   ("RULINGS.md", ["NOBODY ENTITLED TO ENTER MAY BE LOCKED OUT BY THEIR DEVICE"], []),
 ],
 "RUL-026": [
   ("bea_main.py", ["RUL-026: showcase supers never fade", "Showcase adverts are admin-managed."], []),
   ("migrations/024_showcase_immortal.py", ["RUL-026"], []),
   ("scripts/regression_ledger.py", ["RG-0106", "rg_showcase_immortal"], []),
 ],
 "RUL-022": [
   ("bea_main.py", ["def usd_to_zar_amount", "FX-LIVE-1"], ["tuppence * 36"]),
   ("ms.js", ["function loadFX", "fxTopupLine"], []),
   ("scripts/regression_ledger.py", ["RG-0098", "rg_fx_live"], []),
   ("RULINGS.md", ["FOREX IS LIVE, FREE, KEYLESS"], []),
 ],
 "RUL-021": [
   ("ms.js", ["adventures_za_map.html", "adventures_gb_map.html"], []),
   ("adventures_za_map.html", [], []),
   ("adventures_gb_map.html", [], []),
 ],
 "RUL-020": [
   ("migrations/021_open_legal_docs.py", ["RUL-020", "location = /terms"], []),
   ("scripts/regression_ledger.py", ["RG-0092", "rg_legal_docs_public"], []),
   ("RULINGS.md", ["EULA FINAL & BINDING"], []),
 ],
 "RUL-019": [
   ("BACKLOG.md", ["CLEARED 15 Aug 2026", "international payments enabled"], []),
   ("FINANCE_CANON.md", ["Re-verification log", "GLOBAL_PAYMENT_RAILS_2026-08-15.docx"], []),
   ("GLOBAL_LAUNCH_PLAN_2026-08-15.docx", [], []),
 ],
 "RUL-018": [
   ("STANDING_ORDERS.md", ["SO-2", "Representation parity"], []),
   ("HIGGSFIELD_REGEN_QUEUE.md", ["PARITY RULE"], []),
 ],
 "RUL-017": [
   ("scripts/ops_sweep.py", ["OPS-SWEEP-1", "FIX", "REVIEW"], []),
   ("migrations/020_ops_sweep_cron.py", ["ops_sweep"], []),
   ("orchestration_v2/cockpit.html", ["Report &amp; Fix"], []),
   ("ops/autodeploy/deploy_manifest.txt", ["ops_sweep.py", "cockpit.html"], []),
 ],
 "RUL-016": [
   ("BACKLOG.md", ["DECIDED 15 Aug (David): (a)"], []),
   ("FAULT_REGISTER.md", ["CLOSED 15 Aug (letter sent)"], []),
 ],
 "RUL-015": [
   ("ACCESS_CHEATSHEET.md", ["never grant admin"], []),
   ("dashboard.server.html", ["admin-gate-input"], []),
   ("marketsquare_admin.html", ["admin-gate-input"], []),
 ],
 "RUL-014": [
   ("bea_main.py", ["GATE-EMAIL-1", "/review/request-link"], []),
   ("marketsquare.html", ["gate-email-input", "GATE-COOKIE-2"], []),
   ("migrations/019_gate_email_link.py", ["review_emails.txt"], []),
   ("scripts/regression_ledger.py", ["RG-0081"], []),
   ("ACCESS_CHEATSHEET.md", ["access link"], []),
 ],
 "RUL-001": [
   ("LAUNCH_BAR_2026-08-15.md", ["1 September 2026", "29 August 2026", "gate comes down"], []),
   ("BACKLOG.md", [], ["provisionally 2026-08-01"]),   # LAUNCH-DEADLINE-1 must be re-set
 ],
 "RUL-002": [
   ("AI_BASELINE.json", ['"baseline_lane": "openai"'], []),
   ("AI_LANE_GUIDANCE.md", ["AUTO-FAILOVER", "SAFETY NET"], []),
 ],
 "RUL-003": [
   # The doc-error purge (CC-003). Expected to FAIL until BACKLOG stops carrying the
   # repudiated launch-threshold wording -- two months old and counting.
   ("BACKLOG.md", [], ["need 37 more before public launch", "23/60"]),
 ],
 "RUL-004": [
   ("AI_VENDOR_STRATEGY_DECISION_2026-07-11.md", ["No pure Chinese endpoints"], []),
   ("EU_HARNESS_REDUNDANCY_2026-08-15.md", ["EU"], []),
 ],
 "RUL-005": [
   ("MAINTENANCE_AGENT.md", ["AUTONOMY, NO VETO"], []),
   ("scripts/maintenance_agent.py", ["REFUSE_LEGAL_COSTLY", "REFUSE_TRUST_CORE"], []),
 ],
 "RUL-006": [
   ("ONE_DEPLOY.md", ["deploy"], []),
   ("scripts/regression_ledger.py", ["RG-0023"], []),
 ],
 "RUL-007": [
   ("PRICING_CANON.md", [], []),
   (os.path.join(PROJECTS, "CLAUDE.md"), ["FIXED Tuppence"], []),
 ],
 "RUL-008": [
   (os.path.join(PROJECTS, "CLAUDE.md"), ["INTRODUCTORY", "NEVER merchant"], []),
 ],
 "RUL-009": [
   ("AI_BASELINE.json", ["COST ENVELOPE"], []),
   ("scripts/ai_baseline_check.py", ["def main"], []),
   ("scripts/ai_challenger_board.py", ["never switches" ], []),
 ],
 "RUL-010": [
   ("EU_HARNESS_REDUNDANCY_2026-08-15.md", ["HARNESS-PILOT-1", "OUT"], []),
 ],
 "RUL-011": [
   (os.path.join(PROJECTS, "CLAUDE.md"), ["LOCKED in the ledger"], []),
   ("scripts/regression_ledger.py", ["LOCKED"], []),
 ],
 "RUL-012": [
   (os.path.join(PROJECTS, "CLAUDE.md"), ["TRUNCATE"], []),
 ],
 "RUL-013": [
   ("MAINTENANCE_AGENT.md", ["RUL-013", "PRE-LAUNCH", "POST-LAUNCH", "98%", "STANDBY"], []),
   # The honest half: the Fable hand-off is intent, not mechanism. If this gap note ever
   # disappears without the lane actually existing, a session will assume a hand-off that
   # cannot happen -- so the note itself is asserted.
   ("MAINTENANCE_AGENT.md", ["KNOWN GAP"], []),
   # The arrangement is TIME-BOXED. If the expiry wording ever vanishes, a session in October
   # would read RUL-013 as standing policy and keep routing design work at Fable.
   ("RULINGS.md", ["ENDS 1 Sep 2026", "SPEND-GUARD-1"], []),
 ],
}


def main():
    reg = _read(REGISTER)
    if reg is None:
        print("RULINGS CHECK: RULINGS.md missing -- the register itself is gone")
        return 2

    listed = set(re.findall(r"\| (RUL-\d{3}) \|", reg))
    fails = warns = 0
    print("RULINGS CHECK -- is every ruling reflected where the next session will read?")
    print("=" * 78)

    for rid in sorted(REFLECTIONS):
        if rid not in listed:
            print("  FAIL  %s has reflection assertions but is missing from RULINGS.md" % rid)
            fails += 1
            continue
        problems = []
        for path, must, must_not in REFLECTIONS[rid]:
            c = _read(path)
            name = os.path.basename(path)
            if c is None:
                problems.append((FAIL, "%s: file missing (%s)" % (rid, name)))
                continue
            for needle in must:
                if needle not in c:
                    problems.append((FAIL, "%s: %s does not carry %r -- the ruling is not "
                                          "reflected there" % (rid, name, needle)))
            for needle in must_not:
                if needle in c:
                    problems.append((FAIL, "%s: %s STILL carries %r -- superseded wording the "
                                          "ruling was meant to purge" % (rid, name, needle)))
        if problems:
            for lvl, msg in problems:
                print("  %-5s %s" % (lvl, msg))
                fails += 1 if lvl == FAIL else 0
                warns += 1 if lvl == WARN else 0
        else:
            print("  INFO  %s reflected" % rid)

    unasserted = listed - set(REFLECTIONS)
    for rid in sorted(unasserted):
        print("  WARN  %s is in RULINGS.md but has no reflection assertions here -- add them, "
              "or the entry is a note, not a guarantee" % rid)
        warns += 1

    print("=" * 78)
    print("%d rulings checked, %d FAIL, %d WARN" % (len(REFLECTIONS), fails, warns))
    if fails:
        print("RESULT: at least one ruling exists only in memory or in one file -- the blind "
              "spot is live.")
        return 1
    print("RESULT: every ruling is reflected in canon. No session should rediscover one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
