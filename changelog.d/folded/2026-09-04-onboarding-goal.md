## 2026-09-04 — The onboarding goal becomes one goal, handed to an agent (RUL-096)

David, after a review of Fable 5.1 on giving a model the whole task as a single Goal
rather than steering it: *"set this up to start on schedule, Saturday 01:00... Give Fable
all the accesses required and the permissions set to auto. No restrictions other than what
has been defined in the onboarding goal."*

- **THE GOAL** — `ONBOARDING_GOAL.md`: 20 people we contacted cold publish a live listing
  **by their own hand** by Fri 31 Oct 2026. Baseline PROBED 4 Sep = **0**. Method is the
  agent's and is never put to David.
- **SCORED BY TWO PROBES** that must agree, never by self-report: `prospects.published_at IS
  NOT NULL` (read-only) AND the listing visible to a logged-out member of the public.
  PROBED 4 Sep: the launch gate is DOWN (`/`, `/listings`, `/flags` all 200 anonymously), so
  both probes run from any sandbox — no SSH, no browser, no David screenshot.
- **ANTI-GAMING IS PART OF THE GOAL**: real humans from our outreach only; neither Claude nor
  David may create the listing; no paid ads, incentives or bought traffic; no relabelling of
  seeded rows. A truthful 4 beats a manufactured 20.
- **GOAL_STATE.md** — new: the agent's memory between runs, capped at 60 lines, so a fresh
  session orients for a few hundred tokens instead of thousands. Carries the number, the
  leaks, what the last run did, and a "things already tried that did not work" list so no
  future run repeats a dead end.
- **COST FENCE** (the one hard limit): subscription only; never enable, request or consume
  Usage Credits; never ask David to buy capacity; on hitting the limit stop cleanly, save
  state, resume next window. Anything that repeats belongs on the host scheduler or the
  server, never in a paid session.
- **ALLOWLIST WIDENED by 5 SUPPLY/HYGIENE entries only** (run_wave2_unattended,
  run_local_scraper, deploy_citylauncher, fill_wave_gaps, clean_junk_emails). **NO new
  sending authority** — outreach still goes only through the already-permitted, fully gated
  `launch_day_wave.bat`, which already covers all 14 live cities, so RUL-095(e) stands intact.
  `rulings_check.py` RUL-096 now asserts the *absence* of the four unlisted send bats, so a
  later session cannot quietly widen send power.
- **SCHEDULE**: `trustsquare-onboarding-goal`, daily 01:00 SAST, first fire Sat 5 Sep 01:08.
- **The floor is broken and the goal says so**: 546 emailed, 61 clicked, 0 published, because
  self-serve listing has been impossible since 22 Jul (422 price-basis, RG-0249) and invitees
  never received the AI draft (401 gate, RG-0250). First act is to ship those and prove one
  end-to-end pass — not more outreach.

Verified: `rulings_check.py` 93 rulings, 0 FAIL, RUL-096 reflected. `regression_ledger.py`
no regressions (RG-0181/0182 not evaluated — this sandbox lacks `fastapi`, an environment gap,
unrelated to this change).
