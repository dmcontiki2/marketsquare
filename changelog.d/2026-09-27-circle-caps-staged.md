## 2026-09-27 — CIRCLE-CAPS-1 built and STAGED (regulars limits 10 / 50 / 200 behind David's switch)

**What David asked (27 Sep, ~02:30 SAST):** "please build it now as a switch that works as you explained."

**Built:** one switch on the +1 page ("Regulars limits", `launch_switches.circle_caps`, default OFF).
OFF = no limit, the app shows "Your regulars: N". ON = Free 10 / Starter 50 / Pro 200 (Agency 50),
the Buzz screen shows "N of L regulars" with a bar, the plan cards and Quick list the limits, a new
connection into a full Circle is refused with the way out named, nobody already connected is cut off,
and after a downgrade the regulars beyond the new limit that were added under the limits are paused
for her buzzes only. Strangers unchanged. Behaviour proven on a temp database:
`scripts/test_circle_caps.py` -> ALL OK.

**Why it is STAGED, not live — a WORK-LOCK-1 breach by this lane, caught before any commit.**
The banking-terms lane took the lock on bea_main.py / ms.js / RULINGS.md at 00:23Z. This lane edited
bea_main.py and ms.js at 00:32Z without running `work_lock.py check` (RUL-140). Found at 00:37Z when
RUL-176 turned out to be taken. Undone: ms.js, dashboard.server.html, quick.html, genie/HARNESS.html
and roles/quick_i18n.json restored byte-for-byte to HEAD; bea_main.py — which the banking lane had
already edited on top — had only the 12 Circle hunks reversed, its BANKRESOLVE-1 work untouched and
compiling. The whole change now lives in `scripts/apply_circle_caps.py` (idempotent, exact anchors,
refuses while the lock is held; self-test reproduces the built files byte-for-byte).

**Tracked:** RG-0510 CIRCLE-CAPS-1 (OPEN until applied and live). The ruling is written to RULINGS.md
when the lock clears (RULINGS.md is inside the lock).

### Added the same night — KEEP-CHOICE-1, the downgrade standard (David 27 Sep: "Approved ... make this the standard for regulars, and also for listing slots on a downgrade")

**Ruling text for RULINGS.md (file it under the next free RUL number when the lock clears):**
THE DOWNGRADE STANDARD — SHE CHOOSES WHAT STAYS ACTIVE, FOR REGULARS AND FOR LISTING SLOTS.
(a) Before she confirms a downgrade she is told what the lower plan holds against what she has
("Free holds 2 listings and 10 regulars. You have 8 listings and 50 regulars.").
(b) A paid month runs to its end date — a move to Free with paid time left is SCHEDULED, not immediate
(it used to be immediate and forfeited the paid time) — and she ticks meanwhile what stays active.
(c) If she does not choose: the regulars she buzzed most recently, and the listings most recently
published, stay active — never random, never the oldest.
(d) The rest REST: resting regulars can still buzz her, she cannot buzz them; resting listings are
hidden from buyers. Nothing is deleted. She can swap any time. Moving up wakes everything at once.
(e) Customers are never told they were put on rest.
(f) The old "archive down to 2 before switching to Free" refusal is gone. Switching the regulars limits
ON still cuts nobody off (grandfathered at what she has; that allowance only shrinks, and ends when
her plan is lowered). Listing rest is NOT behind the regulars switch — it is the downgrade rule itself —
and applies only at a plan change or her own choice, so sellers already over their slots today are
untouched until they act.
**Also fixed on the way:** scheduled downgrades only ever took effect at a server RESTART
(`_apply_pending_downgrades()` ran once, at import). It now runs hourly.
**Built in the same staged script** (5 files now incl. route_policy.json: POST /buzz/keep,
GET/POST /users/{email}/listings/keep, all user-level and bound; a stranger gets 401).
Test: `scripts/test_circle_caps.py` → regulars OK, listings OK, ALL OK. RG-0510 re-scoped.

### APPLIED 27 Sep 2026 01:28Z (lock clear, repo silent since 01:15Z)
`apply_circle_caps.py` applied cleanly on top of the banking lane's RUL-176/178 commits (bea_main.py 24
hunks, ms.js 13, dashboard 4, quick 2, route_policy 2 + the Quick i18n block). Test ALL OK; the three new
routes answer a stranger 401; no undeclared routes. Rulings filed as **RUL-179** (the switch) and
**RUL-180** (the downgrade standard); PRICING_CANON §1 carries both; rulings_check 0 FAIL.
**Board before deploy: 0 REGRESSED.** On the way it read 4 red, none from a rotted fix:
RG-0504 was this lane's own word ('adverts' in the new messages -> 'listings'); RG-0503 still asserted
the banking form RUL-176 retired (the banking lane shipped at 01:05Z without re-aiming it) -- RE-AIMED to
the ruled state, not weakened, reasons in its ref; RG-0154 was deploy debt (session counter re-derived,
209); RG-0315 was a transient live read that passed on re-run.
