# LAUNCH BAR & DATES — 15 Aug 2026 (v2, dates ruled)

**David's ruling, 15 Aug 2026: FULL LAUNCH Monday 1 September 2026. SOFT LAUNCH TO PUBLIC
Friday 29 August 2026 — the gate comes down three days early.** This closes the open item in
SUPER_LADDER_SIGNOFF_2026-07-27 ("launch date STILL NEEDED from David") and supersedes the
provisional LAUNCH_SPECIAL_DEADLINE of 2026-08-01 (LAUNCH-DEADLINE-1 — re-set it to 2026-09-01).

Drafts LAUNCH-GATES-1 (BACKLOG.md:369). Needs David's ratification of the GATES; the DATES are
his ruling and stand.

---

## The calendar (today = Sat 15 Aug — 14 days to public)

| Date | What |
|---|---|
| **Now → Thu 21 Aug** | Floor work sprint (see below). Flip session runs Sat 16 Aug 09:00 |
| **Fri 22 Aug** | **D-7 GATE REVIEW** — the board is read; any RED gate = hold declared THAT DAY |
| Wed 27 Aug | Last ship day (T-2). Nothing deploys on launch eve |
| **Fri 29 Aug** | **SOFT LAUNCH — the gate comes DOWN. Public access. No wave emails** |
| **Mon 1 Sep** | **FULL LAUNCH** — wave machinery starts (first wave still HALTS at AWAITING_APPROVAL, David approves manually). Travelpayouts resubmission same day — it needs a working public site, which it now has |
| If 22 Aug is RED | Hold posture: gate stays up, testers continue, 1:1 onboarding continues. Slip is ONE month: soft Mon 28 Sep, full Thu 1 Oct. A second miss forces a scope-cut ruling, not a second extension |

## THE 29 AUG EXPOSURE EVENT — the fact the date makes urgent

**When the gate comes down, everything it was masking goes public at once.** The gate is
currently doing security work it was never designed to do:

- **IL-01: `GET /tuppence/balance?email=` is a public read** masked ONLY by the gate.
  On 29 Aug it becomes anonymous-readable. Was already flagged launch blocker; it now has a
  hard date. Authenticate it BEFORE 29 Aug. Owner R2.
- **Secrets: L9 says "execute at/near launch" — near is now 14 days.** The transcript-exposed
  set (MS_API_KEY / MS_ADMIN_PASSWORD / MS_JWT_SECRET), the 96315 reuse, and the systemd
  inline Environment= lines. Tooling ready 9 days. Before 29 Aug, not after.
- **Deploy debt: the live site on 29 Aug is whatever has SHIPPED.** 5 files local-ahead,
  1 unpushed commit, GATE-TRUTH-2/GATE-ORIGIN-1 undeployed. Ship in the sprint window,
  verify by 27 Aug.
- DW-041 (legal docs 401) self-resolves when the gate drops — but testers accepting the EULA
  need it reachable BEFORE then. App-side exemption stays on the sprint list.

## The bar (G1–G8) against the real dates

| # | Gate | Hard by | State 15 Aug |
|---|---|---|---|
| G1 | Money path: M1/M2 test pass + S5 prod flag fail-closed | 27 Aug | S5 OPEN |
| G2 | Security floor: secrets rotated, 96315 killed, IL-01 authenticated, gate posture ruled, no HIGH DW open | **29 Aug hard** | OPEN — none done |
| G3 | Deploy truth: origin/deploy == live == source; smoke ≥37/39 | 27 Aug | OPEN — 5 ahead, 30/39 |
| G4 | Instrument truth: cron parity (DW-045), BIT 8/8, FEA green, external uptime monitor | 22 Aug (review needs true instruments) | OPEN — all four |
| G5 | Fault floor: 0 CRIT / ≤3 MED open tester faults; PERF-001 resolved or ruled | 27 Aug | UNKNOWN — register off-disk |
| G6 | AI lane: P1–P6 done OR flip formally deferred, Anthropic re-pinned standing | 22 Aug decision | Session 16 Aug 09:00 |
| G7 | Legal: EULA/privacy/terms reachable, D4 supplements ruled, CPA s63 | 29 Aug | OPEN |
| G8 | Gate-board on +1 page 4, David signs on the board | **22 Aug — it IS the review instrument** | NOT BUILT |

**G6 honesty note:** with 14 days and G2–G4 on the critical path, completing P1–P6 *and* a
shadow period before 29 Aug is tight. The gate allows formal deferral — flip after launch
stabilises, Anthropic re-pinned standing meanwhile. That is a G6 GREEN by deferral, and it is
the honest default unless the 16 Aug session lands P1+P6+P2 cleanly.

## Sprint order (14 days, floor first)

1. **Now–19 Aug:** G2 items — rotate secrets, kill 96315, authenticate IL-01, rule gate
   posture, legal-doc exemption. Ship the deploy debt (G3).
2. **19–22 Aug:** G4 — smoke UA, cron parity, BIT 8/8, re-aim drift checker, uptime monitor.
   **G8 — build the gate-board**; it must exist to hold the 22 Aug review on it.
3. **22 Aug: D-7 review on the board.** GO → continue. HOLD → declared same day, zero
   narrative cost (no public promise exists until the wave emails send).
4. **23–27 Aug:** G1, G5 closure, rehearsal. 27 Aug: last ship + full smoke.
5. **29 Aug soft / 1 Sep full.**
6. **Post-launch (slip month if held):** HARNESS-PILOT-1 (EU_HARNESS_REDUNDANCY_2026-08-15.md),
   ban drill (D9), the deferred G6 flip with its shadow period.

**Wave trigger stays separate (CC-003): 60 staged prospects/city triggers a WAVE, never the
launch.** Public launch = eight gates green on the board, signed by David.
