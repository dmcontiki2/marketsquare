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
 "RUL-030": [
   ("ONETAP_SETUP.md", ["Apple \u2014 NOT DOING IT"], []),
   ("bea_main.py", ["_apple_client_secret"], []),
   ("RULINGS.md", ["APPLE SIGN-IN IS OUT"], []),
 ],
 "RUL-029": [
   ("migrations/026_gate_down.py", ["GATE-DOWN-1", "/review/verify"], []),
   ("scripts/regression_ledger.py", ["RG-0115", "rg_gate_actually_down"], []),
   ("RULINGS.md", ["PRE-LAUNCH GATE COMES DOWN TODAY"], []),
 ],
 "RUL-028": [
   ("bea_main.py", ["ONETAP-1", "def _oauth_verify_id_token", "def _apple_client_secret",
                    "auth_sub"], []),
   ("ms.js", ["mountOneTap"], ["accounts.google.com/gsi"]),
   ("marketsquare.html", ["onetap-buttons"], ["accounts.google.com/gsi"]),
   ("migrations/025_gate_nolock.py", ["/auth/oauth/"], []),
   ("scripts/regression_ledger.py", ["RG-0111", "rg_onetap_no_third_party"], []),
   ("RULINGS.md", ["FEDERATED ONE-TAP SIGN-IN"], []),
 ],
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
 "RUL-034": [
   # WAF-OPEN-1: the CF edge rule is DISABLED; the ORIGIN gate is the pre-launch guard.
   # Superseded wording must be GONE, or a next session re-learns "testers not yet let in".
   ("ACCESS_CHEATSHEET.md", ["WAF-OPEN-1", "Cloudflare edge OPEN"],
    ["Testers NOT yet let in"]),
   ("RULINGS.md", ["Edge gate DOWN for all visitors"], []),
   ("CHANGELOG.md", ["WAF-OPEN-1"], []),
   ("STATUS.md", ["Edge OPEN for testers"], []),
 ],
 "RUL-033": [
   ("bea_main.py", ["def _anon_reject_only", "PHOTO-REJECT-1"], []),
   ("scripts/regression_ledger.py", ["RG-0122", "rg_photo_reject_only"], []),
   ("RULINGS.md", ["REJECT-ONLY BRIDGE"], []),
 ],
 "RUL-031": [
   ("RULINGS.md", ["NO MORE MICRO-FIXES TO THE ANON-BLUR MACHINERY"], []),
   ("CHANGELOG.md", ["deliberately NOT re-patched"], []),
 ],
 "RUL-032": [
   ("ai_provider.py", ["def _gemini", "GEMINI CANARY (RUL-032"], []),
   ("bea_main.py", ["def _anon_scan_provider", "GEMINI-CANARY-1"], []),
   ("scripts/eval_photo_anon.py", ["100% plate recall"], []),
   ("scripts/regression_ledger.py", ["RG-0121", "rg_gemini_canary"], []),
   ("AI_BASELINE.json", ["CANARY (photo scan/refine only)"], []),
 ],
 "RUL-023": [
   # (a) accountant from MONTH 1, not Year 2 -- the canon file itself carried the overturned
   # wording until 21 Aug, which is exactly what a reflection assertion is for.
   ("FINANCE_CANON.md", ["engaged from MONTH 1", "RUL-023(a)"], ["budgets R2,000/mo from Year 2"]),
   ("RULINGS.md", ["COST BASE, PRE-LAUNCH"], []),
 ],
 "RUL-024": [
   ("Records/DB_DECISION_2026-07-29.md", ["Launch runs on SQLite"], []),
   ("RULINGS.md", ["POSTGRES STAYS POST-LAUNCH"], []),
 ],
 "RUL-025": [
   ("canon.yml", ["RUL-025", "server_eur_month_new_order", "35.49"], []),
   ("RULINGS.md", ["DO NOT RESCALE THE PRODUCTION BOX"], []),
 ],
 "RUL-053": [
   # The launch wave plan (David, 24 Aug): Pretoria ladder from Fri 28 Aug, global
   # launch day Tue 1 Sep (all cities send Stays), SA rolls daily, global three hold
   # to 4 Sep, agencies selective on traction, cap 30/cat/city/day. The board ships
   # at /static/wave_plan.html and the +1 page links it (WAVE-PLAN-1).
   ("RULINGS.md", ["THE LAUNCH WAVE PLAN"], []),
   ("WAVE_PLAN_LAUNCH_2026.html", ["GLOBAL", "HOLD", "1 SEP"], []),
   ("ops/autodeploy/deploy_manifest.txt", ["wave_plan.html"], []),
   ("dashboard.server.html", ["WAVE-PLAN-1"], []),
 ],
 "RUL-052": [
   # International scraped-address outreach RELEASED (David, 24 Aug): US/UK/AU waves
   # proceed on the wave-plan schedule with no counsel pre-gate; counsel review is an
   # ordinary follow-up (SS6.1A class). A "before 4 Sep" gate reappearing on the wave
   # board, or the ruling row vanishing, trips here.
   ("RULINGS.md", ["INTERNATIONAL SCRAPED-ADDRESS OUTREACH IS RELEASED"], []),
   ("WAVE_PLAN_LAUNCH_2026.html", ["RELEASED (RUL-052"], ["Counsel item before 4 Sep"]),
 ],
 "RUL-051": [
   # Features relist waits for the VIDEOS (David, 24 Aug): the Browse card returns only
   # once the full-length feature videos (RUL-043, shelved) are done, on David's word.
   # Until then the feature lives in the agency surfaces, marked launching soon (no
   # public date, RUL-046). Dropping a marker, or relisting early, trips here.
   ("RULINGS.md", ["FEATURES RELIST WAITS FOR THE VIDEOS"], []),
   ("ms.js", ["Programmes (pooled) \u2014 launching soon"], []),
   ("orchestration_v2/templates/placement_onboarding/onboard_5.html", ["Launching soon"], []),
   ("orchestration_v2/templates/placement_agency_outreach.html", ["launching soon"], []),
 ],
 "RUL-050": [
   # The Study & Work Abroad entry is OFF Browse for launch (David, 24 Aug): the teaser
   # videos are shelved placeholders (RUL-043), so the front-door card goes. The page
   # itself stays live UNLISTED (onboard_5 links it; RUL-044/045 artefacts). must_NOT
   # polices any teaser banner/link returning to Browse before David relists it.
   ("RULINGS.md", ["ENTRY COMES OFF BROWSE FOR LAUNCH"], []),
   ("marketsquare.html", [], ["studyabroad_teaser"]),
   ("studyabroad_teaser.html", ["COMING SHORTLY"], []),
   ("ops/autodeploy/deploy_manifest.txt", ["studyabroad_teaser.html"], []),
 ],
 "RUL-049": [
   # Four recruited verticals built: backend verticals exist and the skins are real.
   ("RULINGS.md", ["THE FOUR RECRUITED VERTICALS ARE BUILT"], []),
   ("estate_agents.py", ["CREDENTIAL_SLOTS_COLLECTOR", "CREDENTIAL_SLOTS_INSTITUTION",
                          "CREDENTIAL_SLOTS_SERVICE", "CREDENTIAL_SLOTS_PLACEMENT",
                          "category.institution.clearances"], []),
   ("ms.js", ["collector:C, institution:I, service_company:S, placement:P"], []),
 ],
 "RUL-048": [
   # A Pro seat is EARNED (agent's $5 subscription + EULA), never granted by a console
   # flip. must_NOT polices the old silent-toggle wiring coming back to the UI.
   ("RULINGS.md", ["A PRO SEAT IS EARNED THROUGH THE SUBSCRIPTION FLOW"], []),
   ("PRICING_CANON.md", ["Agency Pro seat (RUL-048"], []),
   ("ms.js", ["agencyProInvite"], ['onclick="agencySeat(']),
 ],
 "RUL-047": [
   # The badge is PARKED: canon says so, and the customer-facing surfaces must stay
   # CLEAN of it until David names the occasion. must_NOT needles police re-surfacing
   # on the highest-traffic templates + both builders; the placement lane doubles as
   # the travel-remnant guard (no ASATA/journey copy in a placement invite).
   ("PRICING_CANON.md", ["PARKED (RUL-047"], []),
   ("RULINGS.md", ["THE FOUNDERS BADGE IS PARKED"], []),
   ("orchestration_v2/templates/travel_agency_outreach.html", [], ["launch_code", "Founders Badge"]),
   ("orchestration_v2/templates/agency_outreach.html", [], ["launch_code", "Founders Badge"]),
   ("orchestration_v2/templates/placement_agency_outreach.html", ["Placement Agency"], ["launch_code", "Founders Badge", "ASATA", "journey map"]),
   ("orchestration_v2/templates/placement_onboarding/onboard_7.html", ["Founding status"], ["20%", "for-life", "Founders Badge"]),
   ("marketing/src/build_deck.js", [], ["Ruby Spark"]),
   ("marketing/src/build_posters.py", [], ["founding badge"]),
 ],
 "RUL-046": [
   # The placement vertical exists as artefacts: cold invite + all 8 onboarding
   # emails + the cadence doc + manifest rows; and the launch posture (engine dark,
   # teaser only) is written in the register. Deleting an email from the sequence
   # or un-manifesting the lane trips here.
   ("RULINGS.md", ["EIGHT-EMAIL ONBOARDING STANDARD", "ENGINE STAYS DARK FOR LAUNCH"], []),
   ("orchestration_v2/templates/placement_agency_outreach.html", ["Placement Agency"], []),
   ("orchestration_v2/templates/placement_onboarding/SEQUENCE.md", ["onboard_1..8", "Day 18"], []),
   ("orchestration_v2/templates/placement_onboarding/onboard_8.html", ["Go-live checklist", "EMAIL 8 OF 8"], []),
   ("ops/autodeploy/deploy_manifest.txt", ["placement_onboarding/onboard_8.html"], []),
 ],
 "RUL-045": [
   # The visual language is template law: photo arc + surroundings + layered map.
   # Both map pages exist with the demo banner include (RUL-040 scope rule for new
   # demo pages); the teaser links them; the queue carries the 12 persona prompts.
   ("studywork_hu_map.html", ["ts_demo_banner.js", "The smart alternatives"], []),
   ("studywork_us_map.html", ["ts_demo_banner.js", "The seasons"], []),
   ("studyabroad_teaser.html", ["studywork_hu_map.html", "studywork_us_map.html"], []),
   ("HIGGSFIELD_REGEN_QUEUE.md", ["sw_hu_1_airport.jpg", "sw_us_6_life.jpg"], []),
   ("scripts/build_dossier_pdf.py", ["mapshot"], []),
 ],
 "RUL-044": [
   # The examples are full PDFs from the template generator; the teaser links them;
   # the refugee pathway stays factual and un-graded ("NOT A WORK ROUTE"). A session
   # that deletes the generator, unlinks the PDFs, or turns the adjacent-pathway
   # panel into a recommendation trips here.
   ("RULINGS.md", ["FULL HOUSE-FORMAT PDFs", "NOT A WORK ROUTE"], []),
   ("scripts/build_dossier_pdf.py", ["P4", "AI-GENERATED EXAMPLE"], []),
   ("scripts/dossier_examples.py", ["ADJACENT PATHWAY - NOT A WORK ROUTE", "Scam Wall"], []),
   ("studyabroad_teaser.html", ["Dossier_EXAMPLE_Study_Hungary.pdf", "Dossier_EXAMPLE_Work_USA_Farm.pdf"], []),
 ],
 "RUL-043": [
   # 5T is canon; both benchmark examples exist on the teaser; the work example is
   # honest about Canada being closed; videos are shelved full-length items, not
   # rendered shorts. A session that ships a 10s short, silently unshleves, or
   # softens the Canada verdict to sell the dream trips these needles.
   ("RULINGS.md", ["5T CONFIRMED", "FULL-LENGTH AND SHELVED"], []),
   ("studyabroad_teaser.html", ["just out of matric", "no working-holiday agreement"], []),
   ("LAUNCH_SERIES.md", ["SHELVED (RUL-043)"], []),
   ("STUDYWORK_DOSSIER_SPEC.md", ["5 Tuppence", "full-length"], []),
 ],
 "RUL-042": [
   # Positioning IS the ruling: preparation is ours (actuals-based), the PLAN is the
   # agency's, and partner agencies are first-class in the design. If a future spec
   # drifts into "we plan it for you" or drops the agency handoff, the register row
   # is the anchor the next session must hit; D15 keeps the three reserved business
   # calls visible until David takes them; the assessment docx must keep existing.
   ("RULINGS.md", ["PREPARATION IS OURS, THE PLAN IS THE AGENCY"], []),
   ("OPEN_LOOPS.md", ["Study & Work-Abroad Advisor"], []),
   ("STUDY_WORK_ABROAD_ADVISOR_ASSESSMENT — nice.docx", [], []),
 ],
 "RUL-041": [
   # The tours resubmit is a one-off act, so the DURABLE half is what must stay true:
   # the token is recorded unrotatable-with-reasons, the loop says AWAIT rather than
   # re-submit, and the no-third-party-script rule that shapes any future partner
   # imagery is still asserted. If a later session "fixes" the loop by resubmitting
   # unchanged, or quietly re-adds a TP script for photos, these trip.
   ("RULINGS.md", ["THE TRAVELPAYOUTS TOURS REVIEW WAS RESUBMITTED EARLY"], []),
   ("SECRETS_REGISTER.md", ["UNROTATABLE-ACCEPTED", "TRAVELPAYOUTS_TOKEN"], []),
   ("OPEN_LOOPS.md", ["RESUBMITTED 22 Aug 2026", "AWAIT OUTCOME"], []),
   ("scripts/regression_ledger.py", ["RG-0025", "RG-0146"], []),
 ],
 "RUL-040": [
   # (a) the label states what the thing IS, at every renderer, and the old accolade
   # wording is GONE -- a fifth renderer copy-pasted from an old one would trip the
   # forbidden clause. (b) the DEMO tab exists, ships, and is NOT on the tester lane:
   # ts_report.js is removed at Soft Launch and DEMO must survive that day.
   ("RULINGS.md", ["AI EXAMPLE GENERATED ADVERTS, AND A DEMO BANNER"], []),
   ("ms.js", ["AI EXAMPLE GENERATED ADVERT", "not a real listing"],
                ["SUPER ADVERT", "free for a real seller to claim"]),
   ("ts_demo_banner.js", ["ts-demo-tab"], ["fault_report"]),
   ("adventures_za_map.html", ["ts_demo_banner.js"], []),
   ("ops/autodeploy/deploy_manifest.txt", ["ts_demo_banner.js"], []),
   ("scripts/regression_ledger.py", ["RG-0140", "RG-0141"], []),
 ],
 "RUL-039": [
   # Paid NPR verification: offered, visible, never a blocker.
   # Assert the PROPERTIES that must not rot, not the wording:
   #   1. the ruling is on record
   #   2. the paid tier is a SEPARATE column from the intro gate (id_verified_at
   #      keeps its job — a session must never "simplify" these into one)
   #   3. the ledger exists (one check ever) AND the duplicate-hash trap is coded
   #   4. the provider is a swappable adapter that fails closed
   #   5. the guards exist
   ("RULINGS.md", ["PAID HOME AFFAIRS ID VERIFICATION AT 1 TUPPENCE"], []),
   ("bea_main.py", ["id_npr_verified_at", "id_verification_ledger",
                    "duplicate_hash", "ID_NPR_PRICE_T"], []),
   ("id_verify_provider.py", ["billable", "is_available", "fail"], []),
   ("test_id_npr.py", ["test_duplicate_hash_on_second_account_is_flagged_not_granted",
                       "test_npr_column_is_separate_from_intro_gate"], []),
 ],
 "RUL-038": [
   # The advert must carry the pre-information, and it must sit BELOW the map.
   # Assert the PROPERTY, not a spelling: the data exists, the renderer exists, the
   # page loads it, and the manifest ships it. Placement itself is asserted by
   # RG-0135 (which compares the call site against the map block in ms.js).
   ("RULINGS.md", ["AN ADVERT FOR A TRIP MUST CARRY THE PRE-INFORMATION"], []),
   ("ms.js", ["tripEssentialsPanel", "does not sell or book"], []),
   ("trip_essentials.js", ["window.TRIP_ESSENTIALS"], []),
   ("marketsquare.html", ["/static/trip_essentials.js"], []),
   ("ops/autodeploy/deploy_manifest.txt", ["trip_essentials.js"], []),
   ("scripts/regression_ledger.py", ["RG-0135", "rg_trip_essentials"], []),
 ],
 "RUL-037": [
   ("RULINGS.md", ["CLAUDE IS THE CTO"], []),
   ("STANDING_ORDERS.md", ["SO-4"], []),
   ("../CLAUDE.md", ["Claude is the CTO"], []),
 ],
 "RUL-036": [
   ("RULINGS.md", ["STANDING FIX-AND-REPORT MANDATE"], []),
   ("STANDING_ORDERS.md", ["SO-3", "report solutions, not problems"], []),
 ],
 "RUL-035": [
   # The supers stay through launch; retirement is a deliberate admin act, one shelf at a
   # time, never a side effect of machinery. Assert the PROPERTY (super_example is in the
   # protected set), not any one spelling of the SQL -- RG-0106 was green for a week
   # because it pinned a literal string. See SUPER-IMMORTAL-2.
   ("bea_main.py", ["SUPER-IMMORTAL-2", "super_example"], []),
   ("migrations/027_super_immortal.py", ["super_example", "showcase"], []),
   ("scripts/regression_ledger.py", ["RG-0123", "rg_supers_immortal"], []),
   ("RULINGS.md", ["THE SUPERS STAY THROUGH LAUNCH"], []),
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
