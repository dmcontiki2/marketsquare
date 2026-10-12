#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 8/8 -- the written record: OPEN_LOOPS.md (L42 updated with exactly what remains),
AUTO_RENEW_BRIEF.md (build record appended), WAYS_OF_WORKING.md (the scheduled-task rule appended).
Re-reads each file at the moment of writing; row replacement and appends only."""
import os, re
from patchlib import load, save, root

R = root()

# ── OPEN_LOOPS.md: L42 ──────────────────────────────────────────────────────────────────────────
P = os.path.join(R, "OPEN_LOOPS.md")
s, crlf, orig = load(P)
if "AUTO-RENEW-1 (RUL-224): BUILT 12 Oct 2026" in s:
    print("OPEN_LOOPS.md already updated -- skipped")
else:
    lines = s.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith("| L42 | **AUTO-RENEW-1 (RUL-224, David 11 Oct 2026 23:28)")]
    assert len(idx) == 1, "expected exactly one L42 row, found %d" % len(idx)
    lines[idx[0]] = (
        "| L42 | **AUTO-RENEW-1 (RUL-224): BUILT 12 Oct 2026, flag-dark -- the switch `launch_switches.auto_renew` is OFF.** "
        "Paid plans renew automatically as the standard; one tick box (ticked by default) makes it month-by-month; the "
        "subscriber's plan card shows 'Renews on <date>' + Cancel renewal. With the switch OFF the one-off 30-day payment of "
        "RUL-201 is byte-for-byte what it was (differential proof against the pre-build source: IDENTICAL). "
        "**What remains is exactly two things:** (1) David arms it; (2) Paystack itself has not been exercised -- no test "
        "key was in reach, so the rendered proof used a local stand-in -- so the first real checkout after arming is the "
        "one step still to be seen. The Agency Pro seat has no checkout of its own yet (RG-0167); its plan is prepared. "
        "| [D] arm | David switches on **Automatic plan renewal** on the +1 page. The session that sees the first real "
        "Paystack subscription records it here and closes this row. | 2026-10-11 | RULINGS.md RUL-224 - AUTO_RENEW_BRIEF.md "
        "s8 (build record) - changelog.d/2026-10-12-auto-renew-1.md - regression ledger RG-0964 / RG-0965 / RG-0966 - "
        "AUTO_RENEW_shots/ |")
    save(P, "\n".join(lines), crlf, orig)
    back = open(P, encoding="utf-8").read()
    assert back.count("| L42 |") == 1 and back.rstrip().endswith(s.rstrip()[-60:]), "OPEN_LOOPS.md tail changed"
    print("OPEN_LOOPS.md OK (L42 row updated; %d lines, tail intact)" % back.count("\n"))

# ── AUTO_RENEW_BRIEF.md: build record ───────────────────────────────────────────────────────────
P = os.path.join(R, "AUTO_RENEW_BRIEF.md")
s, crlf, orig = load(P)
if "## 8 · Build record" in s:
    print("AUTO_RENEW_BRIEF.md already carries the build record -- skipped")
else:
    s2 = s.rstrip("\n") + """

## 8 · Build record (12 Oct 2026)
**BUILT, flag-dark. The switch `launch_switches.auto_renew` ships OFF; arming is David's act, on the +1 page.**
Status as of 12 Oct 2026, verified by the three proofs below (not by this sentence -- run them).

| Section | Built | Where |
|---|---|---|
| s2 plans, once, by maintenance | yes | `bea_main.py _auto_renew_sync_plans` - `scripts/paystack_plans_sync.py` - `POST /admin/auto-renew/plans` - table `paystack_plans` |
| s2 checkout with the plan code only when the tick box is on | yes | `_auto_renew_checkout_plan` + `_auto_renew_initialize` |
| s2 webhook: subscription.create, renewal charge.success, invoice.payment_failed, subscription.disable / not_renew | yes | `_auto_renew_webhook` |
| s2 Cancel renewal, declared in route_policy.json | yes | `POST /payment/seller-subscription/cancel` (+ `/resume` for Renew again) |
| s2 non-card: tick box disabled, one-off flow | yes | ms.js `_arCheckout` |
| s2 replayed reference ignored; never charge from our side | yes | `_claim_payment_ref(..., "seller_subscription")`; no `charge_authorization` anywhere |
| s3 schema | yes | `run_migrations` (ALTER TABLE) |
| s4 app: tick box, 'Renews on <date>', Cancel renewal, DEMO_MODE guard | yes | ms.js block `AUTO-RENEW-1` |
| s4 Agency Pro seat: same tick box and button | **not applicable yet** | the seat has no checkout of its own (regression ledger RG-0167, open since 26 Sep); its Paystack plan is prepared, so it inherits the tick box when that checkout exists |
| s5 dashboard tiles, rulings_check RUL-224, ledger | yes | `/dashboard/launch-metrics` - `scripts/rulings_check.py` - RG-0964 / RG-0965 / RG-0966 |

**Definition of done (s6), item by item**
1. Switch OFF = today: **proven** -- `python3 scripts/prove_auto_renew_off_parity.py --base <pre-build source> --new .` -> IDENTICAL (37 answers, 10 Paystack requests, 4 tables).
2. Switch ON, QA account buys Starter with the tick box on, plan card shows 'Renews on <date>' and Cancel renewal, cancel disables the subscription: **proven in the rendered app against a Paystack STAND-IN** (`AUTO_RENEW_shots/`, `scripts/smoke_harness/rig_autorenew/`). **Not proven against Paystack itself** -- no Paystack test key was in reach (the server holds the live key only).
3. Webhook replay: **proven** -- `python3 scripts/prove_auto_renew.py` (signed POSTs, throwaway database).
4. Tick box off -> one-off purchase, no subscription: **proven** (both proofs + rendered).
5. Ledger, stranger test, pricing canon: see the changelog fragment `changelog.d/2026-10-12-auto-renew-1.md` for the run of the day.
6. Report to David: sent 12 Oct 2026.

**Three things the brief did not know, decided in the build (David may veto):** Paystack bills on the same day each
month, not every 30 days, so a renewal runs from the later of the previous end and the payment (+30 days) and a plan
whose renewal is due waits up to 72 hours; Paystack does not retry a failed charge before the next payment date, so
after a failure the plan ends on its date and the subscription is switched off (one Buzz + one email in total); and a
seller who already renews is still served if the switch is turned off again.
"""
    save(P, s2, crlf, orig)
    print("AUTO_RENEW_BRIEF.md OK (build record appended)")

# ── WAYS_OF_WORKING.md: the scheduled-task rule ─────────────────────────────────────────────────
P = os.path.join(R, "WAYS_OF_WORKING.md")
s, crlf, orig = load(P)
if "SCHEDULED-TASK-ACCESS-1" in s:
    print("WAYS_OF_WORKING.md already carries the scheduled-task rule -- skipped")
else:
    s2 = s.rstrip("\n") + """

## Scheduled tasks -- access is settled when the task is CREATED, not when it runs (SCHEDULED-TASK-ACCESS-1, 12 Oct 2026)

What happened: the AUTO-RENEW-1 build was scheduled for Mon 12 Oct 01:30 SAST, unattended. It could not start. A
scheduled task opens a FRESH session with no folder attached, the approval prompt for `Projects` sat on the PC for two
hours with nobody there, and the run ended having read nothing. David, 05:01 SAST: *"why did you not tell me the promp
cant run before the time when we set it up?"* He was right: nobody had checked.

The rule, for whoever creates a scheduled task that needs this project:
- **Before saying a task is scheduled, name what it needs and confirm it is already granted to THAT task:** the
  `Projects` folder (approved for the task, not just for the chat that created it), and anything else the run will touch
  -- the GitHub repo if it is to read code from there, a browser, a key.
- **If the folder is not yet approved for the task, say so in the same message, plainly:** "this will not be able to
  read your files at 01:30 unless you approve the folder for it now." Do not leave it to the run to discover.
- **Prove it once:** fire the task (or a one-line probe task with the same settings) while David is still there, and
  see it list the project folder. A task that has never started is not set up.
- **An unattended run that finds itself without access notifies David at once** (it did) and says exactly which
  approval is missing -- and the approval, once given, covers that task's later runs.
- Use the `/access` skill before any unattended or overnight run: it exists for exactly this.
"""
    save(P, s2, crlf, orig)
    print("WAYS_OF_WORKING.md OK (scheduled-task rule appended)")
