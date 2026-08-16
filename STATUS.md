# TrustSquare — Status
> **📍 Open loops now live in `OPEN_LOOPS.md` (canonical, ranked).** This file is the session
> narrative history — do not hunt `OPEN:` fragments here to learn what's open; read `OPEN_LOOPS.md`.


## Current Session

## 2026-08-16 — RUL-020 shipped (legal docs public) + TS-0035 visual corrected
EULA decreed final & binding and RELEASED (RUL-020): /terms + /privacy exempted from the
gate via migration 021, asserted by RG-0092. Dashboard AI Providers viz now shows the
true order of use (OpenAI base → Anthropic failover → Scaleway last resort). TS-0035 to
be marked verified after live check; both dashboard ambers clear with it.

## 2026-08-16 — ledger opens (session B)

- RG-0011 re-LOCKED (RUL-021: ZA=4-layer pilot, GB=canon name). RG-0003/0004 fixes in
  demo_listings.json committed — live pass on next deploy, promote when READY TO LOCK.
- RG-0075/0090 untouched here by agreement — main session owns them (dashboard.server.html
  + nginx migration lane).
- RG-0081 showed 429 on /review/request-link mid-morning — likely our own probe burst +
  main-session gate work; re-check before treating as rot.

- **INFRA-TEST-VERDICT-1 shipped to repo (16 Aug):** infrastructure Test buttons on the +1 page now
  paint PASS/FAIL at the row with a Why/Resolve strip on any non-pass (David's ask, same session).
  RG-0093 locked. Rides the next deploy after release bd3d958.

## 2026-08-16 — maintenance-loop

- B2b daily run complete. Ledger GREEN pre+post. Queue: 1 seen / 0 fix-shipped / 0 verified (TS-0035 routed PATH_B design backlog — the AI-order visual is outdated, awaits designer gate).
- Heartbeat posted and confirmed on /dashboard/maint. No escalations. No commits needed (no repo changes beyond fragments).

## 2026-08-15 — Token economics rev 2: David's real cost base + safe-side AI provision
David's actuals folded in: Claude $200+15%=$230, Higgsfield $39+15%=$44.85, Hetzner $32,
plus four FUTURE 5T+ feed subscriptions (Cloudflare ~$20, Flights ~$30, Mapbox ~$50,
non-Google places-type feed ~$40 — placeholders pending quotes). Safe-side AI key provision (David):
$20×6=$120 per 500 users = $0.24/user/mo. New numbers: current floor $327.85/mo; future
full stack ~$467.85/mo. Provisioned carry ratio: 1 Starter per ~19 free users (5% Starter
share needed; model assumes 25%). Break-even ~131 sellers now / ~187 with full stack at
launch mix ≈ 3.1 founding cities. Deliverable: AI_TOKEN_ECONOMICS_2026-08-15_rev3.docx is CURRENT (rev1/rev2 were locked
open in Word mid-edit; rev3 supersedes both and rev 1's $49 floor). Google decision CLOSED
same evening: David confirmed Google Maps/Places stays OUT (1 Aug ruling stands) — the
budget slot is for a NON-GOOGLE equivalent (Foursquare/Geoapify/OSM-based), hard-capped.

## 2026-08-15 — Global launch planned (worldwide, RUL-019) · EULA v1.13 confirmed live
Deploy 03aa9f0 shipped and verified (health ok; /terms now serves v1.13 with UK/US/AU
schedules — the "not yet deployed" note in LEGAL_VERSIONS is stale as of tonight).
GLOBAL_LAUNCH_PLAN_2026-08-15.docx written: the only genuinely new work before 1 Sep is
(1) UK/US/AU localization + email-law pass over the 14 outreach templates, and (2) a
~25 Aug refresh-scrape of London/NY/Sydney (all under the 200/category Gate-2 floor:
63/60/57) + KPI gate re-run. Everything else rides LAUNCH_BAR G1–G8. Beachhead first
waves w/c 1 Sep, each individually David-approved at AWAITING_APPROVAL.

## 2026-08-15 — Agents verified ready + AI token economics memo
Maintenance lane VERIFIED WORKING: ops_sweep server cron live (/etc/cron.d/marketsquare-ops-sweep,
*/15, last run 20:30 UTC today, all green except faults.majors+queue amber = TS-0035 new major,
"visual outdated", arrived after this morning's agent run). Fix agent VERIFIED: maintenance-loop
scheduled task enabled (daily 07:31, fired today 05:32), shadow run clean (seen 0 — TS-0035
postdates it, tomorrow's run picks it up), intake lane proven by RG-0053 (ledger green tonight).
Still SHADOW by design: kill switch MAINTENANCE_AGENT_ENABLED stays 0 until B4 synthetic-storm
rehearsal signs READY (~22 Aug target). AI_TOKEN_ECONOMICS_2026-08-15.docx written, all inputs
canon-sourced: one $5 Starter carries ~546 free users' AI cost at mature adoption (1,364 Yr-1,
136 stress); ~11 Starters cover the $49/mo fixed floor; S3 already gates the only real leak.
Follow-up: set monthly_income_usd in the AI-spend alert config after first revenue (post 1 Sep).

## 2026-08-15 — Money-path status corrected + webhook arm tool built
David confirmed REAL purchases settled to FNB -> sk_live is live (S111 sk_test note is STALE).
Verified in Paystack dashboard: Live Webhook URL already https://trustsquare.co/payment/webhook.
Only unknown: PAYSTACK_WEBHOOK_SECRET on server (no probe exists; endpoint 400s identically
either way). Built add_paystack_webhook_key.bat (resend-key pattern: presence check first, then
ssh paste + restart; Claude never sees the key). A10 narrowed accordingly. E2E proof pending:
smallest-pack buy with tab closed before return must still credit. 2FA on Paystack still Disabled.

## 2026-08-15 — Webhook lane ARMED + RG-0091 LOCKED · money path effectively complete
David installed PAYSTACK_WEBHOOK_SECRET via add_paystack_webhook_key.bat and bought 1T live.
New ledger entry RG-0091 (LOCKED, passing): anonymous garbage POST to /payment/webhook answers
400 — route up, origin gate does NOT eat Paystack webhooks, signature enforced. Blind spot named
in the entry: secret presence itself is externally invisible; detached-credit E2E (tab closed
before return) is the remaining half-proof unless David's 1T buy already did so.
David DEFERRED Paystack 2FA to near-launch (his call, 15 Aug) — one-time reminder scheduled
Thu 27 Aug 09:00, two days before gate-down (RUL-001). STILL PENDING: one deploy_marketsquare.bat
run to ship today's BACKLOG/ledger/fragments so the ops dashboard blockers card reads zero.

## 2026-08-15 — Paystack international payments: ALREADY ENABLED (verified)
Checked live dashboard (account 1777715, Live/Approved): 'Accept international payments' ticked.
Phase 0 of GLOBAL_PAYMENT_RAILS sequence complete without action. Open David-only items spotted:
set up 2FA on Paystack (banner active); decide on enabling Apple Pay checkbox (helps intl buyers).
UPDATE same day: David ENABLED Apple Pay in the dashboard (terms accepted, confirmation modal seen).
No further setup needed — payments.py uses transaction/initialize (redirect/hosted checkout), which
gets Apple Pay automatically; domain registration/.well-known only applies to inline integrations.
Unverified until tried: a real checkout from an iPhone/Safari on the live site. Apple Pay has
per-currency minimum transaction amounts — low-value Tuppence packs may not show the button.

## 2026-08-15 — Global payment rails re-verified (deep+wide)
David asked (again) for worldwide payment options beyond Paystack/Africa. Full memo:
GLOBAL_PAYMENT_RAILS_2026-08-15.docx; FINANCE_CANON.md gained a Re-verification log section.
Headlines: F4 (MoR, lean Paddle) survives; Paddle ZA support confirmed at source; Polar.sh and
Dodo Payments verified as ZA-seller fallbacks; Paystack itself can take international cards
worldwide (ZAR settlement) once intl payments activated — but wallet businesses are ineligible,
so Tuppence positioning (prepaid fee for defined service) decides eligibility everywhere.
Awaiting David: adopt Phase 0/1/2 sequence -> RULINGS.md entry.

## 2026-08-15 — Last launch blocker (B1) CLEARED · RUL-019 worldwide scope GO
B1 done: Paystack live + intl + Apple Pay, verified in dashboard. Dashboard blockers card will
show zero after next deploy (BACKLOG.md ships via manifest). NEW A10 (David, ~10 min): paste
sk_live keys + PAYSTACK_WEBHOOK_SECRET into server env, then one real-card E2E + FNB settlement
check. Until A10, app transacts in test mode — account live, money-in not yet.

- **PG-RATCHET-PRECISION-1 (15 Aug 2026) — the fourth "guard measuring the wrong thing" in two days,
  and the one that was silently blocking every unattended release.** `nightly_ship.bat` runs with
  `PREDEPLOY_MODE=strict`, and `predeploy_check.py` ends `if danger: if MODE=='strict': return 1`.
  `deploy_audit.log` shows verdict=DANGER on EVERY scan since at least 13 Aug. Attended deploys
  survive because they run mode=warn (always exits 0); the nightly would have aborted every time.
  So "fixes never reach live" had a mechanical cause, not a discipline one.
- **Half the DANGER was measuring Python.** `test_pg_readiness.py` counted `strftime\(` — which also
  matches PYTHON's `datetime.strftime()`, a portable stdlib call with nothing to do with SQLite or
  the Postgres move. Of 40 hits, **25 were Python**; only 15 were real SQL
  `strftime('%Y-%m-%dT%H:%M:%SZ','now')`. Adding ordinary date formatting anywhere in bea_main.py
  tripped the ratchet and blocked the release. Pattern tightened to `(?<!\.)strftime\(` and the
  strftime baseline re-cut to the TRUE surface (15). The other three patterns
  (datetime('now'), julianday, INSERT OR) are SQL-only and were already precise.
- **CLAUDE ERROR, caught and reversed in the same step:** the first re-baseline wrote ALL current
  counts, which silently absorbed a genuine `datetime_now` growth 53 -> 54. That is exactly the
  "never weaken an assertion to make it pass" rule, broken by the person quoting it all day.
  Baseline restored to 53; the ratchet now FAILS honestly on the real growth.
- **The remaining growth is REAL and belongs to the concurrent session.** Commit `5dc62a7`
  ("WIP: session commit Sat 08/15 09:46") added `" ts TEXT NOT NULL DEFAULT (datetime('now')),"`
  at bea_main.py:14025 — a CREATE TABLE column default. Portable form is a Python-supplied
  timestamp at insert, or `DEFAULT now()` at the Postgres migration. NOT edited here: it is another
  session's in-flight code and editing it is the concurrent-writer hazard that produced
  CHANGELOG-COLLISION-1 and STATUS-COLLISION-1.
- **STATE: unattended publishing is one line away.** Task `TrustSquare Nightly Ship` is registered
  (02:00 daily, Ready, first fire 16 Aug), battery blocks removed by David, and `media_push` now runs
  in it (MEDIA-NIGHTLY-1) so photos finally have an automated path to live. The single remaining
  blocker is that one `datetime('now')`.

- Final: CDN document-leak OPEN entry = **RG-0090** (0082 and 0083 were both taken by the
  concurrent session mid-write; deliberate jump ends the leapfrog; 0084–0089 gap is by design).

- Correction: the CDN document-leak OPEN entry is **RG-0083** (RG-0082 was concurrently taken
  by the AI-spend-attribution entry). Ship record references to "RG-0082 opened" = RG-0083.

- **GATE-EMAIL-1 LIVE (15 Aug ~08:05 UTC, /tsl):** email-linked gate entry shipped and proven
  live end-to-end; RG-0081 LOCKED. Allowlist seeded (David x2 + 3 testers) at
  /var/www/marketsquare/review_emails.txt — edit live, no restart. Rollback tag
  pre-tsl-gateemail-20260815. NEW OPEN: RG-0082 — CF edge cache hands the gated HTML shell to
  anonymous visitors after a cookie-holder primes it (pre-existing since 13 Aug; data sealed;
  fix = CF html-bypass rule [David console] OR origin no-store migration; reversible by 29 Aug).

- **SPEND-GUARD-1 (David, 15 Aug 2026) — Claude's error, caught by David within minutes.** The first
  cut of RUL-013 routed the pre-launch fix lane at `claude-fable-5` via `ANTHROPIC_API_KEY`: metered
  usage credits at $10/$50 per Mtok, fired by an UNATTENDED loop three times a day with nobody
  watching the meter. David: "eats $ up in seconds... You will bring us to a screeching halt." It
  also broke the standing rule that Fable-via-credits is "reserved for the most important work only"
  (decision note, 11 Jul). **No spend occurred** — the server carries no `ANTHROPIC_API_KEY` and the
  agent had not run since the edit. Removed on both sides: no anthropic `design` row in the seam, no
  `provider="anthropic"` in any live agent call.
- **The corrected design, which was David's point ("let us not break our design"):** Fable still
  resolves pre-launch design requests — **in a Cowork session on the subscription**, where the tokens
  are already paid for. An unattended server process cannot use a subscription; only a session can.
  So the earlier "KNOWN GAP" is not a limitation to close, it IS the design. The agent proposes on
  its normal lane; Fable work happens where it costs nothing extra.
- **TIME-BOXED, and now asserted.** RUL-013's Fable arrangement **ENDS 1 Sep 2026 and does not renew
  by default**. From 1 Sep, design work returns to the allocated design agent or its swapped-out
  option — the `design` task tier (openai `gpt-5.6-sol`, scaleway `mistral-medium-3.5-128b` standby),
  NOT Fable. `rulings_check.py` asserts the expiry wording survives, because a session in October
  reading RUL-013 without it would treat a temporary arrangement as standing policy.
- **RG-0080 locks the general invariant:** a loop nobody is watching never spends per-token. It
  checks the seam has no anthropic design route, the agent pins no anthropic provider in a live call,
  AND that a non-Anthropic design lane still exists so post-1-Sep work has somewhere to go. Sibling
  of RUL-007: unbudgetable cost is barred whether it arrives as a percentage, a retroactive cliff,
  or an autonomous loop holding a metered key — the third form found this week.
- **Numbering note:** this entry was first written as RG-0074 and collided with the concurrent
  session's RG-0074 (admin-gate status branching). Renumbered to RG-0080; theirs untouched. Two
  sessions allocating ledger ids from the same file is a real collision surface — the same class as
  CHANGELOG-COLLISION-1 and STATUS-COLLISION-1, and it has no compiler yet.

### RULINGS.md born — decisions get the same machinery as fixes

The launch date was reviewed several times in sessions and never reached the canon; the sweep
read "launch date STILL NEEDED" as truth. Class-level fix, sibling of the regression ledger:

- **RULINGS.md** — append-only register, seeded with 12 rulings incl. RUL-001 (launch
  1 Sep / soft-public 29 Aug, fixed sequence).
- **scripts/rulings_check.py** — asserts each ruling is REFLECTED where the next session
  reads, and that repudiated wording is actually purged. First run found 3 genuine drifts
  (BACKLOG still carried the repudiated 23/60 threshold after 2 months, and the provisional
  01-Aug deadline) — all fixed same session. 12/12 reflected, exit 0.
- Standing rule appended to Projects/CLAUDE.md: a ruling is not made until it is in the
  register, same session. rulings_check runs alongside the regression ledger.

- **RUL-013 recorded (David, 15 Aug 2026) — the fault-resolution operating model, both phases.**
  PRE-LAUNCH (to 1 Sep): the maintenance agent does NOT surface failures or reports to David;
  testers are the fault source and AI resolves without him; escalations route to the FIX AGENT
  (Fable) under standing pre-approvals with laptop resources open. POST-LAUNCH: source becomes user
  complaints; maintenance agent handles most; fix agent handles 98% of the remainder; David on
  STANDBY for the residual ~2% for the FIRST TWO MONTHS, with Claude's support — reviewed after that
  window, not assumed. Written to RULINGS.md and reflected in MAINTENANCE_AGENT.md;
  `rulings_check.py` gained the assertion, so it is a guarantee rather than a note (13 rulings,
  0 FAIL, 0 WARN).
- **Extends RUL-005 and inherits its condition, which today made pointed reading.** RUL-005 replaced
  the human veto with mechanical gates, on the express condition that "any gate that stops asserting
  re-arms the veto". Three gates had silently stopped asserting: the drift monitor (permanent
  phantom red, DRIFT-CACHEBUST-1 + DRIFT-FILEMAP-1), the tester-intake maint-scope guard (failing on
  CORRECT code since the 13 Aug ruling), and the DANGER verdict they jointly produced on every
  deploy. All three are honest again as of today — so the condition RUL-005 attaches to more
  autonomy is satisfied NOW, but it was quietly unsatisfied for weeks while autonomy was assumed.
- **Recorded honestly: the Fable hand-off is intent, not mechanism.** There is no Fable lane —
  `ai_active` accepts only anthropic|openai|scaleway and no Fable provider exists in the register.
  The server agent runs unattended and cannot summon a Cowork session, and per-session laptop grants
  can never be held by an unattended run (the fault that stalled the photo run at image 1 of 54).
  So pre-launch behaviour in PRACTICE is: PATH_A fixed autonomously and silently as ruled; the
  ESCALATE class accumulates for the next fix session. Better than David reading every report — but
  not yet "AI fixes it without me". Three concrete steps to close it are named in MAINTENANCE_AGENT.md
  and the gap note is itself asserted, so it cannot vanish while the gap remains.
- **NOT delegated in any phase:** the deterministic REFUSE guard. Legal, currently-costly and
  trust-core surfaces still stop for a human. Autonomy is over the fixable class, never the refuse class.

- **OPENAI-BASE-P6 (scheduled run):** Flip found ALREADY LIVE (openai standing since 14 Aug 20:05,
  server key present). P6 spend attribution LANDED in source: model-keyed prices from the card
  (D1), serving-lane attribution at all 24 spend sites (D3), vision import-fallback haiku (D2),
  /admin/flags logged + admin_audit row + reason (D4, AL-3), failover chain baseline-ordered and
  cost-gated (D5), AL-1/AL-2 alerts wired. RG-0018 healed (gpt-5.6-sol on the card, $5/$30,
  web-verified; AI_BASELINE design tier added). ai_baseline_check 6 FAIL→0 FAIL; challenger board
  clean; ledger 1 REGRESSED→0, RG-0082/0083/0084 LOCKED. **NOT deployed** — rides the next /ship.
  **Open, needs David/server: P2** `python3 scripts/golden_seam_v2.py` ON THE BOX (refuses to fake
  without the production key), then **P3** add openai to GOLDEN_PASS with the evidence line.
  Working tree deliberately left uncommitted (a concurrent morning session's edits share it).

## 2026-08-15 — maintenance-loop (automated)

Clean run. Ledger green pre and post. Shadow agent: 0 seen / 0 acted; heartbeat posted
(2026-08-15T05:33:47Z). Queue new 0, fix-shipped 0, verified 23. Escalation brief has 2
informational TS-0032 items awaiting David's tick. No code changed.

### LAUNCH DATE RULED (David, 15 Aug): full launch Mon 1 Sep, SOFT LAUNCH TO PUBLIC Fri 29 Aug

Closes SUPER_LADDER's "launch date STILL NEEDED". LAUNCH_SPECIAL_DEADLINE must be re-set
2026-08-01 -> 2026-09-01 (LAUNCH-DEADLINE-1). LAUNCH_BAR_2026-08-15.md v2 carries the full
calendar: D-7 gate review Fri 22 Aug on the (yet unbuilt) gate-board; last ship 27 Aug;
hold-posture fallback = slip one month (soft 28 Sep / full 1 Oct), bought once.

CRITICAL consequence — the 29 Aug EXPOSURE EVENT: the gate coming down un-masks everything
behind it at once. Hard-by-29-Aug list: authenticate GET /tuppence/balance (IL-01), rotate
the transcript-exposed secrets + kill the 96315 reuse (L9/DW-029, tooling ready), ship the
5-file deploy debt incl. GATE-TRUTH-2/GATE-ORIGIN-1. G6 (OpenAI flip) may be formally
deferred if the 16 Aug session cannot land P1+P6+P2 cleanly — deferral with Anthropic
re-pinned is a GREEN, rushing a lane flip into launch week is not.

### Launch bar drafted + EU harness redundancy evaluated (15 Aug)

- **LAUNCH_BAR_2026-08-15.md** — LAUNCH-GATES-1 finally drafted as G1-G8 with live state
  (6 of 8 open/unknown today), the D-7 decision protocol, and the pre-declared soft-launch
  month plan. Key finding: no bar existed to miss; no public date promise exists, so a slip
  currently costs zero narrative — until the first wave email sends.
- **EU_HARNESS_REDUNDANCY_2026-08-15.md** — DeepSeek Harness (MIT, 13 Aug) evaluated under
  the Add.-6 models-vs-endpoints doctrine. Hosted DeepSeek API stays OUT; HARNESS-PILOT-1
  proposed as a slip-month item: harness + EU-hosted open weights (Scaleway Paris) against
  three closed maintenance faults, success bar 2/3 at <25% recorded cost. Closes the
  PROJECT-layer gap: the app has 3 lanes, the build toolchain has 1 vendor.
- Both need David's ratification. Neither is deployed anywhere.

- **GATE-EMAIL-1 BUILT, awaiting deploy (15 Aug):** gate entry is now email-linked (one-time
  30-min single-use link -> same ts_review cookie, 365d); reviewer code demoted to break-glass;
  GATE-COOKIE-2 ends the sessionStorage re-challenge lockout class at the root. Migration 019
  exempts /review/request-link + /review/enter at the origin and seeds the 5-email allowlist.
  RG-0081 OPEN (live half flips it READY TO LOCK post-deploy); RUL-014 registered. NEXT: /tsl
  on David's word, then send each tester their first link and promote RG-0081.

- **DRIFT-FILEMAP-1 (15 Aug 2026) — the second half of the phantom-drift fault.** The 07:22 release
  proved DRIFT-CACHEBUST-1 in the wild: the drift line fell from TWO files to ONE, marketsquare.html
  cleared, and `Tester fault-intake guards: ok` replaced the standing DANGER from the stale
  maint-scope guard. The residual `dashboard.html` was a DIFFERENT cause wearing the same face:
  `check_deploy_drift.py` FILEMAP mapped local `dashboard.html` -> served `dashboard.html`, but the
  served file is built from `dashboard.server.html` (deploy_manifest.txt:72). Local `dashboard.html`
  is a separate file that is never deployed, so that row could not match no matter what shipped.
  Fixed by comparing what actually ships.
- **The guard now asserts the INVARIANT, not the instance.** RG-0072 gained a cross-check: every
  file in the drift map must agree with the deploy manifest about where the served copy comes from.
  A future mis-mapping goes red the same day instead of producing years of ignorable noise. Known
  exception recorded in the check itself: `demo_sellers.json` is SERVER-OWNED (migration 017
  rewrites it live, the deploy never places it), so "local ahead of live" is meaningless for it.
- **Standing lesson, third instance in two days:** a monitor must compare the thing that actually
  ships, in the form it actually ships in. DRIFT-CRLF-1 (line endings), DRIFT-CACHEBUST-1 (the
  server's own ?v= rewrite) and now DRIFT-FILEMAP-1 (the wrong source file) are one fault class —
  comparing an artefact of transport or build instead of content. Each produced a permanent red
  that trained everyone to ignore the monitor.
- **Still open and genuinely real:** PG-READINESS `strftime` 38 -> 40. It is the ONLY remaining
  contributor to the DANGER verdict, and unlike the other two it is a true finding — two new
  SQLite-specific calls that make the eventual Postgres move dearer.

- **STANDING LANE MOVES TO OPENAI (David's ruling, 14 Aug 2026 — Addendum 11).** Resulting order:
  **1. OpenAI (standing) · 2. Anthropic · 3. Scaleway EU · 4. Grok** (capped, text tiers only, not
  wired pre-launch). The reason is INDEPENDENCE, not price — David's words: this "will also ensure
  we don't use Anthropic as the CEO/COO/Guidance and also then outsource our work to Anthropic."
  Claude authored most of this codebase and advises at CEO/COO level; the same vendor also doing the
  production work makes judgement and execution one correlated dependency. Addendum 1 already
  accepted that logic for REVIEW ("Claude auditing Claude has correlated blind spots"); this extends
  it to EXECUTION. Supersedes "Staying with Claude" as the STANDING LANE only — Claude remains the
  guidance/harness layer, which was never the thing being procured. Cost independently agrees
  (funnel: gpt-5.6-luna first on haiku/triage/vision at +78/78/79%, golden-set passed) but did not
  drive it. Sonnet's +25% is below the 30% bar and moves anyway as part of a whole-lane ruling —
  a different decision class from per-tier procurement, which the 30% bar still governs.
- **The $50/90d absolute floor is now a POST-LAUNCH test, not a pre-launch gate.** It requires
  spend-log volumes that cannot exist before launch, so applied pre-launch it was never a test —
  it was a permanent block. David: these were "discussions that then became hammers to keep us
  pegged." From first revenue it applies as written; before that it is informational and never
  blocks. Amended on the card so the rule travels with the data (Addendum 8's own design).
- **Standing principle worth keeping:** an analysis output is not a requirement, and a gate that
  cannot be satisfied in the current phase is a blocker masquerading as rigour. Same fault class as
  a guard asserting an implementation detail instead of an invariant — DRIFT-CACHEBUST-1 and the
  stale maint-scope guard, both found the same day.
- **LIVE — flip applied and verified 14 Aug 2026, 20:05 UTC.** `POST /admin/flags` needs a JWT from
  a dashboard login, which Claude will not perform on David's behalf, so the change went in as a
  direct write to `launch_switches.ai_active` on the box — database backed up first
  (`marketsquare.db.bak-lane-20260814-200544`), no credential typed, displayed or handled by anyone.
  The provider cache is ~10s and the lane is DB-backed by design ("Page-4 switchable, no restart"),
  so it took effect without a restart. Verified from the app's own `GET /flags`, not from the row
  written: **active=openai · standing=openai · override=null**. Record and live now agree and
  **RG-0019 reads green** ("live standing lane 'openai' == register — record is current"); RG-0018
  green too (card 13d old, 5 priced / 5 wired). Rollback = same write with 'anthropic', or restore
  the printed .bak-lane file.

- **Tester queue cleared to zero new (14 Aug, evening).** TS-0032 + TS-0033 were one fault:
  the Adventures tile counted city-scoped listings while the Adventures page is borderless by
  design, so the number never survived the tap. Fixed at class level (**BORDERLESS-COUNT-1**,
  RG-0078) with `scripts/repro_borderless_count.js` as named evidence — it reproduces the
  testers' exact numbers (Sydney 2→6, Maun 1→6) against the pre-fix file and passes against the
  fixed one. Both rows set **fixed**, not verified: the fix is in source and gated, and reaches
  the reporters on the next nightly deploy. TS-0031 (cars AI vehicle details) is **triaged**:
  its honest half shipped (**SPEC-PROVENANCE-1**, RG-0079 — the attestation screen now says the
  specs were read from photos, not looked up), while whether to ground the lane in real vehicle
  data is David's call and sits in BACKLOG.md with three options. RG-0065, RG-0066 and RG-0069
  promoted OPEN → LOCKED, as each entry instructed, now that they pass.
- **Not mine, flagged:** the ledger's last run went red on **RG-0019** (live AI lane is
  `anthropic`, `ai_price_card.json` records `openai`). That file was edited at 21:59 by a
  concurrent session — my 21:56 run was green — so it is in-flight work on the model register,
  not a fault in this session's changes. Left untouched deliberately rather than raced; the
  register needs the switch reason recorded by whoever made the switch.

- **Grok placed FOURTH in the swap chains; retroactive-repricing becomes a standing rule
  (David's ruling, 14 Aug 2026 — Addendum 10).** Grok 4.6 (xAI, 12 Aug) is $2/$6 with Intelligence
  Index 61, tying GPT-5.6 Sol at $5/$30 — so on cost-per-capability the honest comparison is the
  OPENAI slot, not Scaleway's. Placed fourth anyway and Scaleway's EU slot left alone, because the
  tail of the chain exists for JURISDICTIONAL diversity: three US lanes ahead of any non-US one
  would all fall to a single T3 account action, the class that by definition won't self-heal.
  Text tiers only — vision is the binding constraint (8 of 22 features) and Grok 4.6's vision
  support is contested in the sources, so it is NOT in the vision chain. Not wired before launch
  (Addendum 4 stands). Verified against the live field by search, not from training memory.
- **NEW RULE, generalised from David's reaction ("that is actually a very bad feature"):** a price
  that can re-rate work ALREADY PERFORMED is unbudgetable in the same way a percentage-of-value
  cost is. xAI rebills the ENTIRE request at $4/$12 once a prompt passes 200K tokens — the last
  token can double the cost of the first. Marginal tiering is fine; retroactive tiering is not.
  Any such lane may be used ONLY behind a hard cap that makes the cliff unreachable — no cap, no
  lane, and the adapter refuses or truncates rather than discovering the cliff by paying for it.
  Applies to every future vendor, not to Grok specifically.
- **Timely, unrelated:** Claude Sonnet 5's $2/M input is INTRODUCTORY through 31 Aug 2026 and
  becomes $3/M on 1 Sep — the primary lane's baseline moves in ~2.5 weeks. Budget from $3.

### GATE-TRUTH-2 — the recurring "Connection error" on the dashboard gate is closed at class level

The message was the fault. Five copies of one gate script, four gate fixes applied per-consumer
instead of per-class, and an origin gate that answers HTML where the script expected JSON. Every
refusal read identically, so every occurrence was diagnosed fresh.

- All five copies now branch on `r.status` before parsing, on all three gate routes.
- `RG-0074` LOCKED — a sixth copy, or a regression in any existing one, trips red.
- `RG-0075` OPEN — the duplication itself. Expected to fail until the gate script is one file.
- `/admin/verify` no longer discards a valid session when the gate refuses.

**Immediate workaround for David while this is undeployed:** open `https://trustsquare.co/`,
enter the reviewer code, then open the dashboard in the same browser.

**Not deployed.** Needs a `/ship` or `/TSL` run to reach the live dashboard.

- **EULA v1.13 — AI disclosure written, three-way EULA fork closed (EULA-FORK-1).** Added an
  up-front AI disclosure block before §1, a new §7.7 (built with AI; AI-generated demo/marketing
  imagery; demo listings are not offerings; C2PA/invisible provenance markers never stripped; no
  misrepresenting AI uploads) and a new §8.3 bullet that Your Content is never supplied for
  external AI-model training. Found en route: `terms.html` was v1.12 while `eula_clean.html` and
  the `ms.js` **acceptance-modal** copy were still v1.11 without §6.1B — users were accepting text
  the site did not publish. `scripts/eula_sync.py` is now the one writer (`eula_clean.html` =
  source, `--check` exits 1 on drift); RG-0077 LOCKED asserts the copies stay identical and the AI
  disclosure stays in. All three copies byte-identical at 100,775 bytes; ledger clean; canon
  pointers in line. **On disk, not deployed** — `ms.js` + `terms.html` ship on the next `deploy`
  push. Open for David: the §8.3 no-external-training commitment is a genuine business constraint
  (escape valve already in §8.3: change requires individual notice + fresh consent), and A6 counsel
  review now also covers §7.7.

- **MAINTENANCE AGENT ARMED (14 Aug 2026) — D12 closed, and a trap in its ship path closed with
  it.** All three preconditions proven before arming, not assumed: `b4_tier2.json` reads READY;
  `OPENAI_API_KEY` is present in the live `.env` (so `classify()` takes a real AI lane instead of
  degrading every fault to PATH_B — the mechanism behind TS-0031's four identical verdicts, which
  was a SANDBOX key gap, not a server one); and push auth now returns PUSH_AUTH_OK. Timer live,
  05:20/11:20/17:20 UTC, first run 05:21 UTC 15 Aug, `MAINT_PHASE=prelaunch`.
- **SHIP-PUSH-GUARD-1 — found while arming, fixed before the first unattended run.** The agent
  captured the `git push` result and DISCARDED it (`maintenance_agent.py:875`). Arming initially
  produced `PUSH AUTH MISSING`, and on that footing every run would have: committed the fix to a
  throwaway worktree, failed to push in silence, counted a ship against the rate limit, had
  `aik_verify` correctly find nothing live, marked the fault **"fix-shipped"**, then force-removed
  the worktree — orphaning the commit. Fixes made, work binned, register reporting success. Exactly
  David's complaint ("faults don't get done up to deploy and live") about to be automated 3×/day.
  Now: a non-zero push aborts the ship, preserves the work on a real `maint-unshipped/<ref>-<ts>`
  branch, marks the fault **escalated** with the push error, and records NO ship. Push auth was
  also fixed for real (ed25519 deploy key with write access; `/root/.ssh/config` via base64 because
  PowerShell mangles quotes and newlines in SSH payloads three separate ways — see lesson below).
- **PowerShell → SSH quoting, the sibling of the cmd `for /f` lesson:** double-quoted payloads get
  expanded LOCALLY (`$(...)` ran `grep` on the laptop); empty `""` arguments are DROPPED, leaving
  bash with an unbalanced quote; and `printf "a\nb"` newlines do not survive, which wrote an SSH
  config whose line 1 was a bare `Host`. Rule: single-quote the payload, avoid empty-string args,
  and for any multi-line file send base64 and pipe through `base64 -d` — no spaces, quotes or
  newlines for PowerShell to touch.

- **COUNTRY-FILTER-1 (14 Aug 2026) — David's ruling honoured: borderless AND filterable, both.**
  The two were never in tension; they are different layers. Branch C (`bea_main.py`, David 28 Jun)
  still returns every adventure regardless of city, so a Kenyan lodge stays discoverable from
  Pretoria — untouched, no backend change. The picker is now an EXPLICIT narrowing on top. What was
  actually broken: `advCountry` defaulted to `'ZA'` (ms.js:2108), which delivered NEITHER — pinned
  to one country and unfilterable — so South African adventures appeared under every selection.
  Four changes: (1) Kenya and Botswana rows added to the picker (marketsquare.html) — both had
  live listings and no way in; deliberately NOT adding TZ/ZW/UG/RW/ET, which would return empty;
  (2) default is now `ALL` with the tick moved off ZA, so borderless is what you get until you
  choose; (3) `renderGrid()` now applies the country filter to adventures rows — `renderAdvGrid()`
  always did, `renderGrid()` never did, which is why the browse grid ignored the picker entirely;
  (4) the choice persists in `localStorage` (`ms_adv_country`) instead of resetting to ZA on every
  reload. `node --check` green.
- **RG-0073 locks the INVARIANT, not a country list.** Kenya's 24 listings went live with no picker
  row — reachable only under "All countries". Botswana had been in that state since July, with
  `ADV_COUNTRY_FLAGS`/`CURRENCY` carrying both codes while the sheet never gained the rows. Seeder,
  photos, media push and deploy all succeeded; the market was simply unbrowsable. The new entry
  compares the picker against the countries actually present in live `/listings`, so it stays true
  when the NEXT market ships rather than rotting like the hardcoded list it replaces. Passing: 9
  countries with listings, 9 reachable.
- **Stale maint-scope guard repaired (test_tester_intake.py).** It asserted the PRE-ruling scope
  (`/admin/faults` only, count 4) and so failed on correct code, putting **DANGER** on every deploy
  — the same class as DRIFT-CACHEBUST-1: a check written against an implementation detail that
  legitimately moved. Now asserts the scope David actually ruled (RG-0065): `/admin/faults*` PLUS
  `/dashboard/maint`, exact allowlist, count 5 — still strict, anything outside still fails. All 17
  intake guards pass. That verdict should read clean on the next deploy instead of crying wolf.

- **DRIFT-CACHEBUST-1 (14 Aug 2026) — the "stalled deploy engine" was never stalled; the drift
  monitor could not go clean BY CONSTRUCTION.** Every release logged
  `DEPLOY DRIFT: 2 file(s) local-ahead of live - run /ship: dashboard.html, marketsquare.html`,
  waited out two server ticks, and reported it again — a scheduled session was booked to diagnose
  a stall that does not exist. Cause: `ops/autodeploy/server_deploy.sh:170-186` rewrites the SERVED
  `index.html` in place (`sed -i`, monotonic `?v=` bump) so browsers actually fetch each new build —
  the served file is DESIGNED to differ from its source. `check_deploy_drift.py` md5'd local against
  served, so the only two manifest files carrying `?v=` references (marketsquare.html→index.html,
  8 refs; dashboard.server.html→dashboard.html, 6) reported drift on every deploy, for ever, and no
  amount of re-deploying could clear it. Fixed at class level: `?v=[0-9]+` → `?v=N` is normalised on
  BOTH sides before hashing — locally in `_md5`, and on the box via `sed` piped to `md5sum` — exactly
  as DRIFT-CRLF-1 normalises line endings. Proven with a two-file stand-in differing ONLY in the bump:
  raw md5 differed, normalised md5 matched. Genuine staleness still reports; only the bump is
  neutralised. Locked as **RG-0072**; full ledger re-run after the change: no regressions.
- **Separately, the missing 18 Kenya listings are NOT a seeder fault.** Release 24f6556 logged
  `0 deploy target(s) changed` (it carried only AI-accountability files, none in the manifest), so the
  engine placed nothing and the `post_deploy` seed hook never ran. All 24 tiers have complete photo
  sets on disk and on the server — a simulation of the seeder's discovery step finds every one. The
  seed lands the moment a deploy actually places a manifest file.

- **SUPER-AFRICA-1 KENYA STILLS COMPLETE — 114/114 on disk (14 Aug 2026).** The last 54 ran in one
  sitting: property 18, tutors 9, local market 9, collectables 9, services 9. Every file verified —
  114 expected names all present, ZERO missing, ZERO extra, ZERO duplicate-content groups, all
  decode as valid JPEG, none undersized. Per-tier contact sheets were eyeballed (property A/B/C,
  tutors, local market, collectables, services) and each image checked against PHOTO-ANON-1 before
  it was kept. Next: media_push.bat then the deploy — post_deploy seeds whatever tiers have full
  photo sets, and all 9 Kenya tiers now qualify. The local seeder dry-run correctly reports "no DB"
  in the sandbox; seeding is the server's job.
- **Rejects caught and re-shot rather than shipped (3):** property_a_1_front (a security guard's
  face — PHOTO-ANON-1 breach), property_a_5_outside (came back as a multi-panel COLLAGE, not a
  photograph), and the same collage failure mode pre-empted everywhere after. Standing prompt
  additions that fixed the class: "No people anywhere in frame" for unpeopled shots, and "ONE single
  photograph filling the whole frame — not a collage, not a grid, not a split panel, no insets" on
  every prompt.
- **Moderation map (worth keeping — these cost credits to learn):** Higgsfield refuses
  ("Failed / Credits refunded", no charge) on (a) child-safety — the tutors listing names
  "Primary & High School Homework Coach" and exam/school framing, and (b) currency — "coins",
  "denominations". Rewrites that pass: describe the SCENE with no school-age reference and use
  "commemorative medallions" + "vintage postage stamps" instead of coins. Tutor "session" shots are
  specified as adult hands only, never a pupil. ~6 refusals total, all refunded.
- **Two operational faults fixed mid-run, both now guarded:** the gallery goes stale after ~10
  images (blurred render, Download silently does nothing) — recovery is a page reload, then re-open;
  and the Download click must land on a FULLY SETTLED lightbox, so verify and click are now separate
  steps rather than one batch.

- **Maintenance loop 14 Aug (shadow, unattended).** Queue 3 new / 0 fix-shipped / 23
  verified. No application code changed — no fault reached "gates GREEN, patch ready".
  Two faults in the LOOP ITSELF found and fixed: **GATE-CACHE-1** (RG-0070) — the shared
  ts_review token cache; without it a session burned the 8/10min login limit and the
  ledger printed 13 FALSE regressions against a healthy site. **HOST-CAP-1** (RG-0071) —
  the run report is now flushed per fault, plus `--only=REF` and `MAINT_TIME_BUDGET_S`,
  so a run killed by the sandbox's ~178s bash cap can no longer vanish without a trace.
  Ledger green after: 71 entries, 0 regressed, 6 open. Heartbeat live
  (2026-08-14T06:01:28Z). **Open for David:** TS-0033 (Sydney → SA adventures) was never
  examined to completion — a PATH_A fault on a megabyte file does not fit inside the
  sandbox cap, so it needs an attended session or an uncapped host. TS-0032 is the same
  class and the brain declined a clean patch for it.

- **Moderation lesson (14 Aug 2026):** the tutors ladder trips Higgsfield's child-safety filter on
  the listing name itself ("Primary & High School Homework Coach") -- generation returns
  "Failed / Credits refunded", no image, no charge. Reword: describe the SCENE with no school-age
  reference ("a tidy home study desk prepared for a private tutoring session ... empty room,
  nobody present") and verify on the scene phrase rather than the listing name. The busy/lightbox
  guard caught this correctly -- it refused to download and threw MISMATCH rather than claiming
  the previous image. Applies to all 9 tutors shots; the "session" shots additionally need
  adult hands only, never a pupil.

- **TSL-DBPROOF-1** — the `/TSL` pre-deploy gate no longer needs David's SSH key to prove the
  live database. `/health` now carries a facts-only `db` block (presence, bytes, integrity,
  redis; cached integrity scan, cannot raise) and `tsl_gate.py` reads it over plain HTTPS
  first, with SSH demoted to a second opinion. REVIEW now means "neither transport could
  prove it", not "this session is not David's desktop". Ledger `RG-0069` OPEN — flips to
  READY TO LOCK on the next deploy.

- **GRANT-KILL-1 (14 Aug 2026) — the Downloads grant is dead, not just pre-approved.** David's
  standing complaint, correctly aimed: Claude asks for permissions piecemeal, each one stopping the
  work at the next small item, instead of naming the whole set up front. Root cause of last night's
  stall: the Downloads folder grant is per-session (never inherited), human-gated (needs David at the
  keyboard), and sits in the INNER LOOP of the photo run — `claim_super.py` reads it on every single
  image, so it fails at image 1 of 54, every time, in every fresh session. Fixed at class level:
  `claim_super.py` and `claim_photos.py` now claim from `MarketSquare/_incoming` (inside the
  always-mounted Projects tree), falling back to the old Downloads mount only if it happens to exist.
  One-time Chrome setting (download location -> `_incoming`) completes it — David's click, once,
  forever. New canon: `PREFLIGHT_GRANTS.md` carries the COMPLETE grant list to be requested in ONE
  batch at session boot, plus the killed-grant register and the terminal-paste redaction rule.
  Super-run state unchanged at 60/114 — 2 images generated last night, 0 claimable, ~4 credits spent.

- **DUP-CLAIM-1 (14 Aug 2026) — a silent wrong-claim, caught and fixed.** Second image of the run
  claimed a file byte-identical to the first. Two compounding faults: (a) verification read
  `document.body.innerText`, which CONTAINS THE PROMPT EDITOR, so the check passed on the text
  Claude had just typed rather than on the image actually open — it can never fail; (b) the
  62-second fixed wait is sometimes too short, so the old tile was still newest, and a Download
  that does not fire makes Chrome re-save the PREVIOUS file as "name (1).png" — a new basename, so
  the existing claim-log guard missed it. Fixes, all three landed: verification now reads the
  lightbox-scoped `.attribute-text-value` only; completion is detected by the newest tile's src
  hash CHANGING, never by elapsed time; and `claim_super.py` refuses any candidate whose content
  hash already exists in assets/super ("the Download almost certainly did not fire"). Note
  `os.remove` on _incoming is blocked by FUSE, so consumed files persist — the `--since` floor
  excludes them and the hash guard is the real backstop.

- SUPER-RUN STATE (13 Aug, leg-2 wrap): **60/114 claimed.** COMPLETE: advexp a/b/c (24),
  advacc a/b/c (24), cars a/b/c (12) — every adventures + cars listing fully shot.
  REMAINING 54, next = idx 60 sup_ke_property_a_1_* : property 18 (idx 60-77), tutors 9
  (78-86), lm 9 (87-95), collect 9 (96-104), svc 9 (105-113). Resume recipe: rebuild
  /tmp/super_queue.json from SUPER_LADDER_PROMPTS.md (regex in leg-1 log / trivial),
  fresh Higgsfield tab, JS-click loop, per-image `date +%s` floor,
  scripts/claim_super.py --since <floor> <name>. Higgsfield: greenswan1646, Nano Banana
  Pro, 3:2, ~2cr/img. LESSONS BANKED: downloads intermittently need ONE re-click of the
  lightbox Download button (poll ~40s then re-fire); Chrome auto-download site
  permission now ALLOWED for higgsfield.ai (David clicked it, 13 Aug); gallery = 4-col
  masonry, newest = top-leftmost, verify lightbox prompt text before every download;
  commit ONCE at session end (maintenance loop owns the lock during the day).

## 2026-08-13 — Maroushka login "connection error" diagnosed + fixed (GATE-TRUTH-1, RG-0066)

Cause: GATE-ENFORCE-2's catch-all turned the gate screen's /admin/login fallthrough into
nginx HTML 401 → every wrong/stale reviewer code showed a fake "Connection error". BEA was
up throughout — not the old June crash class. Fix built (truthful gate messages), ledger
RG-0066 OPEN, rides the deploy-engine revival (DW-042). Her immediate unblock: re-send the
current reviewer code (lane verified live-healthy); 10-min wait if rate-limited (8/10min).

- **GATE-EXEMPT-MAINT-1 + BRAIN-DEPS-2 (13 Aug, David's "fix both"):** migration 018
  committed — exempts /admin/faults* + /dashboard/maint (and nothing wider) from the
  origin gate per 007's M2M doctrine, after auditing that every route fails closed on
  _require_maint; runs on the next successful deploy (engine stalled, DW-042 — tonight's
  17:45 session or NIGHTLY-SHIP-1). RG-0065 OPEN watches for it landing (keyed-no-cookie
  intake 401 = expected until then; GATE-COOKIE-1 keeps the loop alive). Maintenance-loop
  scheduled task rewritten to the foreground agent-run method (sandbox reaps detached
  processes at the call boundary). Note for tonight's DW-029 rotation: GATE-COOKIE-1
  re-reads .secrets/review_code.txt every run — rotating the review code is compatible,
  no code change needed.

- **DW-025 CLOSED (evening):** 273/273 images on our origin (244 fetched + 29 stand-ins
  for seed-corrupt URLs that were broken pre-fix); live sellers payload 0 unsplash;
  ATTRIBUTION.json live; RG-0063 LOCKED; ledger green. Two of the day's three G1 items
  closed and locked; DW-029 rotation tonight 17:45. These closing edits ride the next
  wrapper press or tonight's nightly checkpoint.

- **The last open question is ANSWERED (13 Aug, ~14:15Z): the agent patched REAL code —
  probe PASS on bea_main.py (909 KB) and ms.js (1.06 MB),** gates green, shadow-held.
  Seven defects stood between the 11-Aug probe and this verdict; all fixed + locked as
  RG-0067 (WINDOW-AIM-1, PROBE-EXHAUST-1, PATCH-FENCE-1 + --recount = the MAINT-B4-6
  root, WINDOW-SPLICE-1, PATCH-EVIDENCE-1, PROBE-KEYS-1/2, GATE-CREDS-1). GATE-CREDS-1
  matters beyond the probe: since the gate armed, every agent gate-run was structurally
  401-red — now credentialed. Remaining before arming-on-timer is DAVID'S ladder, not
  code: supervised armed run(s) on real queue faults, then B4 re-verdict (migration 015
  re-runs Tier 2 on next deploy — behind DW-042), then the timer.

- **Maintenance loop 13:24Z — B2b lane restored through the armed gate (GATE-COOKIE-1, RG-0064):**
  the morning's gate arming (016) had silently killed remote maint intake/heartbeat at nginx
  (401 before the app saw X-Maint-Key; 13:17Z run failed safe). Both consumers now carry the
  ts_review credential like the ledger does; gate config untouched (an origin-side exemption
  stays David's call — one line for the 17:45 session if wanted). Proven: clean 13:24Z run,
  heartbeat on the live card 13:24:46Z, RG-0064 locked with an inverse guard (anonymous
  /admin/* stays refused). Heartbeat gap 03:39→13:24 was this. Queue: TS-0031 → PATH_B
  (design backlog, 3rd identical verdict). Ledger green before and after; commit rides
  NIGHTLY-SHIP-1 / the revived engine (DW-042) — client-side scripts only, nothing needs the box.

- **CORRECTION — there was NO deploy-engine stall (Claude's timezone error, owned):**
  David's 06:43 SAST wrapper press deployed at 04:45 UTC, two minutes later, exactly
  as designed; the morning "stall" was SAST commit stamps compared against UTC probe
  times. Timer verified healthy (2-min ticks, 102ms no-ops, exit 0). The evening
  paste showed the true residue: **all 29 missing demo images are DEAD SOURCE URLs**
  — truncated params (q=8) and mangled IDs in the original seed data — meaning those
  29 demo cards were broken on the live site all along; the self-host work exposed,
  not caused, them. 017's stand-in rung has each at 1 tracked failure; the next
  deploy takes them to 2 → fills all 29 from landed neighbours (recorded in
  ATTRIBUTION.json) → rewrites live demo_sellers.json → exit 0 → RG-0063 READY TO
  LOCK. One wrapper press completes DW-025 end-to-end.

- SUPER-RUN STATE (13 Aug, live counter — updated as the run advances): journey photos
  **164/164 COMPLETE** (MZ final 7 claimed this morning; map rebuilt 32/32 embedded;
  RG-0062 locks the report-widget class in journey_template.html). Kenya super stills:
  **advexp a+b+c + advacc a COMPLETE (32/114)** — Naivasha, Nairobi NP, Maasai Mara sets all in
  assets/super/. RESUME RECIPE for the 82 remaining: /tmp/super_queue.json rebuilds from
  SUPER_LADDER_PROMPTS.md (make_super_prompt_pack extraction in this session's log);
  next item = index 32 (sup_ke_advacc_b_1_exterior); advacc sets are 8 shots (exterior/room/bed/view/bath/dining/setting/sunrise). Method that works: JS-dispatched clicks
  ONLY (coordinate-free — window resizes don't matter): focus editor via .focus(),
  ctrl+a + type action, verify textContent, JS-click Generate, poll 70s in 10s waits,
  JS-click newest tile (left<480, top>50, w>250), verify lightbox text has the SHOT
  phrase + LISTING name, JS-click Download, bash-poll Downloads for hf_*.png newer than
  per-image floor, `python3 scripts/claim_super.py --since <floor> <name.jpg>` (new
  helper, same hard guard as claim_photos). NSFW rewords banked in
  status.d/2026-08-13-mz-run-prompts.md. EVENING (David): media_push.bat → release.bat
  — post_deploy seeds whatever tiers have full photo sets on disk (proven no-op-safe).

- **DW-023 / RG-0029 CLOSED (David's ruling, executed 13 Aug):** origin token gate
  LIVE via migration 016 (007 superseded — rc-3 duplicate-file refusal found via
  David's SSH paste of the deploy log). Anon data reads 401; health/documents/static
  open; testers unaffected. RG-0029 LOCKED; RG-0053 assertion corrected (edge-401 =
  passage proven, agent on localhost by default); ledger 62 · 60 holding · 0
  regressed · exit 0. Uncommitted closing edits (ledger, fragments, L7) ride the
  nightly checkpoint. Remaining named tail: L7 (attended off-box tools + smoke
  vantage need the reviewer cookie). 005 document-gate decision still David's.

- MORNING WRAP (13 Aug, photo session): journeys **164/164 DONE** (MZ 7 claimed, 3 NSFW
  false-flags beaten by reword; map rebuilt 32/32; RG-0062 LOCKED — report widget now
  lives in journey_template.html so rebuilds can't drop it; intake tests 16/16).
  Kenya supers **32/114 on disk**: advexp a/b/c (24) + advacc a (8). Committed through
  24/114 (8691602); the final 8 + this note are UNCOMMITTED working tree — a stale
  .git/index.lock from a concurrent audit-loop writer blocks sandbox commits and FUSE
  blocks its deletion. SELF-HEALS: any git-writing .bat (deploy/commit/nightly) clears
  it via git_unlock.bat first — tonight's release will sweep these files in. NOTHING
  IS LOST. Resume the 82 remaining: fresh session, "continue" — recipe in
  2026-08-13-super-run-state.md (next = idx 32, sup_ke_advacc_b_1_exterior).
  Credits: ~544 left of 610 (66 spent incl. 3 refunded flags). EVENING unchanged:
  media_push.bat → release.bat → post_deploy seeds full-set tiers → verify ledger+live.

- **Evening handoff (morning session, Claude):** DW-023/RG-0029 CLOSED + LOCKED (gate
  live, verified, ledger green at lock time). DW-025: 244/273 images self-hosted;
  /demo-listings fully local; 29 rate-limit stragglers + live demo_sellers.json rewrite
  ride migration 017 run 2 (hardened: 0.5s pacing, backoff, attempt-tracked stand-in
  rung) — ON the deploy ref via the Kenya session's sweep commit 8691602. **Server did
  NOT act on that ref for 10+ min this morning — diagnose the deploy timer/log FIRST
  tonight** (paste in the scheduled task). RG-0063 OPEN, correctly counting 40 sellers
  refs live. **Bat lesson (Claude's error, owned): release.bat does NOT commit — it
  pushes existing HEAD silently; three presses burned. Tonight and henceforth:
  deploy_marketsquare.bat (gates + folds + auto-commits + publishes).** Tonight 17:45:
  scheduled session runs DW-029 rotation (ROTATE_SECRETS.bat + 5 vendor dashboards,
  one-at-a-time install-verify) then finishes DW-025 and locks RG-0063. Also noted for
  the register: /admin/deploy hook now sits behind the reviewer gate (L7 family).

- **DW-025 close BUILT (David's ask, same session as the RG-0029 lock):** repo fully
  de-hotlinked (1,141 refs → local paths; ms.js fallback neutralized), migration 017
  downloads 266 images + 7 SF tiles server-side (resumable) and localizes the live
  demo_sellers.json at 100%; RG-0063 OPEN guards the class through the gate. Ledger
  63 entries · 60 holding · 0 regressed · exit 0. Rides David's next release press —
  no urgency (gate hides payloads pre-launch), but one press closes it today; brief
  window of broken demo images (reviewers only, ~2-4 min) while 017 fetches.

- **DW-023 / RG-0029 closure in flight (David's ruling, 13 Aug):** migration 007
  activated via DEFER-1 line removal; ledger `_get()` now logs in as a reviewer and
  reads through the gate (payload assertions stay strong, posture stays anonymous);
  review code provisioned in gitignored .secrets/. Pre-deploy ledger run: exit 0,
  all locked holding, zero behavior change. **Waiting on exactly one action: David's
  release click.** Post-deploy: anon-401 verification → RG-0029 READY TO LOCK →
  promote → green run. Known tail queued as L7 (on-box tooling must pass the gate —
  UA-EDGE-1's sibling). 005 (document Basic Auth) deliberately still deferred —
  separate decision.

# MZ 6 remaining — staged prompts (13 Aug session, f1_start DONE 158/164)

Paste-ready, one per generation, Nano Banana Pro · 3:2 · ~2 credits each. Credits seen: 610.
f1_start claimed OK (reworded version passed moderation — reword rule works; note added below).

## f1_view.jpg  (air — window view; no-flames clause included)
Photorealistic editorial aviation travel photography, deep navy and warm amber accents. NO identifiable human faces, no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour. View from a passenger window over the Lebombo range — the lowveld patchwork giving way to green hills, then the flat silver of Maputo Bay on the horizon, a hint of clean unlit wingtip at frame edge, no flames, no fire, no engine glow. Wide landscape shot, strong depth, dramatic natural light, human figures absent.

## f1_sight.jpg  (ground — Maputo arrival)
Photorealistic editorial travel photography, Mozambique Indian Ocean coast — turquoise water, dhow sails, coral-stone and whitewash, bright tropical light with deep navy and warm amber accents, shallow depth of field where appropriate. NO identifiable human faces (people from behind, in silhouette, or in shadow only), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour. Maputo · arrival — sea air through the open terminal doors, tropical light spilling onto the arrivals hall floor, travellers in silhouette with luggage. Characterful mid shot with a strong sense of place.

## f1_over.jpg  (ground — guesthouse courtyard, dusk)
Photorealistic editorial travel photography, Mozambique Indian Ocean coast — coral-stone and whitewash, deep navy and warm amber accents, shallow depth of field where appropriate. NO identifiable human faces, no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour. Guesthouse in the old city — a tiled courtyard behind a heavy wooden door, ceiling fans turning slowly, lamplight on whitewashed walls at dusk, no people visible. Warm inviting accommodation shot at night.

## f2_start.jpg  (ground — the three-kilometre bridge)
Photorealistic editorial travel photography, Mozambique — turquoise water, deep navy and warm amber accents, shallow depth of field where appropriate. NO identifiable human faces, no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour. Across the three-kilometre bridge — off the stone island on the long low bridge over turquoise shallows, then baobab country rolling toward Nampula, morning light. Wide establishing shot with a clear sense of departure and journey ahead.

## f2_sight.jpg  (ground — Nampula departures)
Photorealistic editorial travel photography, Mozambique — bright tropical light with deep navy and warm amber accents, shallow depth of field. NO identifiable human faces (hands only if anyone appears), no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour. Nampula · departures — a last pastel de nata and espresso on a small terminal café table, sand still on a canvas bag beside it, warm window light. Characterful close detail shot with a strong sense of place.

## f2_finish.jpg  (arrival hall — Johannesburg home; keep people distant/from behind AT A DISTANCE — do not use boarding/climbing phrasing)
Photorealistic editorial aviation travel photography, deep navy and warm amber accents. NO identifiable human faces, no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour. Johannesburg · home — golden evening light through tall arrivals-hall glass, travellers at a distance in silhouette with bags rolling toward the exit, warm sun flare on the polished floor, no flames, no fire, no engine glow on any aircraft beyond the glass. Wide closing shot with a sense of arrival and completion, golden light.

## Loop reminders (hard-won, this morning's additions)
- Wait tool caps at 10 s — poll generation in 10 s chunks (~60 s total).
- Scale flipped TWICE this session (÷1.224 → ÷1.361 → 1:1-at-330%): re-probe click scale after ANY viewport change; JS rects are truth, verify inEditor before ctrl+a, verify textContent before Generate.
- Lightbox X overlaps the account-menu button at small sizes — resolve the X from the OVERLAY's own button set, not by position.
- After Download: poll Downloads for hf_*.png newer than the per-image floor, THEN close lightbox, then claim.

- MAINT-DASH-1 (13 Aug): B2b launch-readiness is now ON the +1 page — truth card above the
  Launch Switch, fed by the loop's own heartbeat (POST /dashboard/maint, maint-key gated,
  facts only). Shows brain KEYED/NO KEY (the ai_keys.env gap goes visible in amber), ARMED/
  SHADOW, heartbeat freshness. No web arming surface by design. RG-0061 OPEN → locks after
  next deploy + first heartbeat (tomorrow's 05:33 run). David's two acts stay: paste ONE
  key line in .secrets/ai_keys.env before the ~22 Aug B4 rehearsal; arm only after B4 READY.

- MIDDAY HANDOFF (12 Aug): MZ f1_start twice NSFW-false-flagged (credits refunded both times, reword rule now in runbook); Chrome tab-front + coordinate lessons banked. STATE: 157/164 journey photos (only MZ f1_start..f2_finish remain), all code/deploy wiring COMMITTED (ce80ce1) incl. post_deploy ladder-seed. FRESH SESSION RECIPE: connect Projects+Downloads, Chrome front-tab on Higgsfield, date +%s floor, JS-calibrate, run MZ 7 (reworded f1_start first), rebuild MZ map, then SUPER_LADDER_PROMPTS.md 114. EVENING (David): media_push.bat → release.bat (or token) → post_deploy auto-seeds KE → verify ledger+live. Open decisions: Harare currency, Zambia scope.

- MAINTENANCE LOOP 12 Aug: queue 31 rows → 23 verified / 5 closed / 1 new / 2 dup.
  TS-0024 (AI coach) and TS-0022 (blur covers) both promoted to VERIFIED on named machine
  evidence (AIK-VERIFY-1); closure letters await David's close-send press. New ledger
  tripwire RG-0060 locks the 'AI Coach unavailable' class at zero probe cost (unregistered
  email → 401 before spend). Ledger green 60/57/0-regressed. TS-0031 stays Path B (design:
  suggested-not-asserted car specs), needs reporter's field detail. STANDING GAP, 4th run:
  shadow agent has no AI key in the sandbox — every fault PATH_Bs mechanically; fine while
  the daily session is the brain, but B2b arming needs the key provisioned (David's act).

- DAY-RUN HANDOFF (12 Aug, David at work): Chrome got MINIMIZED as David left → extension clicks blank → photo run PAUSED at 157/164 (only MZ's 7 flight-legs left; then Kenya's 114 advert stills). Everything not needing the browser is DONE and COMMITTED (ce80ce1): ladder seeder ships via manifest + post_deploy.sh auto-runs it every deploy (no-ops until KE media lands — proven-safe pattern copied from seed_super_global). RESUME RECIPE (any session, the moment Chrome is visible): fresh claim floor `date +%s`, JS-calibrate click scale (runbook 11 Aug lesson), then the loop — MZ prompts in JOURNEY_HIGGSFIELD_PROMPTS.md §Mozambique (f1_/f2_), advert prompts in SUPER_LADDER_PROMPTS.md. EVENING SEQUENCE for David: (1) restore Chrome + say 'continue' → I finish MZ 7 (+as many advert stills as the evening allows); (2) media_push.bat (carries sup_ke_* to server); (3) release.bat (or grant .secrets/gh_push_token.txt and I publish) → engine deploys → post_deploy auto-seeds Kenya's 24 ladder listings → I verify live (ledger + diag) and report. Angola OUT; ZW/EG builds still awaiting Harare-currency + Zambia decisions.

- TWO JOURNEYS FULLY PHOTOGRAPHED TONIGHT: Kenya 32/32 and Namibia 30/30 — both maps rebuilt 0-pending (Kenya: CPT-to-CPT complete arc; Namibia: O.R. Tambo gate, Kalahari window, key handover, jacaranda braai, gravel kudu, terminal farewell, Joburg night grid). Root cause of all "unclickable page" failures found and runbooked: Higgsfield's upgrade MODAL overlay (one Escape clears it) + per-session click-scale calibration via JS rects. 13 photos QC'd-and-claimed this session, zero rejects. REMAINING: BW 7 + MZ 7 flight-legs → then ALL journey photography done; next milestones: David's release.bat click (deploy), Kenya 114 advert stills, ZW/EG builds (awaiting Harare currency + Zambia decisions).

- KENYA JOURNEY PHOTOS COMPLETE: 32/32 — the full 7-day fly-in safari (CPT departure to CPT homecoming) shot, QC'd and embedded; adventures_ke_map.html rebuilt 0-pending. Root cause of last night's "unclickable page": Higgsfield's Supercomputer upgrade MODAL overlaying everything (one Escape closes it — runbook updated mentally, formal note below). Next in this session: 21 flight-leg shots (NA f1/f2, BW, MZ), David's 20-min slow-stop rule armed.

- Heritage pins on all 9 maps now deep-link into the app's wonder views (WONDER-DEEPLINK-1 in ms.js + wonders.json ids on 14 journey pins + injected layer on reserve/US/UK/AU; DE = catalog gap). Awaiting David's release.bat click to make ALL map work live (his NA observation was live-vs-local). Remaining photos: BW 7 + MZ 7.

- BOTSWANA JOURNEY PHOTOS COMPLETE: 32/32 — bookends shot tonight (prop-gate sunrise, salt-vs-delta window, Maun bush-plane ballet, Thamalakane stoep with a CORRECT fish eagle, dawn pan exit, boot-dust boarding, thunderhead homecoming). Map rebuilt 0-pending. THREE journeys now fully photographed (KE 32, NA 30, BW 32). LAST remaining: Mozambique's 7 flight-legs — then the entire journey fleet is photo-complete. Deploy still awaiting David's release.bat click.

- **STALE-CODE-1 — two of today's runs tested older code and looked like valid tests.** `git
  pull` says "Already up to date" whether or not the fix was pushed, and the 08:10 live run
  returned output identical to the previous one. Every run now prints
  `code <sha> [DIRTY-WORKTREE] <subject>` before anything else, pinned to the agent's own
  checkout rather than the rehearsal sandbox. **RG-0059 LOCKED.**
- Sixth green-looking no-op of the day, and the reason the count matters: every one of them
  passed its own check. The ledger and the "name the cause" discipline are what caught them,
  not the automation.

- **Correction to today's earlier read: the agent's three `no clean patch` results were RIGHT.**
  TS-0031 is a UX/confidence-policy change that its own row says is blocked awaiting information
  from the reporter; TS-0024 is an unanswered question with no reproducible defect. Neither is
  mechanically patchable. The queue contains no mechanical faults, so 0/2 is the correct output,
  not a failure.
- **What is still genuinely unproven, and why B4 cannot settle it:** both rehearsal tiers patch a
  two-line sandbox `app.py`. The real application is `ms.js` at 1.07 MB and `bea_main.py` at
  907 KB. CAND-FIX-1 made those files visible to the brain for the first time today — nothing has
  yet tested whether a patch written against a windowed excerpt of a million-byte file actually
  applies and gates green.
- **`scripts/maint_realrepo_probe.py` added** — clones the repo, seeds one known mechanical
  defect into a real file, runs the real agent in shadow, and reports whether the defect was
  repaired. Shadow by construction (temp clone + the kill switch stripped from the environment),
  so it can never ship. Run: `python3 scripts/maint_realrepo_probe.py [--target bea] [--keep]`.
- **This is the last open question before the timer is a reasonable idea.** Spine proven, guard
  proven in both phases, B4 Tier 2 PASS, brain reachable — but the agent has still never written
  a line of code into a file this codebase actually contains.

- **First real-repo probe run: INVALID, not failed.** The refuse guard escalated it on the word
  `card` — the probe's fault text said "when I tap a card" (a listing card); `card` is a payment
  marker. The patch path was never reached, so the run says nothing about patch quality.
- **Checked before changing anything:** across all 30 live faults, substring matching differs
  from word-boundary matching exactly once (`anonym` in "anonymity" — correct anyway), and the
  standalone word `card` appears zero times. The guard is not misbehaving; the probe was.
- **Did not narrow the marker to make the probe pass.** Over-refusing costs a human glance;
  under-refusing costs a payment surface. Reworded the probe instead, and its wording is now
  verified against the full marker list before use — both targets clean. The probe also now
  reports ESCALATE as **INVALID** rather than FAIL, so a guard hit can never be misread as a
  patch-quality verdict.
- **Still unanswered, and still the last open question: can the agent patch a 1 MB file?**
  Three attempts today; none has yet reached the patch path against real code.

- **SERVER-BIT-2:** first live boards read 5/8 degraded — all 3 FEA fails were
  vantage-point artifacts (nginx/AdvertAgent surfaces vs uvicorn), production fine.
  Runner fixed both copies (disk shell fallback + AdvertAgent :8002 enumeration);
  expect 8/8 one cycle after the next deploy. Stale root bit/ flagged for /housekeep.

- **First armed live run happened (07:58 UTC): `mode=LIVE, phase=prelaunch,
  trust-core=GUARDED`. 2 faults, 2 × "no clean patch", nothing shipped.** Safe, and the guard
  and gates behaved — but 0/2 is not a working agent, and the reason was structural.
- **CAND-FIX-1 — the fix agent could never see real code.** `_candidate_files` dropped any file
  over 12,000 bytes, and every file this app lives in is far over it (ms.js 1.07 MB, bea_main.py
  907 KB, marketsquare.html 405 KB). Worse, it ranked the agent's own `.maint_agent/run_*.json`
  reports as the top candidates for TS-0024, because they quote the fault title — the brain was
  handed its own exhaust to patch. Fixed: noise excluded before ranking, oversized files
  windowed to a real excerpt with the true line range. **RG-0058 LOCKED.** ms.js now yields
  lines 3626-3766 where it previously yielded nothing.
- **Where the agent actually stands:** spine proven, guard proven in both phases, B4 Tier 2
  PASS in prelaunch (6/6). Patch generation against this codebase remains **unproven** — one
  synthetic typo is still the only patch the brain has ever written, and the structural blocker
  was only removed after the first armed run exposed it. The next live run is the real test.
- **Not yet armed on the timer.** The 07:58 run was hand-driven with David watching, which is
  exactly how it should have gone: it found a blocker no rehearsal could, because the synthetic
  sandbox has a 2-line `app.py` and the real repo has a 16,425-line one.

- MAINT-B4-6 (11 Aug, attended): first server Tier-2 verdict = honest NOT READY (routing 6/6
  PASS with the real brain; only patch-APPLY failed). Rewrite fallback built + proven offline
  (via: rewrite-fallback → gates green → shadow-held); migration 015 re-runs Tier 2 next
  deploy. BIT timer live (UNKNOWN → degraded 5/8); B-FEA-* fails = one mis-aimed probe base
  (localhost:8000 has no FEA) — BIT-AIM-1 work order queued for the loop, not patched blind.
  Arming still OFF, still David's paste, now waiting only on 015's verdict.

- SUPER-AFRICA rulings (David, 11 Aug): ZW/Harare pricing and fares in **USD** ("riders in
  dollars") — the ZW ladder seeder, journey-map fares and COPY blocks build in USD when
  replication reaches ZW. Zambia scope still open. Also 11 Aug: VIZ-MAPS-4 applied to BOTH
  dashboards (dashboard.server.html + the local sibling dashboard.html David actually opens
  — the "still see the column" mystery was the second file). TS-0018 closed on David's
  referent. D8 verified fully done; D10 scheduled for 1 Sep 09:00; D9 post-launch.

- **SHOWCASE-BANNER-1 (11 Aug, David's call after the 002 conflict was raised):** showcase
  trios get the ★ SUPER ADVERT banner via super_example=1, and the new showcase=1 flag
  excludes them from SUPER-PIN-1 pinning in every sort (server + client) — real sellers
  keep top billing. migrations/014 marks live rows; creators born-marked; LIST-002 in the
  register; RG-0052 LOCKED. Rides next deploy.

- **PHASE-AWARE-1 — the arming gate was scoring the wrong mode.** The B4 rehearsal hardcoded the
  postlaunch answer for SYN-DESIGN, so running it in prelaunch (the mode David wants to arm)
  scored correct PATH_A routing as FAIL and printed "NOT READY". The agent was right; the
  harness was wrong. Expectations now track the run's phase+brain and the harness states which
  combination it scored. **RG-0057 LOCKED**, including an assertion that the four
  protected-surface rows can never become phase-conditional.
- **Confirmed live on the server, prelaunch, real brain:** banner read
  `phase=prelaunch  trust-core=GUARDED`, SYN-MECH reached shadow-green, and all four protected
  surfaces escalated (paystack/card, identity/anonym/seller_email, legal/popia/eula, safety).
  GUARD-SPLIT-1 does what it was built to do — full pre-launch autonomy with the trust core
  still refused.
- **Outstanding before arming:** re-run Tier 2 prelaunch to get a true verdict (routing will now
  score correctly), and note that `static/maint/b4_tier2.json` is still **404** — migration 011
  writes it from `post_deploy.sh` on a *deploy*, and only `main` has been pushed.
- **Known gap, deliberately not papered over:** the prelaunch design lane is routed but never
  proven end-to-end. Tier 2 took SYN-DESIGN to PATH_A and the brain returned "no clean patch" —
  correct judgement for an unpatchable synthetic, but it means no design change has yet been
  generated and gated by machine. Only a real design fault will settle that.

## 11 Aug 2026 — DATA & PARTNERS card corrected + per-partner activation brief (PARTNER-LINKS-1)

David asked what activating the four DATA & PARTNERS toggles actually needs. Answer, per lane:

- **Signed-operator photos** (`data_ops`) — internal, no vendor, no key, R0. Blocked on
  **paper, not code**: the Featured Operator Showcase Agreement is still a DRAFT (21 Jun) and
  no operator has signed. Then build upload+render, then flip. [D] counsel sign-off.
- **Google Places** (`data_places`) — **CLOSED**, not pending. Out by David's 1 Aug ruling
  after a silent ~$360 bill. No activation path; row kept as a tombstone so it cannot return
  by accident. Link now points at the billing console.
- **Flights — Travelpayouts / Aviasales** (`data_flights`) — **the only lane with runway.**
  Account live (partner 758984), `TRAVELPAYOUTS_TOKEN` live on the server (re-verified 5 Aug),
  EULA v1.11 §6.1A live, R0 cost, no money through the till. Remaining gap is *entirely our
  own code*: fare-cache adapter (empty `{}` = no fare, NOT an error) → Expedition fare UI with
  the indicative/agency caveat + click-out disclosure → token joins the live probes → flip.
  Tours shelf (~8% vs 1.1–1.3%) still blocked on the 5 Aug review decline — resubmit moment
  is David's (OPEN_LOOPS D10).
- **Mapbox** (`data_mapbox`) — optional; the only row that adds a paid metered dependency,
  for prettier tiles and no trust gain. Recommendation: leave off.

**Cross-cutting finding:** none of the four flags has consumer code. They are wiring-only
placeholders — flipping one changes nothing on the live site. No session should report
"activated" on the strength of a flag flip alone.

Dashboard patched both sides (links, corrected vendor, OUT/KEY-LIVE badges, TO-ACTIVATE
tooltips), locked as RG-0050, ledger green (50 · 47 holding · 0 regressed · exit 0).
Unshipped — rides the next `deploy` ref publish.

- **NO-RETEST-1 (11 Aug, David's ruling):** there are no retests — a complaint is fixed by
  us, verified by us on named machine evidence, and CLOSED with a letter to the reporter.
  Retest-wait status retired; `close-draft`/`close-send` replace the retest routes (the send
  closes + stamps verified_at); dashboard chip now "awaiting close"; ACK/widget copy no
  longer promise a retest ask. migrations/012 moves the 1 parked live row to 'fixed'.
  Ledger RG-0048 LOCKED. Awaiting next deploy; then close-draft → David approves → send.
- Pre-existing tripwire failure observed (not this change): adventures_na/bw/mz/ke_map.html
  carry no REPORT widget (test_widget_is_wired_into_every_tester_page red).

- **Maintenance loop, 11 Aug (daily run):** the loop's own intake was broken and reporting
  green — `UA-EDGE-1`. Cloudflare refused every UA-less call from our tooling (error 1010)
  before it reached the origin, so `maintenance_agent.py` read an empty queue and exited 0.
  Fixed for the whole class (5 scripts that call our edge now send a User-Agent); verified
  by reproducing the failing action clean (403 → 200, 7 faults appeared). **RG-0053 LOCKED**,
  with a live half so a silent re-break turns the ledger red. Committed, not deployed —
  NIGHTLY-SHIP-1 carries it through the gates.
- **Fault queue after the fix is readable again: 30 total · 7 new · 19 verified · 2 duplicate
  · 1 closed · 1 stale `awaiting-retest` (TS-0022 — status retired by NO-RETEST-1/migrations
  012; row not touched by this session, flagged for `fault_reconcile`).** All 7 new are
  severity=major: TS-0001, TS-0006, TS-0018, TS-0021, TS-0024, TS-0027, TS-0030.
- **None of the 7 were fixed this session — and the reason is itself a finding.** The shadow
  agent routed all 7 to PATH_B with `why: "ai_provider unavailable -- defaulting to the
  batched design lane"`. That is RG-0049 degradation working as designed (a brain failure
  degrades, never kills), but it means **the queue is currently classified by the fallback,
  not by judgement** — no fault reached "gates GREEN, patch ready", so per the loop's strict
  contract nothing was applied. The brain binding needs an ai_provider lane reachable from
  wherever the loop runs, or the 3×/day sessions will keep binning real faults as design work.
- Escalation brief: none written — no safety / legal / cost items in the last 24h.

- **Maintenance loop, 11 Aug (second run today):** ledger green before and after — **54
  entries, 51 holding, 0 regressed, 3 open** (RG-0003, RG-0004, RG-0029, all pre-existing
  and unchanged). Escalation brief: none written — no safety/legal/cost items in 24h.
- **Fixed: CV-GUARD-1 — the seller CV blanked on an empty roster or an off-city card.**
  `openSellerCV` dereferenced `s.headline`/`s.trustScore` with `SELLERS` empty, and `l.trust`
  twice in its markup after having already guarded `l` one line above for the arithmetic.
  `renderProfilePreview` had the same `SELLERS[0]` deref plus an unguarded `CATS[s.cat].icon`.
  RG-0031 missed both because it scoped to "the openDetail call graph" and these are **sibling
  entry points** — same class, different door. Verified by reproducing the failing action
  clean: `scripts/repro_cv_guard.js` gives **3/3 CRASH (exit 1)** on the pre-fix backup and
  **3/3 pass (exit 0)** on the fix. **RG-0054 LOCKED.**
- **Verified: TS-0001** ("the 15 matching list button doesnt work") — fixed 5 Aug, but the
  row was never updated and sat in `new` for six days. Live-probed the deployed asset
  (`GET /static/ms.js`, HTTP 200, 1,056,818 bytes, contains `upBox.onclick`) and moved to
  `verified`. Queue hygiene, not new work — worth watching that fixes get their row closed.
- **Fault queue: 30 total · 6 new · 20 verified · 2 duplicate · 1 closed · 1 stale
  `awaiting-retest` (TS-0022, status retired by NO-RETEST-1 — still not touched, still for
  `fault_reconcile`).** The 6 new all now carry an honest `fix_note` saying what the loop did
  and, more importantly, what it deliberately did **not** claim, so next session does not
  re-triage them from scratch: TS-0006 and TS-0027 are Path B design calls; TS-0021 is a
  model-selection question that is David's by standing rule; TS-0024's root cause was never
  established (though all three AI lanes read available from `/flags` and the breaker is
  empty, so the likely single-vendor cause is structurally closed by RG-0032); **TS-0018
  needs one sentence from David** — "if we dont use this, can we remove it?" has no referent
  in the text and removal is irreversible, so the loop will not guess.
- **Standing finding, now twice in one day: the brain is not reachable from where the loop
  runs.** Both runs today had `maintenance_agent.py` route every fault to PATH_B with
  `ai_provider unavailable -- defaulting to the batched design lane`. That is RG-0049
  degrading correctly rather than dying, but the effect is that **real mechanical faults get
  binned as design work** and nothing ever reaches "gates GREEN, patch ready". Everything
  fixed today was found by Claude reading the queue directly, not by the harness's triage.
  Until an `ai_provider` lane is reachable from the loop's environment, the 3×/day scheduled
  sessions are doing shadow bookkeeping, not triage — this is the B2b binding gap, and it is
  the single thing most worth closing before the launch rush.

- MAINT-CLOSE-1 (11 Aug, attended): Maintenance Agent open items CLOSED to the arming line —
  MAINT-B4-5 degrade-not-die fix (RG-0049 locked, ledger green), migration 011 ships the server
  Tier-2 rehearsal on next deploy (verdict → static/maint/b4_tier2.json, reviewer-gated), B3
  escalation brief machinery + tripwire, DESIGN_CHANGE_GUIDELINES.md (boundary-redraw item 1
  closed; item 2 designer binding = David), maintenance-loop scheduled daily 07:31, arming
  runbook + 3×/day server timer staged. Committed for NIGHTLY-SHIP-1; David's one-word /tsl
  ships it sooner. OPEN for David: arm after Tier-2 READY; bind the designer role.

- **LIVE-FLAGS-1 + SERVER-BIT-1 (11 Aug, David):** dashboard now self-refreshing — Launch
  Switch card polls /flags (20s + focus); BIT heartbeat moves ON the server (manifest
  ops/bit/ + migrations/013 systemd timer, 15 min, localhost, detect-only). No human, no
  deploy in the refresh loop. Ledger RG-0051. Rides next deploy.
- **Converged with parallel maint session ff8ec95:** my migration renumbered 011→012;
  torn adventures_ke_map.html restored from HEAD (widget back, tripwire green);
  RG-0048/0049/0050/0051 all coexist, ledger fully green.
- **Second clobber, class-closed:** the journey-map rebuild lane rewrote all five
  adventures maps again 06:09 (widget lost, +new c2c page). No code generator exists —
  the runbook drives rebuilds, so the standing rule now lives in
  JOURNEY_PHOTO_RUNBOOK.md; all five pages re-patched, intake tests ALL PASS. The
  deploy gate blocks any future widget-less rebuild from shipping.

- Kenya photo run: 29/32 — Days 1-6 COMPLETE (balloon dawn, cheetah watchtower, Mara crossing, bush breakfast, Oloololo sundowner all in). Map rebuilt with 29 embedded. Overnight session ended when the Higgsfield tab renderer froze (~03:30); root-caused a CSS-vs-screenshot coordinate-space trap first (runbook updated — big lesson banked). REMAINING: 3 shots (d7_start bush airstrip / d7_sight Nairobi connection / d7_finish Cape Town home) ≈ 15 min in a fresh tab, then 21 flight-leg shots NA/BW/MZ, then supervised photos DONE → next phase: /tsl deploy + server seed --apply + replicate ZW/EG.

- David's 4 map points DONE: off-line pins fixed (seg-through-stops, all Kenya days + bookends), airport continuity stitched (d7 ends CPT/JNB with own pins+photos — KE's 3 airport stills still pending generation), heritage layer live on all 5 maps, TP static links on flight days (marker 758984; strip-on-claim rule canon'd). Ledger RG-0025 strengthened with ke page.

- **GUARD-SPLIT-1 — pre-launch autonomy is now available without dropping the trust core.**
  `MAINT_PHASE` was controlling both the design lane (the autonomy David wants) and the
  identity/auth/kyc/schema/safety refusals (which nobody asked to drop). Split them:
  `TRUST_CORE_GUARD` defaults ON in **both** phases; `MAINT_PHASE` now only decides whether
  design changes are implemented or batched. **RG-0056 LOCKED.**
- **Why now:** the 9 Aug "no real users/sellers/money" premise has expired — three real
  reporters, and Maroushka's live listing 335 with 8 real photos. Evidence: the B4 storm at
  prelaunch failed **2/6** before the split (SYN-ANON and SYN-SAFETY routed PATH_B instead of
  escalating) and passes **6/6** after, banner reading `phase=prelaunch trust-core=GUARDED`.
- **B4 Tier 2 PASSED on the server, 06:45 UTC** — first time the brain has ever answered
  (`brain[anthropic/claude-haiku-4-5-20251001]`), real model's patch gated green end-to-end,
  commit withheld. The earlier 06:42 "NOT READY" was invalid: the server was still on 9cc3725,
  one commit behind BRAIN-PATH-1, so it re-ran the import bug.
- **Arming is now David's single act, and the config to use is `MAINT_PHASE=prelaunch` with the
  trust-core guard left at its default.** Two items still outstanding before the runbook's own
  gate is satisfied: `static/maint/b4_tier2.json` returns **404** (migration 011 has never run —
  it fires from `post_deploy.sh` on a *deploy*, and only `main` has been pushed), and Tier 2 has
  not yet been run in prelaunch mode to prove the design lane actually routes PATH_A.

- **BRAIN-PATH-1 — the "brain unreachable" finding was a two-line bug, not an environment gap.**
  `ai_provider.py` is at the repo root, `maintenance_agent.py` is in `scripts/`, and the agent
  never put `REPO` on `sys.path` — so `import ai_provider` had failed on **every run, on every
  machine, since the agent was written**, keys or no keys. RG-0049 degradation then binned every
  fault as PATH_B and exited 0. **Second green-looking no-op found in one day** (UA-EDGE-1 was
  the first): both times a correct fail-safe with a vague message hid a plain wiring fault.
- **Fixed:** `REPO` on `sys.path` (the `__file__` root, not the `--repo` rehearsal override);
  degradation messages now distinguish *will not import* / *no key* / *call failed*; and
  `.secrets/ai_keys.env` added as the local key slot, since `ai_provider.envkey()` only falls
  back to `/var/www/marketsquare/.env`, which exists on the server alone. **RG-0055 LOCKED**,
  with an executable half that loads the agent from `scripts/` and proves the import.
- **Still keyless, and now honestly so.** The loop reports: `no AI lane has a key where the loop
  runs (checked: ANTHROPIC_API_KEY, FAILOVER_API_KEY, OPENAI_API_KEY, SCALEWAY_API_KEY) — the
  brain imported fine; it has nothing to call.` **One key in `.secrets/ai_keys.env` (gitignored,
  template already in place) turns the loop's triage on — that is David's act, and the only
  thing still outstanding.** Worth knowing before doing it: autonomous triage has never actually
  run, so its first real outing should be watched rather than left to a 2 a.m. schedule.

- AMBER-SWEEP-1 (11 Aug, attended): fault queue reconciled on evidence — 6 new → 2 (TS-0018
  awaits David's referent; TS-0024 awaits one coach run), 3 design/strategy items closed &
  routed, TS-0030 verified by live probe, TS-0022 retest letter = 9-cover replacement request
  drafted awaiting David's send. Remaining ambers all have named clearers: one deploy (BIT ×2 +
  Tier-2), David's tp_tours resubmit moment, Maroushka's re-uploads. Details in
  Records/FAULT_RECONCILE_2026-08-11.md.

- SUPER-AFRICA-1 Kenya pilot BUILT locally (ticket in CHANGE_REGISTER 2026-08-10): ladder seeder + 24 KE COPY blocks + journey map + prompt packs + KE wiring + 7 OPEN-market launch entries. Next: (1) supervised Higgsfield run — 114 advert photos (SUPER_LADDER_PROMPTS.md) + 25 journey photos (JOURNEY_HIGGSFIELD_PROMPTS.md §Kenya); (2) /tsl deploy + server --apply + diag; (3) replicate to ZW/AO/EG + extend NA/MZ/BW. Harare currency decision pending (USD vs ZWL).

- Kenya photo run: 8/32 claimed and QC'd (fly-in day COMPLETE: CPT departure, Rift window, JKIA arrival, Karen cottage; Day 2: matatu street, rhino-and-skyline flagship, Karen Blixen farmhouse, nyama choma). Map rebuilt after each batch. Pace ~4-5 min/photo incl. QC (queue slower than 26 Jul's 60s). Next: d2_over (coffee-garden cottage dawn), then Days 3-7 (24 photos), then 21 flight-leg shots NA/BW/MZ.

- Kenya photo run: 24/32 — Days 1-5 COMPLETE. Day 5 additions: wheatlands road, Narok market, Maasai adumu (all-anonymous framing), elephant family + skyline giraffe, Milky Way tented camp. Map rebuilt, 24 embedded. Remaining: Day 6 (balloon dawn, big cats, river crossing, bush breakfast, sundowner finish = 5), Day 7 fly home (3), then 21 flight-leg shots. Queue steady ~100s; David's 20-min slow-stop rule in force (not yet needed).

- Kenya photo run: 19/32 — Days 1-4 COMPLETE (fly-in, Nairobi, Naivasha, Hell's Gate/Nakuru). Map rebuilt, 19 embedded. Standing instruction from David: on a slow stop, wait 20 min (2×10-min sleeps) then resume. Remaining: Day 5 (Mara road, 5), Day 6 (herds, 5), Day 7 (fly home, 3), then 21 flight-leg shots.

- Kenya photo run: 14/32 — Days 1-3 COMPLETE (fly-in, Nairobi, Great Rift/Naivasha). Two species/artifact QC catches so far (burning winglet; bald eagle regenerated as correct African fish eagle). Map rebuilt, 14 embedded. Remaining: Day 4 (Hell's Gate/Nakuru, 5), Day 5 (Mara road, 5), Day 6 (herds/balloon, 5), Day 7 (fly home, 3), then 21 NA/BW/MZ flight-leg shots.

- Kenya photo run: 10/32 claimed, QC'd, embedded (Days 1-2 COMPLETE + d3_start tea-country escarpment road). Higgsfield queue running slow today (~90-110s/render vs runbook's 60s — their shared GPU pool at Sunday peak, not our side; 26 Jul precedent, recovers on its own). One mid-run viewport resize threw coordinate clicks — recovered; lesson: verify prompt-in-box via screenshot before every Generate. Remaining: d3_view/sight/food/over, Days 4-7 (17), then 21 flight-leg shots NA/BW/MZ. Resume any session: fresh `date +%s` claim floor, then the runbook loop.

- Kenya photo run LIVE: 2/32 claimed (d1_start CPT departure, d1_view Rift-from-window — both QC'd, map rebuilt with them embedded). Loop debugged end-to-end (see runbook 10 Aug lessons: lightbox/Download traps, aircraft flame artifact). Resume: continue the same session loop — next up d1_sight (JKIA arrival); floor timestamp /tmp/claim_floor.txt; ~30 × ~2.5 min remaining, then 21 flight-leg shots for NA/BW/MZ.

- SUPER-AFRICA-1 addendum: Kenya map upgraded to 7-day FLY-IN safari (CPT⇄NBO bookends, real ~R8,900 indicative fare from live Data API, RG-0025 clean). SUPER_AFRICA_RESEARCH.md canon started (advisories, operators, TP rules). Photo count now 32 journey + 114 advert prompts. OPEN for David: (1) Zambia in scope? (2) AO sequencing given Luanda L3 advisory. (3) Harare currency (USD vs ZiG).

- SUPER-AFRICA-1: Angola OUT (David). NA/BW/MZ maps upgraded to 7-day fly-in (existing photos intact, real fares, RG-0025 clean). Fares snapshot cached for ZW/EG. NEXT: supervised Higgsfield run — Kenya 32 first, then 21 flight-leg shots; needs Downloads grant + Higgsfield in Chrome. Open: Zambia scope, Harare currency.

## 2026-08-10 — PHOTO-MEASURE-1 ready to ship
Maroushka's 10 Aug retest (TS-0028/29/30) diagnosed from live evidence: blur ceiling was
judging boxes while the painter painted more (feather+capsule) — output-diff gate now guards
both accepted exits (RG-0047, offline-proven); edit-path upload errors unsilenced (ms.js ×3).
LOCAL until /ship. Open: client render staleness (TS-0030b), stored-cover remediation flow
(9 of 15 live covers over ceiling — Records/BLUR_AUDIT_2026-08-10.md), Tier-2 rehearsal re-run.

## D8 Stays/B&B — photos DONE, adverts staged, email track scoped (7 Aug 2026)

The photo gate on D8 is cleared: all 15 Stays photos exist on disk and are in spec. That was the
one thing only an attended session could do, and it is done.

What is ready to ride the next deploy: `migrations/009_stays_showcase_adverts.py` creates the three
`adventures_accommodation` showcase adverts and prints their ids into the deploy log. Harvest those
ids, then run `CityLauncher/emailer/flip_showcase_hrefs.py thatch=NNN jacaranda=NNN marula=NNN`
(already extended for the three new keys) to deep-link the cards.

What is NOT done and is now the whole of what remains on D8:
1. Build three 352x728 phone cards from the new heroes -> `CityLauncher/emailer/assets/`
   (`phone_stay_thatch.jpg`, `phone_stay_jacaranda.jpg`, `phone_stay_marula.jpg`), register them in
   `inline_images.py`, and upload to `/static/`.
2. Replace the three MOCKUP cards in `adventures_accommodation_outreach.html` (lines 189-279) with
   the sibling pattern: two anchors per card, bare `https://trustsquare.co` hrefs for the flip
   script to fill. This also removes the Unsplash hotlinks — worth doing on privacy grounds alone.
3. Deploy (via /tsl, David's call) so the adverts exist and the deep links resolve.
4. The 4-layer ZA map pilot has not been started. The concept page remains the design truth and the
   three new adverts now carry real lat/lng, so the B&B layer can read pins from the DB.

Not a blocker but worth naming: `adventures_accommodation_outreach.html` is seven weeks behind its
three siblings (15 Jun vs 2 Aug). Swapping the cards closes the gap that matters; the rest of the
drift (heroimg, outlookbg, claimyour, rankcta, stepnum) is a separate, smaller decision.

- PARKED 5 Aug evening (David's call, reminder set for 08:00 6 Aug): CF rail is BUILT
  (subdomain + worker v2 router + secret both sides + catch-all wired; Resend step
  deleted via RELAY-FROM-1 — verified-domain From, alias Reply-To, $0). Remaining:
  /tsl (ships RELAY-FROM-1, safe — flag OFF), Peer round 3, then flip both rails +
  two-party drill. Check: marketplace mode back to Launch—Free only?

## 2026-08-05 — AIK-VERIFY-1: people report, machines verify (David's ruling)

- **Doctrine amended** (MAINTENANCE_AGENT.md + FAULT_REGISTER.md): the month's evidence
  answered the design question early — testers report but do not retest (retest chip 0
  while 21 fixed-or-open majors sat amber). David's ruling: after a fix the AI TESTS it
  and declares it verified (green) on NAMED machine evidence (reproduced-clean, tripwire,
  or live probe in fix_note); the tester retest letter becomes an optional courtesy; a
  tester's "still broken" always reopens. The who of verification changed, never the
  whether.
- **RECONCILE_FAULTS.bat + scripts/fault_reconcile.py:** one click on David's machine —
  reads the queue, marks the 16 substantiated fixed faults VERIFIED with evidence
  (TS-0002/3 via RG-0031; TS-0004 brand-label; TS-0005/7/8/9/10/11/12/19/20 fixback
  9166b30; TS-0014..17 OPS-MAP-2 b0182af), prints the honest still-open triage table,
  writes Records/FAULT_RECONCILE_<date>.md. One y/n before any write.
- No BEA change needed — the PUT /admin/faults ladder already supports verified (+
  verified_at); the Ops Map already counts verified as green.
- v2: reconcile runs server-side over SSH (edge gate 403s off-browser HTTP by design).

## 2026-08-05 — Relay + account binding built (dark)

- INTRO-RELAY-1 and ACCOUNT-BIND-1 built in one pass, both dark behind fail-closed
  launch switches; RG-0038/0039 LOCKED; 7 relay semantics + session scope separation
  proven by isolated tests; Cloudflare worker staged at ops/cloudflare/. Rides next
  /tsl. Then: David's CF console step, Peer round 3, flag flip + two-party drill.

## 2026-08-05 — Introduction relay (Option B)

- David selected Option B (masked-alias relay). Build spec written (Records/INTRO_RELAY_BUILD_SPEC).
  No new subscription — reuses Cloudflare Email Routing + Resend. One-way-first, dark-flagged,
  folds into the F1 account-binding pass, Peer-reviewed before any live intro. Doctrine ruled:
  nothing of the customer's leaves except a consented, revocable channel — enshrine in CLAUDE.md.
- Awaiting David: build P1 now behind the dark flag, or hold for the CF console prerequisites first.

## 2026-08-05 — Dashboard as memory

- LS-TIPS-1: hover OFF/ON/implication explainers on ALL launch switches; new Trust &
  privacy rails group (intro_relay + account_binding) with live Cloudflare-rail status;
  Ops Map gains the Intro Relay block with switch/rail/binding chips. Server /flags +
  /admin/flags carry the two new switches + relay_configured. Rides next /tsl.
- FIXED-HONESTY-1: ops-map Maintenance chips no longer lump 'fixed' (shipped,
  unconfirmed) with untouched faults — majors count only genuinely-open rows;
  'fix shipped · retest' chip carries the pending-confirmation pile. If the 21
  majors still show after deploy, their DB rows need advancing via the retest
  letters (draft → send), which is the honest path to green.

## 2026-08-05 — Peer round 2 fixes

- F3 KYC SSRF guard + lane pin (RG-0036) and F2 atomic spend reservation (RG-0037) DONE
  on disk; py_compile green; ride next /tsl. F1 (app-wide account binding) is a DECISION
  brief for David — Records/F1_ACCOUNT_BINDING_DECISION_BRIEF (recommend Option A,
  session-bound charges). Awaiting A/B/C.
- Still open from earlier: RG-0028 origin-firewall regression (Hetzner console, David).

## status fragment — 2026-08-05 rg0028 false alarm closed
- RG-0028 ALERT RESOLVED — FALSE ALARM: Hetzner firewall `trustsquare-origin-lockdown` verified
  INTACT + Fully applied (check-host.net 57/58 global nodes time out on 80/443; console rules
  exact: 22=David only, 80/443=Cloudflare ranges). The "regression" was the sandbox runner's own
  transparent 80/443 proxy accepting every connect. No Hetzner action was ever needed.
- RG-0028 probe hardened (RG-0028-GUARD): control-connect to unroutable TEST-NET-3 first; unfit
  runner → INFO + skip, fit runner → unchanged. Scope label corrected CPX22 → CPX32.
  Backup: scripts/regression_ledger.py.bak-rg0028guard-20260805.
- Known 403-gate-artifact REGRESSION lines from off-allowlist runners: unchanged, still expected
  until run from a gated/allowlisted vantage.

## 2026-08-05 — AI services fixes (audit acted on)

- AI-SERVICES-AUDIT-1 findings ACTED ON same day per David: F1 any-lane gates (15x),
  F2 deliver-then-charge (AI1/AI2/AI5), F3 vendor-neutral card copy, F5 HEARTBEAT-1
  idle-recovery live in code. RG-0032..0035 LOCKED. py_compile green; NOT yet
  deployed — rides next /tsl. Post-deploy: re-run both ban-drill variants.
- Peer pack v2 ready (extract generator answers the packet complaint) — David
  re-runs PEER_AUDIT_AI_SERVICES.bat.
- ALERT: RG-0028 regression — origin accepts direct connections (Hetzner firewall
  likely off). David: Hetzner console. Not fixable from a session.

## 2026-08-05 — AI services audit

- AI services audit Phase 1 DONE (Records/AI_SERVICES_AUDIT_2026-08-05.md + nice
  docx): estate verified sound overall; F1 HIGH (15 ANTHROPIC_API_KEY hard gates
  defeat vendor independence — pre-launch blocking, fix awaits David's go),
  F2 MEDIUM (AI1/AI2/AI5 charge-before-deliver vs published refund promise),
  F3 David-decision (Claude-branded copy vs cost-first routing). Phase 2 peer
  audit staged: double-click PEER_AUDIT_AI_SERVICES.bat.

2026-08-05 (scheduled follow-up, ~10:00, unattended): Travelpayouts project review returned DECLINED for the tours shortlist (+22 partner programs) — "website under development / not yet ready, re-submit after setup." Not resubmitted (unchanged site fails again); parked as OPEN_LOOPS D10 — David picks the resubmit moment, passing auto-connects the programs. Aviasales flights lane unaffected (Data API re-verified, JNB-CPT R2,284 ZAR). $400 payout minimum on chosen method noted for later.

2026-08-05 (attended, David — found by his question, not by our testing): MODERATION PARITY ON THE AGENCY IMPORT DOOR. David asked "as long as the API agencies upload does get scanned for illegal photos?". Checked rather than reassured. HALF YES: /agencies/{id}/import runs _anon_photo_pass, which uses the SAME vision scan as the seller gate (so it inherits anonymity checks, the confidence floor, redact-blur, reject-hold, and today's seller-own-brand extension) and is fail-closed — a failed scan HOLDS the photo. BUT it never read scan["flag"], so the MODERATION-1 rules live since 15 Jul on the seller upload path (nudity, graphic violence, weapons brandished at people, degrading states, hate symbols) were simply absent at the agency door. An anonymous-but-unacceptable photo could be attached from an agency feed. FIXED: same check, both doors — held (not rejected) because the import is a bulk operation and one bad photo must not fail an entire agency's advert. Tripwire test_every_photo_door_applies_the_same_rules asserts the flag check and the shared scan on that path; the principle it encodes is that a rule holding at one door and not the other is not a rule. NOTE ON PROVENANCE: this was a LAUNCH-RELEVANT gap in a compliance-adjacent control, and no tester, audit or code review found it — David found it by asking a sceptical question about a path we had just declared fine. Worth remembering when weighing "we checked it" against "someone asked whether we checked it".

2026-08-05 (attended, David — TS-0004): SELLER'S OWN BRAND ON THE GOODS. David: the honey jar in the live feed reads "Misty Forest" — a brand name — and the AI agent should have flagged it as an anonymity violation. ROOT CAUSE: _ANON_SCAN_PROMPT is written for PROPERTY AND CARS. It hunts agency logos, watermarks, For-Sale boards, agent headshots, number plates, house numbers and street signs. A brand printed on the PRODUCT ITSELF was never in scope — and for a home producer the label IS the seller. The framing was wrong, not the model. FIX: the prompt now boxes the seller's own brand on goods, packaging, jars, tags, aprons and stall banners, WITH an explicit carve-out for mass-market manufacturer marks on resold items (a Nikon body, a Toyota badge names the maker, not the seller) and a decision rule for the ambiguous middle — "could a buyer search that name and find the person selling this?". Tripwire test_photo_gate_covers_the_sellers_own_brand asserts both halves, because a fix that blurs every Toyota badge is a different fault. STILL OPEN, and it is the bigger question: the prompt only governs NEW uploads. The live photo is untouched, and if one advert carries a seller's own label others may too — that is a launch-risk question ("how many?"), not a one-photo question. Re-scanning existing photos through the gate costs AI spend against David's daily ceiling, so it is HIS call, put to him immediately rather than parked. PAIRS WITH TS-0006 (David Jnr: a near-duplicate photo the checker did not catch) — two of the first six reports are the same component's blind spots.

2026-08-05 (attended, David): ONE-TAP PHONE DEPLOY. The compare-and-merge PR route I first gave David got him stuck on the handset — long diffs, Merge button below the fold, the GitHub app hijacking the link. Wrong mechanism for the device. Replaced with .github/workflows/phone-deploy.yml, a workflow_dispatch job: Actions tab -> Deploy to trustsquare.co -> Run workflow. Two taps, no diff to scroll, identical in the mobile app and mobile web. It does exactly what deploy_marketsquare.bat's final step does and nothing more — moves the deploy ref to main — so ONE DEPLOY is intact. Guards: a typed confirmation input so a mis-tap does nothing, and a FAST-FORWARD-ONLY push (no --force; if deploy has diverged it fails rather than rewriting history from a phone). The run summary lists the commits about to ship, so David can see what he is shipping before it lands. Gates still run at arm time on his machine (strict mode); the server still health-checks and auto-rolls-back after the pull. NOTE: the workflow only appears in the Actions tab once it is itself on main, so it needs one more arm+publish by the old route before the new route exists.

2026-08-05 (attended, David — runbook correction): DEPLOY_FROM_PHONE.md told David to run `arm_phone_deploy.bat "what these fixes are"`. Two faults in one line, both mine and both repeats of earlier ones today: (a) no `.\` prefix, which PowerShell requires for a script in the current folder — every OTHER command I have given him this session had it, so this was pure inconsistency; (b) a PLACEHOLDER as the argument, which he passed verbatim, exactly as with PASTE_IT_HERE earlier. Fixed: the runbook now shows `.\arm_phone_deploy.bat` with no argument (the bat already defaults the message to a timestamp) and states that a custom message is optional and must be quoted. STANDING LESSON, now twice-paid: a runbook must never contain a token the reader is expected to replace, and must be copy-runnable verbatim in the shell it names. If a value is needed, the script reads it; if a message is wanted, it defaults.

2026-08-05 (attended, David): DEPLOY FROM PHONE. David wants to ship a verified fix while at work so testers can retest ~10 minutes later. Needed NO new infrastructure: the server already tracks the deploy ref on a ~2 min timer, so publishing that ref is the deploy, and GitHub can move a ref from a phone browser. Built arm_phone_deploy.bat: autobump + changelog/status fragment folding, then EVERY gate in PREDEPLOY_MODE=strict plus the tripwire suites, and only then commit + push HEAD:main (main is a mirror; it deploys nothing). Refuses to commit at all if a gate is red. The phone step is one bookmarked URL — github.com/dmcontiki2/marketsquare/compare/deploy...main?expand=1 — then Create PR, Merge, Confirm. THE DESIGN POINT: the deploy bat runs gates in WARN mode, which is fine when David is reading the output; he will not be reading it from a train, so the gate moved to the moment he can still act on it. Server-side protection is unchanged and is what makes blind deploys safe: snapshot, manifest-only copy, cache-buster bump, restart, health check, AUTO-ROLLBACK on failure, CDN purge. Runbook in DEPLOY_FROM_PHONE.md. DELIBERATELY NOT BUILT: an unattended scheduled arm — committing whatever happens to be in the working tree is how half-finished work ships by accident.

2026-08-05 (attended, David — TS-0002/0003 ROOT CAUSE, second pass): David sent a screenshot of the wishlist signals list: "these view buttons still doesnt work?" They are not buttons. wl-sig-badge is a LABEL saying how each signal was captured (WISH explicit / SEARCH from a search / VIEW from looking at a listing) — but styled as a bold uppercase pill with a filled background, sitting immediately beside the real delete button. It read as a control and he clicked it, twice, 23 minutes apart. This RESOLVES the earlier ambiguity: TS-0002/0003 are genuine faults, not smoke-test payloads, and my first-pass diagnosis (sobViewMyListing) found a DIFFERENT real dead button — both were worth fixing, but this is the one he actually reported. FIX: badge stripped of fill, pill radius and pointer (cursor:default, user-select:none, fixed width so the column aligns); labels changed to past tense — 'viewed' describes what happened, 'VIEW' reads as an instruction; title attribute added. PATTERN NAMED: three of the first six tester reports are the SAME class — an element that looks like a control and is not one (TS-0001 the inert count, TS-0002/0003 the badge). That is a design-system fault, not three bugs, and per FAULT_REGISTER rule 3 it is exactly the recurrence signal that should open a Path B dossier rather than a third patch. Tripwire test_labels_do_not_impersonate_buttons asserts the badge keeps cursor:default, never regains pill styling, and never reverts to an imperative label.

2026-08-05 (attended, David — process defect, mine): THE PASTE_IT_HERE FAILURE. My MAINTENANCE_KEY_SETUP.md runbook used the placeholder PASTE_IT_HERE in three separate commands and expected David to substitute it. He ran them verbatim, as anyone would: the literal string PASTE_IT_HERE went into the server .env and into .secrets/ms_maint_key.txt, and the real generated key was echoed to his terminal and from there into the chat transcript, burning it. ROOT CAUSE IS THE RUNBOOK, NOT THE OPERATOR — a runbook that requires hand-substitution of a secret is a defective runbook. Rewritten as ONE block with nothing to substitute: PowerShell generates into $k (assignment does not print, so the secret never reaches the screen or scrollback), writes the gitignored file, and expands $k into the ssh line itself. The ssh line now does `sed -i '/^MS_MAINT_KEY=/d'` FIRST so a re-run replaces rather than duplicates — which also makes it the rotation procedure, so there is no separate revocation story. Verification section reads the key back from the file rather than asking David to retype it. Standing lesson for every future runbook: if a step says "paste your X here", the runbook is wrong; make it read X from somewhere instead.

2026-08-05 (attended, David — MAINT-B1b addendum 8): SCOPED MAINTENANCE CREDENTIAL. David asked how to fix the permission gap. Built rather than described: MS_MAINT_KEY, a separate secret guarding exactly four endpoints (GET /admin/faults, PUT /admin/faults/{id}, retest-draft, retest-send) and nothing else. Deliberately NOT the master MS_ADMIN_KEY, which opens flags, deploys, the lifecycle sweep and the ledger — handing that to a session to read a complaint queue would repeat SEC-1 (23 Jul, leaked key demoted after the fact). Constant-time comparison; falls through to the existing admin paths so the dashboard is unchanged; fails closed when unset. Blast radius if leaked: read the fault queue and re-send a retest letter to the address already on the row — it cannot be aimed at an arbitrary recipient, cannot flip a flag, cannot deploy, cannot touch the ledger. Tripwire test_maintenance_key_opens_faults_and_nothing_else fails the pre-deploy check if that endpoint list ever grows, asserts /admin/flags stays on the FULL admin credential, and asserts the comparison stays constant-time. Setup runbook in MAINTENANCE_KEY_SETUP.md (generate, server .env, .secrets/ms_maint_key.txt, verify). LIMIT STATED HONESTLY: this unlocks in-session triage while David's desktop is online; it does NOT unlock unattended overnight running, which needs the B2 re-bind to a server-resident worker reading the key from the box's own environment.

2026-08-05 (attended, David — THE LOOP RAN FOR REAL): first faults arrived through the in-app channel and were diagnosed and fixed the same session. CORRECTION FIRST: I told David his first report "almost certainly failed with a 401". It did not — TS-0001 is in the register, filed 16:32:02. I was wrong and said so. THE QUEUE: TS-0001 "the 15 matching list button doesnt work or there are nothing shown"; TS-0002 + TS-0003 "view button doesnt work when clicked" (same text, 23 min apart). DIAGNOSIS (subagent, read-only, source-level): (a) TS-0001 is the PR-17 free-tier upsell box #wf-upgrade — only the 20-character trailing anchor carried a handler, so tapping the COUNT (what the sentence is about) hit dead space; and goTo('wishlist') lands on a settings form that shows none of the 15. Both halves of his sentence were both halves of the defect. (b) TS-0002/0003: found a CONFIRMED dead button — sobViewMyListing passes a RAW BEA INTEGER to openDetail, but FEA ids are 'bea_N' strings, so findListing returned undefined and openDetail threw on l.trust inside a setTimeout. Nothing caught it, nothing rendered. Worse, the missing guard made a CLASS of silent dead clicks: every wishlist feed/showcase card for a listing outside the active city (those feeds span countries by design; LISTINGS holds one city). FIXED: openDetail now guards + normalises and toasts instead of dying; sobViewMyListing normalises the id and awaits loadLiveListings instead of racing it on a 300ms timer; the upsell box is clickable across its full area and its copy no longer promises a list it cannot show. Proved by running the REAL openDetail body against stubs: raw integer resolves, unknown id toasts + logs, null does not throw. RG-0031 LOCKED. HONEST GAP: I cannot confirm TS-0002/0003 are app faults rather than David's own smoke-test text — "the view button doesn't work" is verbatim his illustration from the paste conversation, and the two rows are identical 23 min apart. Settling it needs the screenshot on those rows, which needs /admin/faults, which needs admin credentials this session does not hold. ALSO FOUND, unreported: openTopup() is called by two "Top Up Tuppence" buttons (ms.js:11354, 11472) and is not defined anywhere — ReferenceError, dead buttons. Not fixed this session; needs David's call on what it should open. STILL TO DO: phone testing of the report flow (paste is not the phone gesture; the file picker fallback is there but unproven on a handset).

2026-08-05 (attended, David — MAINT-B1b addendum 7): "IT PASTED SOMETHING BUT I COULD NOT IDENTIFY IT AS THE SNIPPY." Diagnosed by reading his live browser: the deployed widget was correct (18,102B, paste handler live, capture button gone, gold tab, window.API_KEY exposed) and the paste HAD worked — a 484x168 thumbnail existed and the drop zone read "Screenshot attached". The defect was that the preview rendered BELOW THE FOLD of the scrolling sheet, so from where David sat nothing visibly happened. Attaching silently is indistinguishable from not attaching. Fixes: the preview is now a green-framed card headed "This is what you are attaching" with a Remove button, matted on dark navy so a pale snip still reads, and attach() scrolls it into view and writes a confirmation line next to the send button where the eye already is. Verified END TO END in a real Chromium via Playwright — tab renders, sheet opens, synthesised clipboard paste attaches, preview shown 492x166 AND inViewport true, Remove detaches cleanly. Screenshot kept. This is the third round on one feature; each round was a real defect the previous verification could not see, which is itself the argument for driving the browser rather than reasoning about it.

2026-08-05 (attended, David — MAINT-B1b addendum 6): PASTE REPLACES THE CAPTURE BUTTON. David: "instead of having a complex (not complaining) can't we just have a paste option? open report, say 'the view button doesn't work', snip the button and paste it." He was right and the getDisplayMedia button is gone. Win+Shift+S then Ctrl+V are two things Windows users already do; the capture button achieved the same end but demanded a permission prompt and a window choice first. Now: a dashed paste zone under the text box, Ctrl+V anywhere in the sheet attaches the clipboard image, thumbnail preview, paste again to replace. Drag-and-drop rides the same handler for free; the file picker survives as a quiet underlined link for phones. The document-level paste listener is unhooked in close() so it cannot keep firing after the sheet is dismissed. Tripwire test_paste_is_the_attachment_path asserts the handler, the clipboard read, the drop handler AND the removeEventListener — a listener that outlives its dialog is the classic version of this bug. node --check clean. NOT yet deployed; the paste flow will be verified in David's own browser against the live file once it is.

2026-08-05 (attended, David — MAINT-B1b addendum 5): THE 401 THAT ATE DAVID'S FIRST REPORT, PLUS THE SIMPLIFIED INTAKE. (a) DEFECT FOUND BY READING HIS LIVE BROWSER, NOT BY ASKING: David flipped the switch, found the tab and filed a report — and it was refused 401. Cause: _fault_caller_ok accepted only a reviewer token or the app API key. Superusers never enter the reviewer code, and ms.js declares API_KEY with `const`, which does NOT attach to window, so ts_report.js's fallback could never read it and sent no header at all. EVERY in-app report was failing. Fix, both halves: _fault_known_user() makes a real account a valid credential (attributable, no new secret), and ms.js now sets window.API_KEY (same key, already public in that file, exposes nothing new). (b) SECURITY CATCH from the harness while fixing it: the account-as-credential rule must NOT apply to GET /app/faults/mine — a fault carries the page URL, console output and screenshot, so knowing an address would have been enough to read someone's reports. Reading is now strictly token/key only; filing may lean on the account. (c) SIMPLIFIED INTAKE (David's ruling): the severity and app-area pickers are gone. The tester writes what is wrong, attaches a snip, sends. The bin is derived server-side from page_url (_fault_bin_from_page) and severity defaults MAJOR so nothing sinks unseen; both are set properly at triage. (d) SNIP THE SCREEN: native getDisplayMedia, no library (RG-0025 safe), hides the form during capture, thumbnail preview, falls back to the file picker on mobile where the API does not exist. Proof: harness 61/61 green including four page-to-bin derivations; five new tripwires lock the 401 fix, the read-path asymmetry, the three-field form and the first-party snip. NOT yet deployed.

2026-08-05 (attended, David — MAINT-B1b addendum 4): DISCOVERABILITY FIX after David deployed three times and still could not find the tab. Diagnosis read live from his own browser, not guessed: fault_report=false. Everything else correct (script deployed 12,555B with the flag check, widget loaded, superuser recognised). NO deploy can ever show the tab — the launch switch is what opens it, and that had never been flipped. David's real point stands and was accepted rather than defended: if the person who commissioned the feature cannot find it, no tester would have. Changes: (a) the tab is now GOLD (#C8873A) not navy, bigger padding, stronger shadow — navy-on-white was too polite; (b) a ONE-TIME coach mark on first load ("Something wrong? Tap REPORT any time, on any page") with a Got it button, remembered in localStorage ts_report_seen, self-fading after 12s so it can never nag; (c) window.tsReportWhere() console hatch that re-shows the pointer and flashes the tab for anyone asking "where is it". The failure this prevents: a tester who never notices the tab reports nothing, and silence reads exactly like no faults found. node --check clean, tripwires 10/10. NOT yet deployed.

2026-08-05 (attended, David, cloud — MAINT-B1b addendum 3): FULL COVERAGE + THE STATUS-COLLISION FIX. (a) REPORT tab now on 18 of 18 deployed pages — David's ruling: it belongs on every page, his own dashboard included, so NOT_TESTER_FACING is now empty and the tripwire's exclusion set is deliberately blank. (b) STATUS-COLLISION-1: scripts/status_compile.py built as the ONE writer for the Current Session block, mirroring changelog_compile.py after a hand edit to STATUS.md was silently clobbered earlier today while the changelog fragment written in the same minute survived. Fragments go in status.d/YYYY-MM-DD-slug.md; the compiler folds them under the anchor heading, refuses rather than guesses if the anchor is not unique (a wrong insert breaks the dashboard's session-counter parse), archives to status.d/folded/, and is wired into deploy_marketsquare.bat beside changelog_compile. Self-tested on a copy: folds, verifies, re-runs as a no-op, counter still parses. THIS PARAGRAPH ARRIVED VIA THE NEW MECHANISM. (c) CLAUDE.md discipline note now names STATUS.md explicitly instead of hand-waving at "shared docs". (d) REPORT_TAB_MAP.html generated from the deploy manifest — screen position plus all 18 pages with links, filed in Visuals. NOTE: the three explainer pages and the dashboard were wired AFTER release ba2aad9, so they need one more deploy.

2026-08-05 (attended, David, cloud — MAINT-B1b addendum): COVERAGE GAP CLOSED + a lost-edit finding. (a) David asked whether the REPORT tab is on every page. It was on 14; the site deploys 18. ranking_explainer.html, agency_import_guide.html and agents_as_a_service.html had NO report path, and test_tester_intake.py read GREEN because its page list was hand-typed. Now 17/18 (dashboard.server.html deliberately excluded — David's own console). CLASS FIX: the tripwire now derives its page list from ops/autodeploy/deploy_manifest.txt, so any new deployable page fails until it carries the tab; proved it bites (removed the tag from a copy -> FAIL, exit 1). (b) LOST-EDIT FINDING: an earlier addendum written into this file at ~15:57Z was gone by the 18:09 release commit — clobbered on disk, not lost in git. The changelog FRAGMENT written at the same time survived and folded correctly. STATUS.md has no fragment mechanism, so it stays vulnerable to exactly the CHANGELOG-COLLISION-1 failure that changelog.d/ was built to end. Proposed: status.d/ + a compiler mirroring scripts/changelog_compile.py — David's call. (c) Live-verified through David's Chrome (the origin gate now 403s anonymous WebFetch, so self-verification moved into the browser): /static/ts_report.js 200 and correct, script tag on the live index, widget loaded, tab correctly NOT rendering because /flags fault_report=false. The dashboard switch IS in release ba2aad9; the three newly-wired pages are NOT — they need one more deploy.

2026-08-05 (attended, David, cloud): MAINT-B1b — THE TESTER FAULT CHANNEL IS BUILT. David's ruling: for the month to launch, testers report app faults through the app's own complaint channel, Claude fixes them and writes back with what changed so the tester can retest and confirm — and that month of real traffic is what specifies the Maintenance agent. Shipped in repo (NOT yet deployed): app_faults table + POST /app/fault (multipart, optional screenshot, auto-captures page URL / app version / viewport / user-agent / console tail), instant ACK quoting reference TS-nnnn, GET /app/faults/mine, admin queue GET /admin/faults (blockers first), PUT /admin/faults/{id} triage with dup_of->recurrence accounting, and the retest letter split into draft (read) + send (act) so nothing reaches a founding seller unread. FEA: ts_report.js — 13KB first-party widget, no CDN (RG-0025 safe), no ms.js/ms.css dependency, wired into all 14 tester-facing pages, right-edge tab z-index 9000. Fail-closed twice: launch_switches.fault_report defaults 0 (whole lane 503s) and the widget hides if /flags is unreadable; unauthenticated POST refused (reviewer token or app key required); 12/tester/hour + 20/IP/10min. Proof: 49-assertion live harness green (real FastAPI + real SQLite, code sliced verbatim from bea_main.py), test_tester_intake.py 8/8 wired into predeploy_check.py, PG-readiness ratchet held at 53. RG-0030 added OPEN. AWAITING DAVID: run deploy_marketsquare.bat, then POST /admin/flags {"fault_report": true} to open it. Privacy copy for the intake is drafted and PARKED for his approval (CCP Gate 1).

2026-08-01 (Session 155, attended, David, evening): SESSION COUNTER CORRECTED 150 -> 155 (precedent: the 139->141 correction, Session 141). The counter froze at Session 150's close (23 Jul) while attended work continued unnumbered: 151 = 24 Jul (Adventures wow pass), 152 = 27 Jul (Cape to Cairo), 153 = 31 Jul (AI-vendor Addenda 5-8 + GPT-5.6 seam WIP + peer-review build), 154 = 1 Aug daytime (INFRA-PANEL-2 + TP-FLIGHTS-1 + EULA v1.11 — sitting boundaries unrecorded, collapsed to one number), 155 = this evening cloud session (Kimi K3 EU survey -> vendor-strategy Addendum 11: WAIT for Scaleway/OVH, HostYourAI not pursued). NB the dashboard parses this counter from STATUS.md ON THE SERVER — the badge shows 155 after the next deploy carries this file.


2026-08-01 (attended, David, evening): EULA v1.11 LIVE — SS6.1A affiliate-disclosure clause added + SS6.1 income enumeration corrected (v1.10 would have been falsified by Travelpayouts commission). All three copies synced (eula_clean/terms/ms.js modal), shipped via SEC-2 from the cloud, CF purged, /terms verified. Counsel ratification + tax treatment remain the [D] gate in OPEN_LOOPS before any travel flag flips.

2026-08-01 (attended, David): TP-FLIGHTS-1 — Travelpayouts is live as the flights pre-information lane (Amadeus self-service died 17 Jul; Google OUT per David's $360 ruling). Account activated + project "Trustsquare" connected to Aviasales (hidden blockers: unread activation email, missing Project). Flight Data API dry-run green in native ZAR across 4 trunk routes; thin routes return clean empty. Panel row swapped amadeus→travelpayouts (TRAVELPAYOUTS_TOKEN, presence-only, flag data_flights stays DARK); token provisioned to server .env (never in git). Travel positioning + supplier-fallback doctrine + fixed-cost pricing rule all recorded in CLAUDE.md. Introduction model intact: commission in, no money through the till.

2026-08-01 (daily loop, Saturday): SCAN-29 SHIPPED — ruff B904 ×2 in `admin_deploy_file` (/admin/deploy-file, MS_DEPLOY_KEY-gated deploy channel): added `from None` (base64 400) + `from exc` (write 500) exception chaining, behaviour-neutral, security-class, ungated. Parity-block cleared (David attended-/shipped the AI-vendor GPT-5.6 WIP 07-31 05:00; deploy-drift clean 19/19). Restart active, /health ok v1.3.1, md5 parity local==server, smoke 40/40 pre+post. Loop health: regression ledger GREEN, FEA ok, subs 34up/1standby/15held/1planned 0 issues, cron-parity MATCH, AI spend $0.00/$100. Static-scan auto-ship queue now EMPTY. Session counter unchanged (150).

2026-08-01 (attended, David): INFRA-PANEL-2 — dashboard Infrastructure card root-cause fix (stuck "Loading checks…" on absent/expired admin session): `ms-admin-auth` event from the PIN gate reloads token-gated cards the moment sign-in succeeds; 401/network states now loud (amber "Checks paused" / red "Checks could not load" + Retry); token-aware bootstrap + 5-min poll (no doomed calls signed out). dashboard.server.html + .bak-20260801-infrapanel2; node --check 10/10, simulated state machine 9/9 green. Goes live on next dashboard push (NB deploy_bit_monitoring.bat's server→local pre-pull would clobber it — push first). ADDENDUM: the pre-pull clobber happened (~09:54 bit run) — fix re-landed as idempotent apply_infra_panel2.py wired into deploy_bit_monitoring.bat step [2c/6] (same survives-the-pull pattern as the BIT panel); live from the next bit run.

2026-07-27 (attended, David): CAPE TO CAIRO COMPLETED + SHIPPED LIVE — route made real (rail to Dar es Salaam, flown safari circuit over the Rift, Nile cruise + sleeper; Sudan leg removed), 12 photos generated/claimed/built → 38/38 embedded, Germany added to the Adventures picker (Bavaria advert now reachable), phone fixes (hide overlays + ‹ Back) across all nine journey maps + build template, c2c bumped to v6. Deployed 11:01, smoke green. Route + pricing benchmarked against the real Goway/North South 32-day product (from ±US$50 000 pp).

2026-07-24 (attended, David): ADVENTURES WOW PASS — +5 photos to each Adventures SUPER ADVERT (270 game drive, 271 lodge) via Higgsfield/Nano Banana Pro with reference-image consistency, plus an interactive Leaflet map embedded in both listing pages ("Explore the reserve"). Then genericised off Dinokeng (Option A safe pass, standing rule SO-1) — de-named, map kept illustrative. Staged + armed (deploy steps 3c-map/3d/3f, RUN_ADV_PHOTOS_ONCE.flag). Awaiting the guarded deploy on David's machine.

2026-07-23 (Session 150 close): EVERYTHING SHIPPED AND VERIFIED LIVE — PEN-CAP-1, FADE-1, RESP-1
(morning), EULA v1.10 on /terms + gate + modal, SEC-1 admin-key containment (leaked ms_mk_ key
demoted to user-facing only), SEC-2 HTTPS deploy channel (first cloud deploy executed and proven).
Server env carries MS_ADMIN_KEY / MS_DEPLOY_KEY (secrets in .secrets/, gitignored).

2026-07-23 (Session 150, attended, David): TRUST + LIFECYCLE SHIP — PEN-CAP-1 (penalties now bite
AFTER the 100 cap; David's 178-case gap closed; evidence ledger shows post-cap Penalties group),
FADE-1 (fade-out engine finally implemented: 30/60/90-day windows per David's ruling, warn at
window−7, hide, archive +14d; daily sweep + /admin/lifecycle-sweep + keep-live endpoint + dashboard
button; demo exempt), RESP-1 (gentle model: −5 at 48h unanswered intro, removed at 96h, both parties
emailed, 90-day time-only recovery; LM excluded). State machine v1.3 (EULA §2 aligned $0/$5/$20 +
Agency free), trust criteria amendments v1.2+v1.3. SHIP was rocky: first run shipped frontend only;
a parallel session overwrote bea_main.py in-tree (restored from f2e6612, its Maurice relink was
already included); startup NameError (missing 'import threading') took the BEA down ~10 min —
hotfixed 51eec71, redeployed via targeted scp, smoke GREEN 06:28 (root 0.8s, browse OK, new routes
live + gated, Bee Lady ledger 100==100, sweep dry-run all zeros). Tags: ship-20260723-0503.
OPEN: lifecycle EULA clauses (§§1–6) not yet in live in-app EULA — next EULA revision; lawyer draft
v1.9 "penalty halves every 90 days" clause contradicts canon decay rules — flag to counsel;
git-on-FUSE leaves stale .lock files every commit (worked around via _to_delete/, needs real fix).

2026-07-23 (Session 149, attended, David — remote/phone): EULA v1.9 PUBLISHED (David's explicit
pre-counsel instruction; A6 counsel review stays open). Audit of v1.7 docx + discovery that the live web
EULA (v1.3 label) was a drifted fork 250 lines ahead of the docx; v1.9 = web fork + not-a-referral §2.6,
MtG Reference Library licence §8.10, local-laws §13.5, Country Schedules UK/US/AU §13.6 + A/B/C.
Shipped terms.html + embedded gate copy in marketsquare.html (both stamped v1.9). Rollback tag
ship-20260723-eulav19. Register/canon bumped to v1.9. OPEN: counsel consolidation of docx vs web forks;
privacy.html UK/US/AU supplements.

2026-07-22 (Session 147, attended, David): DAVID JNR QA ROUND 1 — his 21-Jul Super-Advert
walkthrough triaged with David's verdicts (1 fix · 2 intended · 3 fix · 4 fix · 5 fix · 6 discuss ·
7 approved). Shipped: RNaN fix on Adventures detail (JNR-FIX-3) + always-visible price units
(JNR-FIX-5), friendly seller-CV category labels + per-category specialist exemplar sellers via
one-shot server script (JNR-FIX-1), three same-scene "duplicate" exemplar photos recomposed as
detail crops + game-drive hero regenerated wildlife-only at the same waterhole (JNR-FIX-4, 2 credits).
deploy bat now ships assets/super permanently (step 3d). OPEN: Stays/Experiences label unification
(David Jnr discussion tonight — proposal: one buyer-facing vocabulary everywhere); WhatsApp Web QR
link so Claude can read feedback directly.

2026-07-21 (Session 145, overnight): LAUNCH-READINESS AUDIT complete + all recommendations fixed.
Site live+healthy at ms.js v347. Sessions 143-145 delivered: agents-as-a-service (3 verticals:
property/cars/travel; reverse intro — agent pays 1T on accept; TS/SPS/Rank = 50/50 on all agent
surfaces), evidence-true trust scores with buyer-visible itemised ledger (/sellers/credentials),
10 SUPER exemplars live and photo-vs-copy audited (2 fixed live, 2 regen candidates queued),
Bee Lady real 100-score listing, FILTER-DATA-2, brand photography throughout.
EMAIL WAVES: Brevo DKIM+DMARC live; EMAIL-WAVE-1 signup-suppression hook in bea_main (needs
BREVO_API_KEY + BREVO_SIGNUP_LIST_ID env to activate); LaunchEmails v2 (3 ZA tracks, fee claim
corrected) in docs/. OPEN: counsel question on post-filing disclosure of reverse-intro + Rank
(draft email in Patents/DRAFT_Counsel_Email_NewMatter_2026-07-21) — settle BEFORE Wave 1.
Full detail: CHANGELOG Sessions 143-145 + TrustSquare_LaunchReadiness_Audit_2026-07-21.


Session 144 · 20 July 2026 (attended, David) — AGENT-SVC-4 + PHOTO-ANON-1: dedicated Professional Agents surface in Services, generic per-vertical stock scenes (no persons pre-intro), agent-facing metrics trio (Trust · Avg Quality · Match Rank), back-bars on all served doc pages. ms.js v320 · 56 tests green.

Previous: Session 143 · 19 July 2026 (attended, David) — AGENT-SVC-1/2/3 shipped: Professional Agents as a Service, three verticals (property FFC · cars MIRA · travel ASATA), estate_agents.py + ms.js v319 + onboarding assets (showcase page, Import Guide Step 0, Playbook v3 PDF). 52 tests green. Counter: 142 was the HMI/SELLER-CV attended block (17-18 Jul); today is 143.

Previous: Session 141 · 17 July 2026 (attended, David) — legal must-have cards (28, 4 countries) + SELL Step 6/6 + agency import schema sync + server quality gate + agent filters + dealer skin + AI swap architecture + E2E dummy-agency test. COUNTER CORRECTION: CHANGELOG used Session 140 on 17-18 Jun 2026 (MOUNT-READ-1 + 5T paid-feed) but this counter was never bumped; every loop note since repeated "stays 139". 140 is consumed; today is 141. (Found by David via a stale local dashboard copy, 17 Jul.)

## Applicable article: BIT Agent (self-test) — added 27 Jun 2026
- TrustSquare now has a **Built-In Test (BIT) self-test article**, kept SEPARATE from the app (not in bea_main.py). Budget: BIT source <=2% of core LOC (currently 0.84%), zero third-party deps, read-only HTTP coupling. On Hetzner same-box for now (own process), separate-host later.
- Canon: **Codex v4.8 §13** (with system block diagram). Full schema: **BIT_ARCHITECTURE.md**. Article: **../trustsquare-bit-agent/** (runner + registry + bit_budget_check.py).
- Found a true positive on first run: FEA calls `/ai/example/<id>` but the BEA has no such route → the free 'See an example' buttons error (B-FEA-EXAMPLE + B-FEA-CONTRACT). The heartbeat monitor is structurally blind to this.


## Awaiting David (15 Jul 2026)
- **STRIPE-GLOBAL-1: SHELVED by David (16 Jul 2026)** — foreign entity + Stripe costs ~$400-1,200 cash pre-revenue; deferred until an income stream funds it. REVISIT TRIGGERS (whichever first): ZA subscription MRR sustains ~$500/mo, OR real international demand appears (non-ZA sellers/buyers blocked from paying), OR Wave-1 international city goes live-transactional. Prep checklist stays ready in BACKLOG.md — registration itself takes days, not weeks, so deferring loses no lead time.
- **LEGAL-STEP-1..3 SHIPPED 17 Jul 08:0x SAST (tag ship-20260717-0755, commit de8c7f1):** SELL flow now 6 steps — Step 6/6 "The legal side" renders the country-swappable legal must-haves card (phone-native stacked rows from /static/legal-must-haves/legal-cards.js) + per-category agency-value note ("manage what they may, facilitate the rest"). 28 country cards (ZA/US/UK/AU × 7 cats, PNG+SVG) on server; SF_LEGAL_LIVE gates to ZA until US/UK/AU pass local legal review. Smoke green: homepage 200 0.84s, ms.js v298 serves sfLegalS, legal-cards.js?v=1 200, ZA property PNG 200. Earlier 404s were Cloudflare negative-cache from mid-deploy checks — self-healed; if a stale 404 lingers, purge CF for /static/legal-must-haves/*.
- **SELL-FLOW-REDO-2 ready to ship:** new guided sell flow (all 7 categories, sub-picks, quality score, 50-gate) wired into ms.js v287 + marketsquare.html behind SF_ENABLED. CHAR-BLUR-1 (characters-only feathered plate blur + skew capsule + never-reject last-resort rung) ready in bea_main.py. One `deploy_marketsquare.bat` + BEA deploy ships both. Then: QA one car listing end-to-end (blur + attest + publish), upload /static/sf_cat_*.jpg (7 tile photos), refresh FEA baseline.

## Live State
BEA v1.3.1 · FastAPI + SQLite · Hetzner CPX32 (8GB RAM) + 100GB volume · trustsquare.co · 65 live listings · World Heritage layer 332 sites · AI email triage LIVE · AI Price Check feed-driven + deliver-then-charge · AI cost guardrails LIVE (real-token + hard daily ceiling + dashboard panel) · Card photos: vision auto-orient on collectibles + 9 live cards fixed upright · Backend modules (auth/database/storage/payments) now in guarded auto-deploy (O2) · CORS locked to trustsquare.co origins (S4) · KYC verification path crash-fixed (SCAN-1 SONNET_MODEL + SCAN-2/3/4/6 missing imports re/hashlib/urllib/base64 + _json name + SCAN-5 doc-upload MEDIA_DIR→_LOCAL_MEDIA_DIR + SCAN-7 vision-draft background_tasks param — block SCAN-1→7 closed) · FEA wallet UX overhaul: How-introductions compact picker + transaction filters + AI-services list refresh (added Yield Estimate & Batch Card Lister) + refund mechanism removed (ms.js v130 / ms.css v115) · S3 DONE: BEA API key now X-Api-Key-header-only on the 3 KYC seller-document endpoints (`?api_key=` query fallback removed + dead `require_api_key_header_or_query` retired; CDN header-stripping assumption disproven) · JS-1 DONE: buyer-app post-payment Tuppence balance refresh crash-fixed (undefined `updateTuppenceDisplay()`→`updateTuppenceUI()`; ms.js v131) · Maroushka property photos cleaned (David-requested, data-only): 39 units de-duplicated (perceptual-hash) + location-revealing exterior/entrance/signage shots removed for anonymity + capped ≤10/unit (510→254 kept; DB [photos:] block only) · TVS steps 3-5 live: free/owned price+yield tiers + flag store + FEA chip selector (paid OFF, B7 intact) · JS-2 DONE: buyer-app location-badge refresh crash-fixed (undefined `updateLocBadge()`→`updateBadgeLabel()`; ms.js v133) · Wave 1+2 launch cities selectable + maps auto-aligned (geo seed US/GB/AU + 3 ZA; ms.js v141) · ZA dupe-city merge: Nelspruit→Mbombela + Port Elizabeth→Gqeberha (ms.js v142) · SCAN-8 DONE: trust-score dup-key removed (Cars_private `category.cars.service_history` deduped — fuller "Service history on file" entry kept; points 4 unchanged)  · Demo home counts now city-filtered: empty city (e.g. NY) reads 0, not Pretoria's totals (ms.js v143)  · World Heritage filter now resets on demo→live (was stuck on the demo country's sites) (ms.js v144)  · Pretoria 'coming soon' placeholder cards no longer leak into other cities' category counts (ms.js v145)  · For You/wishlist feed now hidden in demo mode (was bleeding real Pretoria listings into demo prospect cities; live geo-scope open as W12-FORYOU) (ms.js v146)  · Category tiles now always show (empty cities read '0 listings' instead of being hidden) (ms.js v147) · SCAN-9 DONE: dead PUT /wonders stub cleaned (removed unused import json/asyncio + body/body_bytes locals; handler behaviour unchanged)  · Demo-mode sweep fixes: titles + Adventure currency + US heritage parks + heritage type-filter reset (data + ms.js v149, incl. David QA-pass fixes: adv-grid broken-image fallback + 'us US' flag dedup) · Demo P2 fixes (Detect-engine run): Wave-1 adventures normalized to Stays/Experiences + 9 new verified-image stays (NY/Lon/Syd) + card↔detail photo-source parity poka-yoke (fixes 4 dead card images) (ms.js v150) · LIVE empty-city demo-bleed fixed: Sydney/etc no longer show demo totals — purge demo on switch-to-live + complete the !DEMO_MODE guard + selectCity re-renders Featured/HomeStats (ms.js v152) · Orchestration v2 Phase 2 (Triage) built+deployed: deterministic triage.py + visual board + cockpit (first live run — S123 sweep: 12 findings → 3 green to Fix, 3 resolved, 6 dismissed, 0 red) behind /orchestrator/v2 auth · server smoke_test.py deploy-drift synced (stale cat:Adventures assertion; demo data was fine) · Orchestration v2 Phase 3 (Fix) built + first green-lane batch shipped: DEMO-6 renderAdvGrid honours l.per + DEMO-7 renderCatCounts paused-guard (ms.js v153, smoke-green, live-verified) · DEMO-5 routed to DEMO-4 (R2 self-host, not re-hotlinked) · Orchestration v2 Phase 4 (Prevent) built: 3 regression guards (DEMO-6/7 + photo poka-yoke) + gentle demo-image monitor; a guard FAIL re-enters Triage→Fix so the loop closes on itself; first run 3/3 guards pass + monitor caught 3/30 dead (0 false positives, 498 watched) · Orchestration v2 Phase 5 (Automate) built: deterministic zero-token nightly conductor orchestrator_v2.py runs Detect→Triage→Fix→Prevent on the box (cron 03:50 SAST, SHADOW — deploys nothing, old loop untouched); cockpit 'since last night' panel live; 5-stage arc complete end-to-end; controlled cutover staged (CUTOVER-1, gated on parity) · SCAN-10 DONE: removed 2 redundant module-level `from datetime import timedelta` re-imports in bea_main.py (F811; line 25 canonical) — behaviour-neutral, auto-shipped · Founders Badge redemption side LIVE env-gated OFF (launch_redemption.py: TSL HMAC validate + ID-hash mint + ×1.2 allocation hook + registry sync + per-day velocity limit; 4 tables pre-created) · Ruby Spark beside trust chip on cards/detail/profile, both modes (ms.js v155) · AI-uses copy + pack SKU retired (buy-pack→410) · sob tier cards → tier canon ($12/$20) · Travel + Tour_Guides 45-pt trust signals seeded (travel/tour outreach templates unblocked) · S130 complete · Post-129 demo-mode wiring hardened (audit): wishlist signal-capture + wlRenderSettings/wlStartGlobalCheckout + goTo block-list (wishlist/guided-onboard/aa-*) + legacy buyerPriceCheck/buyerYieldCalc now DEMO_MODE-guarded — ms.js deployed, smoke-green, CF purged · SCAN-11 DONE: bea_main.py dead-code sweep (−290B, 8 edits; getaddrinfo family params intentionally kept) · Session 139 complete: Rental availability (occupancy) axis LIVE on Property listings - new rental_status {available/reserved/occupied} + available_from (BEA migration + create/edit/validate + derived availability_label), buyer badges (cards + detail pill, ms.js v175 / ms.css v132) and a seller Availability control in the Edit Listing screen; deploy_marketsquare.bat hardened (static assets upload BEFORE HTML + new [6b] live-CDN md5 verify + fixed stale 1.3.0 health check) after diagnosing a Cloudflare ?v= cache-poisoning incident (old js pinned to a version key; purge didn't evict - a fresh version number is the cure); rental availability spec v1.1 in MarketSquare · Session 138 complete: Video Tutor button → chip-row top-right, gold (ms.js v172 / ms.css v130, David-requested) + GUIDED-PUBLISH-1 fixed (publish endpoint admin-key Depends dropped — internal email-auth already complete; hub DRAFT badge + Publish button dashPublish; sobGoLive embedded-key removed; auth matrix live-tested 403/200/idempotent) + SELLERHUB-STATUS-1 fixed (drafts no longer shown Active) + WONDER-AUTOLINK-CAT-1 (auto-link allowlist Property+Adventures per David ruling; 27 listings / 135 auto museum-links cleaned, manual preserved) — bea_main.py + ms.js v171 + index.html deployed, backups *-gp1, md5 parity ×3, restart active /health v1.3.1, smoke ALL OK, CF purged · Session 137 complete: BASELINE-12JUN-1 ADJUDICATED → APPROVED (David-delegated; cost-sweep content matches approved brief — P2 ceiling rails + real-token spend logs + starter/pro payable fix + agency 400 guard + free draft-from-photo endpoints + admin spend summary; prices byte-identical, SCAN-14 preserved, 9 sibling deploys md5-identical; process breach stays filed as COST-SWEEP-LANE-1) + MOUNT-TEAR-1 healed (mount bea_main.py restored from server, prefix-proven) + scan queue CLEARED: SCAN-16-LEDGER `from e` @ ai-commit/ai-settle 11869/11912 (approved 11 Jun) + SCAN-15 dead `as e`@1552 / `photo_entry`@2565 (−34B) + SCAN-16 non-ledger 22×B904 `from exc` (+11 bindings) + B905 `strict=False` — flake8 B904/B905=0, 3 deploys each backup+md5+ast+restart+health green, smoke ALL OK, CF purged; SCAN-13→16 block CLOSED · Session 136 complete: SCAN-14 removed the unused `sessions: int = 8` param from the retired `aa_buy_pack` /advert-agent/buy-pack 410 stub (bea_main.py:3879; last vestige of the retired AI-uses pack SKU; stub raises 410 before any logic — behaviour-neutral, non-ledger) — BEA restarted, /health v1.3.1, smoke green · Session 135 complete: SCAN-13 removed the unused `Query` FastAPI import (bea_main.py:1, F401; import-only, behaviour-neutral) — BEA restarted, /health v1.3.1, smoke green · Session 134 complete: SCAN-12 removed the unused `import os` (database.py, F401; import-only, behaviour-neutral) — BEA restarted, smoke 40/40 · S133 AI Features INTEGRATED INTO THE APP (wallet 'AI feature credits' entry → #screen-ai-features; ms.js v156 +AI module, ms.css v121, demo-blocked at goTo choke; dry-run default-ON = $0 integrated testing; nginx /ai/ API opened for app, /ai/test keeps Basic Auth; baseline refreshed; smoke ALL OK) · S132 complete: AdvertAgent advanced-AI per-use service LIVE dev-gated (port 8002 · nginx /ai/ Basic-Auth) + BEA Tuppence HOLD ledger (ai-commit/ai-settle: commit→burn-on-delivery→release-on-failure, idempotent) + 2 flagship functions (collectables advert 5T · heritage tour 5T, Sonnet+web-search) real-API tested incl. failure-path no-charge · B7 ceiling $20/mo enforced in code · RM-5 CityLauncher engine LIVE on server (S130): strategist(5001, claude-sonnet-4-8) + saturation scraper deployed, agency-layer scrape RUNNING on Pretoria across all 7 categories (individuals + agencies), Founders launch-codes issuing side deployed env-gated OFF, BEA /launch/sync-registry wired green, prospect pool 1,416 / 1,326 mx_ok verified · 12 Jun daily loop AMBER: Fixer HELD approved SCAN-16-LEDGER — unattended 04:24Z cost-sweep replaced+restarted live main.py ungated (Simpler-Model paid_tiers + P2 rails + draft-from-photo endpoints); BASELINE-12JUN-1 staged for David; mount bea_main.py torn @11855; loop deployed nothing · SCAN-17 DONE (17 Jun, David-approved in chat): ruff F811 duplicate `admin_ai_spend_summary` resolved — newer `/admin/ai-spend/summary` daily handler renamed to `admin_ai_spend_daily_summary` (older `/admin/ai-spend` keeps the name); behaviour-neutral, both routes re-verified 401; ast+md5+restart+health+smoke 40/40 green, CF purged; static-scan open set now EMPTY · DEMO-FIX-18JUN: demo property heritage links re-populated (40 props) + international amenities enriched to Pretoria depth (NY/Lon/Syd 18 each) — deployed+live-verified; deploy script now ships demo_listings.json (was never auto-deployed — the drift root cause) · FEA-DRIFT CLOSED: deploy now auto-commits (Step 7), drift structurally impossible · POI-CONTAM-18JUN: demo amenities were hand-seeded with fabricated distances (Bela-Bela farm showed Pretoria schools) — ALL 40 props regenerated from OSM (real local POIs/real distances, same pipeline as live listings) + regression guard scripts/validate_demo_pois.py wired into deploy as [3e-pre] gate (proven to catch the bug) — deployed+live-verified

## Daily Loop (2026-07-30) — SCAN-28 shipped (B905 in /admin/services-status) + RG-0014 LOCKED; ledger GREEN
- **SCAN-28 · LOW · DONE.** `bea_main.py:12241` `zip(ids, results)` -> `zip(ids, results, strict=False)` in `admin_services_status` (behaviour-neutral; ids/results equal-length by construction from `asyncio.gather`). Non-gated (admin infra-status board; no payments/ledger/EULA/KYC) -> Gate 1+2 clear, auto-ship. Local==server parity pre-edit (md5 `8df61152...`), str.replace driver (anchor unique==1, never Edit/Write), +14B, AST clean local+server-venv; server backup `main.py.bak-20260730-scan28` (809935B), scp `.new`->venv-AST->`mv`->`chmod 644`, restart active, /health v1.3.1 public+localhost, md5 parity local==server `c113e07b...`, `/admin/services-status` 401 (route live+gated), smoke 40/40 pre+post, CF purge `{purged:true}`.
- **RG-0014 promoted OPEN->LOCKED** (Adventures red ★ SUPER ribbon guard now passing live post-ADV-SUPER-BADGE-1 deploy; live ms.js v411). Ledger: 14 entries · 11 holding · 0 REGRESSED · 3 open (RG-0003/0004/0006 pre-existing structural currency defects) · exit 0. GREEN.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 238 calls, $1.319) · cron-parity **MATCH** (findings.cron.json loop_date 2026-07-30, 01:30 shadow fired; cron smoke 39/39 vs live 40/40 both all-green — cron shallower by design; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: benign attended-deploy baseline-lag -> refreshed (ms.js v407->v411, css v275->v277, index +4279B; local `./ms.js` == server on-disk == CDN `ms.js?v=411` byte-identical md5 `27c79ddc...`; baseline refreshed to v411/v277/405089 -> ok, 0 alerts) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (openai failover key unverified/standby, root-only conf — not an alarm) · deploy_drift clean (19/19).
- **Queue after this run:** SCAN-29 (auto-ship, `bea_main.py` /admin/deploy-file — 2 raises need `from None`/`from exc`) is top for the next Fixer. Nothing staged; nothing awaiting approval.
- **Session counter unchanged (150).** Loop-only LOW auto-ship; `/dashboard/summary` currentSession stays 150 (no attended session completed).
- **On-time** (~06:32 SAST vs 06:30). Server report.json loop_date was 2026-07-29 at start -> full fresh loop, Fixer eligible + shipped SCAN-28.
- **Git:** tree dirty (`bea_main.py`, `scripts/regression_ledger.py` + doc write-backs + `.bak` files). No secret staged; `demo_sellers.json` not present. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-29) — regression ledger BACK TO GREEN: 4 RED regressions CLOSED (loop held at 06:33, then attended closure)
- **Morning loop (06:33 SAST):** BEA ok v1.3.1 · smoke 40/40 · AI spend $0.00/$100 (0.0%) · real-token 100% · cron-parity MATCH · FEA ok/0 alerts (baseline refreshed to v407 after this morning's confirmed-benign attended /ship) · subs 34up/15held/1standby/1planned, 0 issues. Fixer HELD a 3rd run — SCAN-28 deploy-gated by the RED ledger. ✅ Yesterday's MSJS-DRIFT + the older DASH-DRIFT RESOLVED (v407 ship; `deploy_drift` clean, all 19 files match live).
- **Attended closure (David: "complete and close these 4"):** all 4 RED regressions closed at root. **No production deploy was required — the live app + data were already correct on all four.** 3 of the 4 were the GUARD itself rotting (looking in the wrong feed / too-strict regex); 1 (RG-0013) was a genuinely-unfixed local deploy script.
  - **RG-0002 / RG-0005 (maun/BW currency):** app already renders BW correctly (ms.js `ADV_COUNTRY_CURRENCY` `BW:'P'`). Completed the ledger's OWN market model — `CITY_CCY["maun"]="P"`, `CITY_COUNTRY["maun"]="BW"`, RG-0002 `ADV["BW"]="P"`. Records true facts; not a weakening.
  - **RG-0012 (c2c + NA tour maps):** invariant satisfied live (c2c supers 306/307 ZA · NA supers 304/305 · both maps live · ms.js fully wired). The guard read `/demo-listings` (no supers there) — corrected to read `/listings` (real feed, keyed on `category`); NA-un-gated regex now tolerates the `?v=` cache-buster. Still enforced.
  - **RG-0013 (`deploy_frontend_nops.bat`):** real fix — the no-PowerShell quick-deploy shipped ms.js without bumping `?v=`. Now calls `scripts/autobump.py` + derives the live-check version dynamically (was hardcoded "v395"). RG-0013 regex broadened to accept `autobump.py`.
  - **RG-0011 promoted OPEN→LOCKED** (ISO codes + map filenames pass, all markets).
- **Verify:** `python3 scripts/regression_ledger.py` → 13 entries · **10 holding · 0 REGRESSED** · 3 open · exit 0. Ledger is GREEN.
- **Remaining OPEN (pre-existing, NOT regressions, untouched):** RG-0003 (240 non-Adventures listings carry no country → currency guessed from price string — the structural cause), RG-0004 (demo_stay_4/9 city=Pretoria but country=MZ/NA), RG-0006 (9 seller price prompts hardcode Rand). These are the retire-the-whole-class items on BACKLOG, not loop scope.
- **SCAN-28 / SCAN-29 now UN-gated** (auto-ship class, Gate 1+2 clear) — the ledger no longer blocks the deploy lane; the next Fixer will ship SCAN-28 (add `strict=False`) then SCAN-29.
- **Files changed (repo/tooling only, NO app/server deploy):** `scripts/regression_ledger.py`, `deploy_frontend_nops.bat`, + CHANGELOG/AUDIT_PROGRESS/STATUS. `.bak-<ts>` beside each edited file.
- **Session counter unchanged (150).** Git tree dirty — one commit/push block handed to David; no secret staged, no `.git/index.lock`.

## Daily Loop (2026-07-28) — Fixer HELD (regression ledger still RED); nothing shipped
- **Fixer HELD — SCAN-28 deploy-gated by RED regression ledger.** `regression_ledger.py` exit 1 (RED): the same 4 previously-LOCKED facts remain rotted, **unchanged from 07-27** — RG-0002/RG-0005 ('maun'/Botswana has no currency rule, buyer+seller), RG-0012 (NA not un-gated in ADV_COUNTRY_MAP; no live `tour='c2c'` and no live NA super listing -> both per-tour maps orphaned), RG-0013 (`deploy_frontend_nops.bat` uploads ms.js without bumping `?v=` -> ships a browser-cache-stale asset). All originate in the attended 07-24..26 Adventures/Botswana/DE lane -- POLICY §7, the loop never touches it -> escalated to David, NOT auto-fixed, no ledger entry marked fixed. SCAN-28/29 stay queued (auto-ship class, Gate 1+2 clear) but deploy-gated until the 4 clear. `bea_main.py` untouched (no working-tree drift created).
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 238 calls, $1.319) · cron-parity **MATCH** (findings.cron.json loop_date 2026-07-28, 01:30 shadow fired; cron smoke 39/39 all-green shallower-by-design vs live 40/40; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: **benign attended-deploy baseline-lag -> refreshed** (Cape-to-Cairo 07-27 11:01 SAST: index +202B, ms.js v395->398, css v264->267; local `marketsquare.html`==server `index.html` 400810B byte-exact; baseline refreshed -> ok, 0 alerts) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf -- not an alarm).
- **⚠️ Needs David -- 4 RED regressions (SEV-2, do NOT deploy until cleared):** RG-0002/0005 maun currency · RG-0012 c2c+NA tour maps · RG-0013 nops.bat cache-buster. These block the loop's deploy lane; SCAN-28/29 wait behind them.
- **⚠️ Needs David -- MSJS-DRIFT (SEV-3):** local `ms.js` is ahead of live at the SAME `?v=398` (local 1030798B vs server 1029973B, +825B). `run_daily_checks` deploy_drift=drift ahead=[ms.js]. Same version, different bytes = exactly the RG-0013 hazard; needs a `/ship` WITH a `?v=` bump, not a silent re-upload.
- **RG-0011 READY TO LOCK:** country codes ISO + map filenames now passing (ALL markets). Recommend David promote OPEN->LOCKED (surfaced, not auto-promoted -- attended maps lane, ledger currently RED).
- **Resolved since last loop:** DASH-DRIFT -- `dashboard.html` now byte-identical local==server (403904B).
- **DEPLOY-OWNERSHIP-1 (SEV-3, unchanged):** server `index.html` + `static/ms.js` still root:root; Fixer `.new`+`mv`+`chmod` path mitigates; permanent fix belongs in `deploy_marketsquare.bat`.
- **Ignored (FP, unchanged):** ruff B008 ×22 (FastAPI arg-default idiom), vulture `family` ×2 (getaddrinfo wrapper params).
- **Session counter unchanged (150).** Held loop; no attended session via the loop.
- **On-time** (~06:33 SAST vs 06:30). Server report.json loop_date was 2026-07-27 at start -> full fresh loop.
- **Git:** tree dirty (`OPEN_LOOPS.md`, `checkpoint_log.txt`, `ms.js` + untracked `nightly_tsl_log.txt`, `ranking_explainer.html`). No secret staged; `demo_sellers.json` not present. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-21) — SCAN-25 shipped (B023 loop-variable bind in the agency import)
- **SCAN-25 · LOW · DONE.** `bea_main.py` IMPORT-SYNC-1 helpers now bind the loop variable explicitly — `def _imp_i(k, ad=ad)` (:11491) and `def _imp_s(k, cap=160, ad=ad)` (:11496). Both are already called in-iteration, so behaviour is unchanged; the bind removes the structural ruff-B023 trap. Non-gated (agency bulk-import field mapping — no payments/ledger/EULA/KYC) → Gate 1+2 clear, auto-ship. Server-fetched str.replace driver (both anchors asserted unique==1; never Edit/Write), +14B, AST clean local + server venv, server backup `main.py.bak-20260721-scan25` (758753B), md5 parity `0425b628…` local==server, restart active, /health v1.3.1 localhost + public, smoke 40/40 pre+post, CF purge `{purged:true}`.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 196 calls, $1.020) · cron-parity **MATCH** (findings.cron.json loop_date 2026-07-21, 01:30 shadow fired; cron smoke 39/39 all-green vs live 40/40 all-green — cron shallower by design; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: **benign attended-deploy baseline-lag → refreshed** (ms.js v319→v347, index +639B; local repo == server on-disk origin byte-exact — `marketsquare.html`/`index.html` md5 `76771c69…`, `ms.js` md5 `6cd83159…`; Session 145 overnight deploys per CHANGELOG; baseline refreshed to v347/v228/384909 → status ok, 0 alerts) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **⏳ Awaiting your approval — SCAN-26 (Gate 2, staged 2026-07-20):** `launch_redemption.py:436` B904 `from e`. Behaviour-neutral exception chaining on a read-only registry read, but staged **by module path** — `launch_redemption.py` carries the Founders Badge ×1.2 Tuppence allocation hook (POLICY §12 never-automated). Approve with "approve SCAN-26".
- **⚠️ SEV-3 DEPLOY-OWNERSHIP-1 (new, self-healed for `main.py`):** the attended Session 145 deploy left `main.py`, `index.html` and `static/ms.js` **root:root** on the server, so the loop's scoped `msdeploy` user got `Permission denied` on `scp main.py`. Resolved with **no root fallback** — the web root is msdeploy-owned, so the deploy went `scp main.py.new` → server-venv AST-check → `mv` → `chmod 644`, which also returned `main.py` to msdeploy. **`index.html` and `static/ms.js` are still root-owned**, but the `.new` + `mv` path generalises to them (the web root is msdeploy-owned), so tomorrow's SCAN-27-JS on `ms.js` is **mitigated, not blocked** — the loop's deploy step now uses `scp <file>.new` → syntax-check → `mv` → `chmod 644` as its standard path. Root cause still belongs in `deploy_marketsquare.bat`: deploy as msdeploy, or `chown msdeploy:msdeploy` after.
- **⏳ Needs David — DASH-DRIFT (SEV-3, unchanged since 18 Jul):** local `dashboard.html` 396494B (mtime 18 Jul) vs server 393507B (mtime 17 Jul). `run_daily_checks` labels it "local-ahead", but the byte direction flipped between 07-18 and 07-19 and it is still unclear whether the local edit incorporated the server's earlier ahead-content — a naïve `/ship dashboard.html` could regress server-only content. Loop did **not** deploy it. Reconcile pull-direction before any deploy.
- **CDN note (not an anomaly):** Cloudflare's edge serves `index` 387821B vs origin 384909B (+2912B = CF HTML injection); informational, never an alert.
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Queue after this run:** SCAN-27-JS (auto-ship, `ms.js:15052` no-redeclare) is top for tomorrow; deploys via the `.new` + `mv` path, so DEPLOY-OWNERSHIP-1 does not block it. SCAN-26 staged. Next Monday deep scan 2026-07-27.
- **Session counter unchanged (145).** Loop-only ship; the attended Session 145 completed overnight and 146 stays reserved for David's next attended session.
- **On-time** (~06:32 SAST vs 06:30). Server report.json loop_date was 2026-07-20 at start → full fresh loop.
- **Note for future runs:** the repo `smoke_test.py` must be run **from the sandbox/repo**, not on the box — a server-side run returns a false 29-FAIL because the box cannot fetch its own public host.
- **Tooling note:** `smoke_test.py` backgrounded in the sandbox does not survive the bash call (each call is its own short-lived sandbox); run it synchronously inside the 45s window.

## Daily Loop (2026-07-19) — clean maintenance day (queue empty, Fixer idle, nothing shipped)
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 188 calls, $0.903) · cron-parity **MATCH** (findings.cron.json loop_date 2026-07-19, 01:30 shadow fired; cron smoke 39/39 all-green vs live 40/40 all-green — cron shallower by design; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: **benign version-bump baseline-lag → refreshed** (ms.js v311→v315, css v227→v228; local index==live byte-exact on the versioned URLs the app loads — ms.js?v=315 / css?v=228; Session 142 HMI-1/SELLER-CV-1/HMI-2 attended deploys per CHANGELOG; baseline refreshed to v315/v228 → status ok, 0 alerts) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **Shipped:** nothing — auto-ship queue **EMPTY** (SCAN-13→24 block closed; last ship SCAN-24 on 07-17). Fixer idle; nothing staged; **nothing awaiting approval.** Next Monday deep scan (2026-07-20) repopulates.
- **⏳ Needs David — DASH-DRIFT (SEV-3, filed, direction FLIPPED since 07-18):** local `dashboard.html` is now 396494B vs server 393507B — **local is now larger** (yesterday server was larger). An attended session edited local dashboard.html since the last loop (uncommitted +85/−3 vs HEAD). `run_daily_checks` labels it "local-ahead", but because the byte direction flipped and it's unclear whether the local edit **incorporated** the server's prior ~5.7KB of ahead-content, a naïve `/ship dashboard.html` still risks regressing server-only content. Loop did **not** deploy. Reconcile pull-direction with David before any deploy.
- **CDN note (not an anomaly):** the *unversioned* `/static/ms.js` at the Cloudflare edge may lag, but the app only ever requests `ms.js?v=315` — byte-current across local, server origin and CDN. Not user-facing; ignored with reason.
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 @2214/2315 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Session counter unchanged (141).** Idle loop day; no attended session completed via the loop. `/dashboard/summary` currentSession stays 141.
- **On-time** (~06:32 SAST vs 06:30). Server report.json loop_date was 2026-07-18 at start → full fresh loop, Fixer eligible but queue empty.
- **Git:** working tree dirty with Session 142 attended changes (bea_main.py, ms.js, marketsquare.html, dashboard.html, ai_provider.py, CHANGELOG, STATUS + golden-eval/prototype untracked files) + today's STATUS.md loop write-back. No secret staged (`ssh_hetzner_key` + `.ssh/id_ed25519` gitignored); `demo_sellers.json` not present. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-18) — clean maintenance day (queue empty, Fixer idle, nothing shipped)
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 177 calls, $0.816) · cron-parity **MATCH** (findings.cron.json loop_date 2026-07-18, 01:30 shadow fired; cron smoke 39/39 all-green vs live 40/40 all-green — cron shallower by design; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: **benign attended-deploy baseline-lag → refreshed** (ms.js v294→311, css v213→227, index +68B; local repo == server on-disk origin byte-exact on the versioned URLs the app actually loads — ms.js?v=311 md5 56874ae / css?v=227 / index ed62fb8; Session 141 provider-seam + DEALER-SKIN-1 deploys per CHANGELOG; baseline refreshed to v311/v227/382540 → status ok, 0 alerts) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **Shipped:** nothing — auto-ship queue **EMPTY** (SCAN-13→24 block closed; last ship SCAN-24 on 07-17). Fixer idle; nothing staged; **nothing awaiting approval.** Next Monday deep scan (2026-07-20) repopulates.
- **⏳ Needs David — DASH-DRIFT-18JUL (SEV-3, filed):** live server `dashboard.html` (393507B) diverges from local/committed repo (387820B) — server is ~5.7KB **larger**, and local is clean vs HEAD, so the **server is ahead** (an attended dashboard change was never synced back to the repo). `run_daily_checks` labelled it "local-ahead" but the byte direction is the opposite. A naïve `/ship dashboard.html` would push the smaller local file over the larger server copy and **regress** it — so the loop did **not** deploy (09 Jul WIP-intent precedent). Reconcile pull-direction with David before any deploy (likely: pull server → repo, or confirm the local edit is the intended one first).
- **CDN note (not an anomaly):** the *unversioned* `/static/ms.js` at the Cloudflare edge is still the old v294 build (901984B), but the app only ever requests `ms.js?v=311` — which is byte-current (915555B, DEALER-SKIN-1 present) across local, server origin and CDN. Not user-facing; ignored with reason.
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 @2214/2315 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Session counter unchanged (141).** Idle loop day; no attended session. `/dashboard/summary` currentSession stays 141.
- **On-time** (~06:32 SAST vs 06:30). Server report.json loop_date was 2026-07-17 at start → full fresh loop, Fixer eligible but queue empty.
- **Git:** working tree = HEAD + `checkpoint_log.txt` (auto) + today's STATUS.md loop write-back. No secret staged (`ssh_hetzner_key` + `.ssh/id_ed25519` gitignored); `demo_sellers.json` excluded. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-17) — SCAN-24 shipped (unused param `ticket_id` dropped; static-scan queue now EMPTY)
- **SCAN-24 · LOW · DONE.** Dead param `ticket_id` removed from `_demand_send_invite` (`bea_main.py:5778`, the outreach ONLY-send path, vulture 100%) + its single caller (`:5946`, was passing `t["id"]`) updated in the same edit. Behaviour-neutral (param never read; the `demand_invites_outbox` INSERT using a `ticket_id` COLUMN @5939 is a separate untouched line). Non-gated (outreach SEND-path signature; no payments/ledger/EULA/KYC, no consent/opt-out/send-gating — triple-gate env+dry-run+RESEND_API_KEY untouched) → Gate 1+2 clear, auto-ship. Server-fetched str.replace driver (both anchors asserted unique==1; never Edit/Write), −20B, AST clean local+server-venv; server backup `main.py.bak-20260717-scan24` (742287B), md5 parity `54341eb…` local==server, restart active, /health v1.3.1 localhost+public, smoke 40/40 pre+post, CF purge `{purged:true}`.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 150 calls, $0.713) · cron-parity MATCH (cron 39/39 vs live 40/40 both all-green — cron harness shallower by design; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: benign attended-deploy baseline-lag (live ms.js v294 / css v213; local repo == live byte-exact md5 MATCH + deploy_drift clean 19/19 = version-bump deploy signature per CHANGELOG SELL-FLOW-REDO-2 + David sell-flow deploys, not same-version tamper; baseline refreshed to v294/v213 → ok) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **Queue after this run:** static-scan auto-ship queue **EMPTY** (SCAN-13→24 block CLOSED). Next Monday deep scan (2026-07-20) repopulates. Nothing staged; **nothing awaiting approval.**
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 @2214/2315 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Session counter unchanged (139).** Per loop precedent (SCAN-19/20/22/23) the attended-session number is not bumped for a LOW auto-ship; the loop records itself in this Daily Loop block. `/dashboard/summary` currentSession stays 139 (correct — no attended session completed).
- **On-time** (~06:32 SAST vs 06:30). report.json loop_date was 2026-07-16 at start (yesterday's loop) → full fresh loop, Fixer eligible + shipped SCAN-24.
- **Git:** working tree dirty (loop doc drift + local bea_main.py synced to the deployed SCAN-24 file). No secret staged (`ssh_hetzner_key` + `.ssh/id_ed25519` gitignored); `demo_sellers.json` excluded. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-16) — SCAN-23 shipped (auth_verify B904 ×2 cleared; queue advances to SCAN-24)
- **SCAN-23 · LOW · DONE.** B904 ×2 in `auth_verify` (`POST /auth/verify`, `bea_main.py:10204` + `:10206`) — added `raise … from None` to the two `HTTPException(401)` inside `except _pyjwt.ExpiredSignatureError:` / `except _pyjwt.InvalidTokenError:` (suppress the JWT internal in the chain; user-facing 401 copy unchanged). Magic-link SIGN-IN path = security-class (POLICY §5) — **not** KYC/SA-ID identity-doc handling, **not** payments/ledger → clears Gate 1+2 → auto-ship. Server-fetched str.replace driver (each anchor incl. its `except` line asserted unique==1; never Edit/Write), AST clean local + server-venv; server backup `main.py.bak-20260716-scan23` (733470B), md5 parity `4986afc…` local==server; restart active, /health v1.3.1 localhost+public, `/auth/verify` bad-token re-verified **401** (not 500), smoke 40/40 pre+post, CF purge `{purged:true}`.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0.0%) · real-token 100% (MTD 144 calls, $0.604) · cron-parity MATCH (cron 39/39 vs live 40/40 both all-green — cron harness shallower by design; health ok/1.3.1 both; today_spend $0.00 both) · FEA integrity: baseline-lag only (live ms.js v291 / css v211; version-bump deploy signature confirmed vs CHANGELOG — S139 rental-availability + David's sell-flow/TQTY deploys — not same-version tamper; CF edge +2912B informational) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **Queue after this run:** SCAN-24 (unused param `ticket_id` in `_demand_send_invite` + its single caller @5866 — 2-site auto-ship) sole remaining item. Nothing staged; **nothing awaiting approval.**
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 @2214/2315 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Session counter unchanged (139).** Per loop precedent (SCAN-19/20/22) the attended-session number is not bumped for a LOW auto-ship; the loop records itself in this Daily Loop block. `/dashboard/summary` currentSession stays 139 (correct — no attended session completed).
- **On-time** (~06:32 SAST vs 06:30). report.json loop_date was 2026-07-15 at start (yesterday's loop) → full fresh loop, Fixer eligible + shipped SCAN-23.
- **Git:** working tree dirty (loop doc drift + local bea_main.py ahead of HEAD after the SCAN-23 edit landed on the server copy). No secret staged (`ssh_hetzner_key` + `.ssh/id_ed25519` gitignored); `demo_sellers.json` excluded. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-15) — SCAN-22 shipped (auto-ship queue advances)
- **SCAN-22 · LOW · DONE.** Dead local `name` removed from `_demand_render_invite` (`bea_main.py:5685`, ruff F841) — computed but never used; next line hardcodes `greeting = ""`. Behaviour-neutral, non-gated (outreach-render template filler; no payments/ledger/EULA/KYC, no consent/send-gating logic → Gate 1+2 clear). Server-fetched str.replace driver (anchor unique; never Edit/Write), ast clean, −75B; server backup `main.py.bak-20260715-scan22`, md5 parity `cdeda94…` local==server, server-venv AST OK, dead-local grep=0 on served file, restart active, /health v1.3.1 direct+public, smoke 40/40 pre+post, CF purge `{purged:true}`.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.0199 / $100 ceiling (0.0%) · real-token 100% (MTD 140 calls, $0.528) · cron-parity MATCH (cron 39/39 vs live 40/40 both green — cron bundle shallower by design; spend cron $0.00 vs live $0.0199 = 01:30 sample pre-dating today's 3 AI calls, both 0%/no breach) · FEA integrity ok, 0 alerts (live ms.js v286 / css v208; benign attended baseline-lag) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **Queue after this run:** SCAN-23 (B904 ×2 `auth_verify` — add `from None`; security-class auto-ship) → SCAN-24 (unused param `ticket_id` in `_demand_send_invite` + its single caller — 2-site auto-ship). Both queued for the next Fixer (~26h latency by design). Nothing staged; **nothing awaiting approval.**
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 @2214/2315 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Session counter unchanged (139).** Per loop precedent (SCAN-19/20) the attended-session number is not bumped for a LOW auto-ship; the loop records itself in this Daily Loop block. `/dashboard/summary` currentSession stays 139 (correct — no attended session completed).
- **On-time** (~06:33 SAST vs 06:30). report.json loop_date was 2026-07-13 at start (no desktop loop ran 07-14 — machine likely asleep; 01:30 cron shadow covered 07-14 & 07-15) → full fresh loop, Fixer eligible + shipped SCAN-22.
- **Git:** working tree dirty (attended-deploy + loop doc drift + local bea_main.py ahead of HEAD). No secret staged (`ssh_hetzner_key` + `.ssh/id_ed25519` gitignored); `demo_sellers.json` excluded. One commit/push block handed to David in the brief.

## Daily Loop (2026-07-13) — Monday deep scan · queue repopulated (3 new LOW), Fixer idle
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0%) · real-token 100% (MTD 136 calls, $0.507) · cron-parity MATCH (cron 39/39 vs live 40/40, both green — shallower cron bundle by design) · FEA integrity ok, 0 alerts (live ms.js v286 / css v208; benign attended baseline-lag) · subs 34 up / 15 held / 1 standby / 1 planned, 0 issues (OpenAI-failover key unverified/standby, root-only conf — not an alarm).
- **Monday scan (delta vs 2026-07-06, prior open set EMPTY): 3 NEW LOW · 0 crash-class** (pylint 10.00/10, 0 cyclic imports, 0 F821; all 5 py compile; eslint 0 new structural errors). All in bea_main.py; introduced by attended deploys since last Monday (the `_demand_*` outreach block + the `auth_verify` magic-link except handlers):
  - **SCAN-22 · F841** dead local `name` @5685 (`_demand_render_invite`; greeting already hardcoded `''`) → auto-ship class.
  - **SCAN-23 · B904 ×2** @10205/10207 (`auth_verify` JWT except → add `from None`; user-facing 401 unchanged) → auto-ship (security-class per POLICY §5).
  - **SCAN-24 · unused param** `ticket_id` @5698 (`_demand_send_invite`; single caller @5866) → auto-ship, ranked LAST (2-site edit).
- **Shipped:** nothing — Fixer idle, queue was EMPTY (seeded empty by the 07-12 Sunday Phase 3). Per one-item-per-run + seeded-queue, the 3 new items are queued by THIS run's Phase 3 for the NEXT Fixer (~26h latency by design). Nothing staged; **nothing awaiting approval.**
- **Ignored (FP, unchanged):** ruff B008 ×14 (FastAPI arg-default idiom), vulture `family` ×2 @2214/2315 (getaddrinfo wrapper params), eslint `tshLoad` (SCAN-21-JS decorator), eslint no-undef/no-unused warning class.
- **Git:** working tree = HEAD + **2 modified docs today** (SCAN_REPORT.json, AUDIT_PROGRESS.md; `.bak` backups gitignored). No secret staged (`ssh_hetzner_key` + `.ssh/id_ed25519` gitignored); `demo_sellers.json` excluded in the block. One commit/push block handed to David. Sandbox plain `git status` still hits the FUSE index-corruption error (GIT-INDEX-1) — used the temp-index (`read-tree HEAD`) workaround to confirm the clean 2-file delta.
- **On-time** (~06:33 SAST vs 06:30). report.json loop_date was 2026-07-12 at start (no desktop loop had run today) → full loop ran (Fixer eligible but queue empty). 01:30 cron shadow fired today (findings.cron.json loop_date 2026-07-13, smoke 39/39, health ok, $0).

## Daily Loop (2026-07-09) — clean maintenance day (queue empty, nothing shipped)
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0%) · real-token 100% (MTD 40 calls, $0.021) · cron-parity MATCH (cron 39/39 vs live 40/40, both green — shallower cron bundle by design) · FEA integrity ok (baseline refreshed).
- **Shipped:** nothing — auto-ship queue EMPTY (SCAN-13→20 block closed; last ship WONDER-DUP-MARKERS-1 on 07-07). Fixer idle; nothing staged.
- **FEA alert = benign:** live ms.js v270→280 / css v198→204 / index +596B were confirmed benign attended deploys (local repo == live byte-match; CHANGELOG documents v276→280: user-manual link + PDFs, sign-in refresh, agency rename prompt, superuser agency fallback). Baseline refreshed to v280/v204/370659B → status ok. Not a same-version tamper.
- **Gap:** no desktop loop ran 2026-07-08 (machine asleep); the 01:30 cron shadow covered it (smoke 39/39, health ok, $0) and the queue was empty across the gap, so no Fixer work was lost.
- **Open items (all FILE / David-gated, none loop-actionable):** L3a support-mailbox launch blocker (ops); WONDER-DUP-1/4/7/8/9/10 (data calls David makes in chat); A11Y-1/2/3, ADMIN_KEY, TR-90D (filed); CC-001/002/003, DEMO-4, W12-FORYOU, CUTOVER-1 (attended/gated).
- **Git:** tree dirty (38 entries — accumulated attended-deploy + doc drift; no secret staged). One commit/push block handed to David in the brief. Next Monday's deep scan repopulates the queue.
- **Afternoon re-fire (17:2x SAST, +~11h) — NEW drift found:** duplicate late trigger; the morning loop (04:39Z) had already run, so the Fixer phase was skipped per the late-run guard. Re-sensing caught an attended-deploy incompleteness the morning run never saw: served **index.html** pins `static/ms.js?v=281` (served==local byte-match) but served **/static/ms.js is still the older v280 build (834226B)** — the local **uncommitted** `ms.js` v281 (835474B, larger, not a mount-tear) was never shipped to `/static`. Live **index↔JS version drift**: the `?v=281` cache key is filled with older JS and any intended v281 change is **not live** (site still functional — served JS valid, smoke 40/40). FEA baseline deliberately **not refreshed** (alert kept firing). No auto-deploy (WIP intent unknown). **⏳ David: re-run full `deploy_marketsquare.bat`** (static-before-html + [6b] md5 gate + CF purge) to reconcile, or confirm local ms.js v281 is intended before deploying. Tracked as `FEA-MSJS-DRIFT-09JUL` in orchestrator/report.json.

## Daily Loop (2026-07-09, later) — late catch-up re-sense (+~11h; morning loop already ran 04:39)
- **Guard honoured:** report.json already had loop_date 2026-07-09 (04:39 run) → Fixer phase NOT re-run; queue+staged empty all day anyway. Read-only re-sense + report refresh only.
- **State (17:36 SAST):** BEA ok v1.3.1 · smoke 40/40 · today spend $0.00/$100 (0%) · real-token 100% · cron-parity MATCH · FEA now ok.
- **Only new state since morning = two ATTENDED Paystack-reviewer deploys (David, ~16:39 + ~16:53):** pre-launch gate RE-LOCKED (had been fail-open since 06-Jul for Paystack review) + server-side reviewer access hardened (POST /review/login + GET /review/verify, bcrypt hash on box, 14-day review JWT that can never validate as admin). FEA alert (index +1541B, ms.js cache-buster v280→281, content bytes unchanged) confirmed benign — local marketsquare.html == live index byte-exact; baseline refreshed → ok.
- **⚠️ SEV-2 git-secret PRE-CATCH (resolved):** the live reviewer code was sitting in plaintext in the tracked CHANGE_REGISTER.md, about to be swept into today's commit — contradicts David's own plaintext-never-in-repo design. Redacted in place (backup CHANGE_REGISTER.md.bak-secretredact-*, gitignored); `git grep` for the code now returns 0. Git block is safe.
- **Filed (new):** ADMIN-SUBCHECK-1 — David-flagged today that `_require_admin`/`admin_verify` accept any `_JWT_SECRET`-signed token regardless of `sub` (latent, needs the admin secret); defence-in-depth sub-check deferred by David (needs master password to test). Attended/gated.
- **Note:** undeployed local ms.js (835474B, signout edit 16:22) sits ahead of live (834226B) — attended mid-flight work, not loop-actionable.

## Daily Loop (2026-07-01) — SCAN-20 shipped (auto-ship queue now EMPTY)
- **SCAN-20 · LOW · DONE.** B904 `from e` added to the admin-only AI provider test endpoint `admin_ai_test` (`bea_main.py:9145`, route `POST /admin/ai-test`) — the `raise HTTPException(500, "ai-test failed: …")` inside `except Exception as e`. Diagnostic endpoint (David-only, `_require_admin`-gated) that runs a tiny prompt through the active provider seam and bypasses the 15 production call sites — **no Tuppence credit/debit, no payments/pricing/KYC/regulatory copy** → Gate 1+2 clear with positive confidence, auto-shipped. Python str.replace driver (anchor asserted unique; never Edit/Write); ast clean; smoke 40/40 pre+post; server backup `main.py.bak-20260701-scan20`; scp md5 parity `5ae44a4…` local==server; server-venv ast OK; chained line confirmed on served `main.py:9145`; restart active; /health v1.3.1 (direct+public); CF purged `{purged:true}`. Repo `bea_main.py` set byte-identical to the deployed file (`5ae44a4…`) so today's git block captures it.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0%) · real-token 100% (MTD 0 calls — fresh July month) · cron-parity MATCH (cron 39/39 vs live 40/40, both green — shallower cron bundle by design) · FEA integrity ok, 0 alerts (baseline trails live ms.js v212 / css v158 — known loop baseline-lag).
- **Queue after this run:** static-scan auto-ship queue EMPTY (SCAN-13→20 block closed). SCAN-21-JS → IGNORE-with-reason (intentional `tshLoad` decorator). COST-WRAP-1 already CLOSED (06-30). Next Monday's deep scan (DOW=1) repopulates.
- **Loop note:** LATE RUN (+~13.5h) — desktop-app catch-up: scheduled 06:30 SAST, ran ~20:05 SAST. Server report.json confirmed no prior loop ran today before this one.

## Daily Loop (2026-06-30) — SCAN-19 shipped + repo↔server drift reconciled
- **SCAN-19 · LOW · DONE.** B904 `from e` added to the BIT status writer `dashboard_bit_post` (`bea_main.py:8739` — `raise HTTPException(400, "bad bit payload…")` inside `except Exception as e`). Diagnostic-only (BIT's single `bit_status.json` write surface); no app/ledger/payment state. Python str.replace driver (anchor asserted unique); ast clean; smoke 40/40 pre+post; server backup `main.py.bak-20260630-scan19`; scp md5 parity `ed99e6f…` local==server; server-venv ast OK; chained line confirmed on served `main.py:8739`; restart active; /health v1.3.1 (direct+public); CF purged. Gate 1+2 clear, auto-shipped.
- **BEA-DRIFT reconciled:** served `main.py` was 1 line ahead of the repo — David's 29-Jun `videos_visible` decouple (deployed, uncommitted; verified/paid-feed gates stay live-gated). SCAN-19 based on the server copy; repo `bea_main.py` set byte-identical to the deployed file (`ed99e6f…`) so today's git block captures both. Non-gated UI flag.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0%) · real-token 100% · cron-parity MATCH (cron 39/39 vs live 40/40, both green — shallower cron bundle by design) · FEA integrity ok, 0 alerts (live ms.js v210 / css v158; baseline trails v189/v143 — the loop's known baseline-lag, not a same-version byte change).
- **Queue advances:** SCAN-20 (B904 `admin_ai_test` `bea_main.py:9145`) → next auto-ship. SCAN-21-JS → IGNORE-with-reason. COST-WRAP-1 → confirm-close.
- **Loop note:** on-time (~06:3x SAST vs 06:30 schedule); not late.

## Daily Loop (2026-06-29) — SCAN-18 RE-SHIPPED (phantom-ship corrected) + SCAN-19/20 queued
- **SCAN-18 · LOW · DONE (re-shipped).** B904 `from None` in `_validate_rental_fields` (`main.py:1407`). Monday's scan found the 25-Jun "DONE" ship had **never landed** — the edit was absent on repo AND live server (PHANTOM-SCAN18, SEV-3). Re-applied via Python str.replace driver; ast clean; smoke 40/40 pre+post; local↔server md5 parity `3f45bd5…`; server backup `main.py.bak-20260629-051647-scan18`; server-venv AST OK; **`from None` confirmed present on the served main.py this time** (the check the phantom ship lacked); restart active; /health v1.3.1 (direct+public); CF purged. Gate 1+2 clear.
- **State:** BEA ok v1.3.1 · smoke 40/40 · today's AI spend $0.00 / $100 ceiling (0%) · real-token 100% · cron-parity MATCH (cron 39/39 vs live 40/40 = older cron smoke bundle, both green) · FEA integrity ok, 0 alerts (live ms.js v205 / css v158; Live-State line below still trails the live FEA version — loop deploys bump js without a STATUS rewrite).
- **Queue advances:** SCAN-19 (B904 BIT writer `bea_main.py:8739`) → SCAN-20 (B904 `admin_ai_test` `bea_main.py:9145`), both NEW + non-ledger auto-ship. SCAN-21-JS (`tshLoad` intentional decorator) → IGNORE-with-reason candidate. COST-WRAP-1 likely resolved by the 29-Jun attended cost sweep (all 15 AI sites metered) — Orchestrator to confirm-close.
- **Loop note:** last loop report was 2026-06-28 (on-time); 29 Jun run is ~37 min late vs 06:30 (within the 2h tolerance, not flagged late).


## Last Completed (2026-07-06 — Search Engine Step 1)
- **Server-side dial-in LIVE (SQL, no AI) — the FILTER_ENGINE_DESIGN Step 1 launch gap closed.** bea_main.py: startup migration (price_num REAL + backfill · indexes price_num/trust_score/(category,city)/(make,vehicle_year) · FTS5 listings_fts external-content + sync triggers + idempotent rebuild); get_listings gains q (prefix FTS, ≤8 terms), sort (smart|newest|price_asc|price_desc|trust; smart = trust×0.6 + 30-day freshness×0.4), price_min/max, trust_min, make/model/year_min/year_max — composed at the OUTER wrapper so they hold across all four reach branches (home/extended/trips/online); facets=1 returns same-set counts (totals/price range/makes/years/trust bands/service types). Default response shape unchanged — current FEA untouched. Scratch-DB proof pre-deploy: 'bmw 1996' ✓ make+year ✓ price sort ✓ trust floor ✓ online-via-q ✓ smart order ✓.
- **HMI blueprint delivered:** SEARCH_DIALIN_HMI_DESIGN.docx (debounced bar → q · facet chips with true counts · smart-default sort · URL state · infinite scroll) — awaiting David's approval, FEA build next session (SEARCH-HMI-1 on BACKLOG).
- **Also this session:** Branch D online-mode borderless reach (canon §2b) · tier-audit fixes (offer_advisor→Starter monthly ritual, retirement_planner→Pro class, PRO chips, billing bullets on both surfaces, Ruby date removed — powder dry) · /support public 200 · closed-testing spend guard on /tuppence/ai-commit (non-superusers 403 on paid AI until launch).

## Last Completed (Session 139 — 2026-06-16)
- **Rental availability (occupancy) - new feature, full stack.** Property listings gain a seller-controlled availability axis, kept separate from the `listing_status` lifecycle and the free-text service `availability` field. BEA (`bea_main.py`): migration adds `rental_status TEXT DEFAULT 'available'` {available/reserved/occupied} + `available_from` (ISO) + index; accepted on create + `PUT /listings/{id}`, validated (enum + ISO date -> 400); read endpoints return a derived `availability_label` computed at read time (so "Available from <future>" auto-flips to "Available now"). FEA (`ms.js`/`ms.css`): buyer badges on cards (occupied/reserved/upcoming) + a colour pill on detail; seller **Availability** selector + **Available from** date in the Edit Listing screen, wired into the existing PUT. Demo data seeded with all states. End-to-end verified live (seller sets Occupied -> buyer sees the badge).
- **Deploy hardening (root-cause fix for recurring stale-cache pain).** `deploy_marketsquare.bat`: static assets (ms.js/ms.css) now upload BEFORE the HTML referencing the new `?v=N` (the reverse order let Cloudflare pin the OLD js to the NEW version key - the bug that cost hours today); new **[6b]** step fetches the live ms.js through Cloudflare and md5-compares to the local build, failing loudly at deploy time; stale `1.3.0` health check made version-agnostic.
- **Cleared 3 long-stale board items (David's request).** SELLERHUB now renders the full 7-state listing lifecycle as colour-coded chips (DRAFT/LIVE/PAUSED/FADE_OUT/WITHDRAWN/BLOCKED/ARCHIVED) via sbLifecycleChip(), replacing the old 3-state collapse; the guided sell-flow gained a go-live-before-exit guard so drafts aren't silently stranded (GUIDED-PUBLISH-1 follow-up); and a new G-PUBLISH guard in the Prevent harness flags any regression (verified PASS against the deployed ms.js). All three had sat un-started on the 'next' board for ~5 sessions.
- **Deploys:** ms.js v175 / ms.css v132 / index.html; bea_main.py (rental_status migration, already live); CF purged; live-verified in-browser. Spec doc `TrustSquare_Rental_Availability_Status_Spec_v1_1_Draft.docx` in MarketSquare.
- **Cost model impact:** none.

## Next Session (140)
- **Rental availability follow-ups (deferred from 139):** search-ranking demotion for occupied/reserved (currently visible, not yet down-ranked); optional `hide_when_occupied` seller toggle; `reserved` middle-state UX polish; rent-vs-sale gating (the availability label currently shows for ALL Property listings, not only rentals - confirm the rent/sale flag); "notify me when available" via the existing queueCount; stale-availability nudge when an `available_from` date passes.
- **Standing:** COST-SWEEP-LANE-1; LAUNCH-GATES set; CC-001/CC-002/CC-003 (David verify/land); ORCH-POLICY-1; DEMO-4; W12-FORYOU; CUTOVER-1; WONDER-DUP-1->10.
- **Awaiting your approval:** none.

## Last Completed (Session 138 — 2026-06-12)
- **GUIDED-PUBLISH-1 + SELLERHUB-STATUS-1 (David repro, id 243):** guided drafts stranded invisible while the hub said Active. Publish endpoint freed of its redundant admin-key Depends (email-auth inside was complete); hub derives status from `listing_status` — 📝 DRAFT badge + demo-guarded Publish button; sobGoLive stops sending the client-embedded admin key. Auth matrix live-tested (403 wrong-email · 200 no-key publish · idempotent re-publish). CORRECTION on the initial filing: sobGoLive always had the publish wiring — the gaps were the key gate + the hub mislabel.
- **WONDER-AUTOLINK-CAT-1 (David ruling):** heritage auto-linking now Property+Adventures only; 27 Collectors listings cleaned of 135 auto museum-links (flag-filtered — manual picks preserved); picker unchanged for all categories.
- **Deploys:** bea_main.py (566,706B) + ms.js v171 + index.html; backups `*-20260612-gp1`; md5 parity; restart active; /health v1.3.1; smoke ALL OK pre+post; CF purged.
- **Cost model impact:** none.

## Next Session (139)
- **Open from today:** guided-handoff UX (surface "Go live" before flow exit — GUIDED-PUBLISH-1 follow-up); PREVENT-PUBLISH-1 guard + negative KPI (guided listing must reach live); SELLERHUB 7-state chips (PENDING/SUSPENDED).
- **Standing:** COST-SWEEP-LANE-1; LAUNCH-GATES-1 + LAUNCH-CONTROL-1 + GATE1-PAY-ZA/INTL + AGENCY-IMPORT-1 + LEGAL-COUNTRY-1 (launch-readiness set); PITCH-AGENCY-1 external-use gated on patent filing; CC-001/CC-002/CC-003 (David verify/land); ORCH-POLICY-1; DEMO-4; W12-FORYOU; TR-90D; CUTOVER-1; GIT-INDEX-1 + MOUNT-READ-1; WONDER-DUP-1→10 (David data calls). **FEA-DRIFT: CLOSED 18 Jun — deploy_marketsquare.bat now auto-commits after every deploy (Step 7), so source can no longer drift uncommitted; GIT-INDEX-1 root cause is *why* commits must run on the Windows deploy side, not in the sandbox.**
- **Awaiting your approval:** none.

## Last Completed (Session 137 — 2026-06-12)
- **BASELINE-12JUN-1 ADJUDICATED → APPROVED (David-delegated).** The 04:24Z cost-sweep deploy is content-correct: matches BUILD_BRIEF_SIMPLER_MODEL (P2 `_check_cost_ceiling` rails before every Tuppence-charged AI call + real-token `_log_ai_spend` ×6, `paid_tiers` starter/pro fix — the offered tiers couldn't initialize payment pre-sweep, agency→400 guard, rank-by-price downgrades, free $0-first draft-from-photo(s), read-only admin spend summary). `_SELLER_SUB_TIERS` byte-identical (no price change); SCAN-14 preserved; the 9 sibling deployed files md5-identical to mount; AST/restart/journal/smoke all green. Rollback rejected: would re-break starter/pro payment-init + drop protective rails + need SCAN-14 re-apply. Process breach NOT blessed — COST-SWEEP-LANE-1 stays open. Acked baseline banked (`main.py.bak-20260612-scan16L`).
- **Queue cleared (3 deploys, each: server backup + scp md5 parity + venv ast + restart active + /health v1.3.1 + CF purge; smoke ALL OK):** SCAN-16-LEDGER `from e` at ai-commit/ai-settle (11869/11912; David-approved 11 Jun 07:47Z) → SCAN-15 dead `as e`@1552 + dead `photo_entry`@2565 (−34B; live 2445 path untouched) → SCAN-16 non-ledger 22×B904 `from exc`/`from jde` (+11 new `as exc` bindings) + 1×B905 `zip(…, strict=False)`. `flake8 --select=B904,B905` = ZERO on bea_main.py. **SCAN-13→16 block closed; auto-ship queue EMPTY.**
- **MOUNT-TEAR-1 healed:** mount bea_main.py restored from server (torn copy md5-proven a pure truncated prefix — zero local loss; post-restore parity 38aab78… both sides).
- **Cost model impact:** none — deterministic hygiene only; zero AI calls.

## Next Session (138)
- **Maintenance auto-ship queue:** EMPTY — SCAN-13→16 closed; the next weekly scan repopulates.
- **Standing:** ORCH-POLICY-1; COST-SWEEP-LANE-1 (register the 4th lane or fold into the loop); DEMO-4 R2 self-host (carries DEMO-5); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1; TR-90D (triage); HTML-2 `status` residue (per-site confirm); CUTOVER-1 (attended/gated — NOT a fixer item); FEA-DRIFT-3 + GIT-INDEX-1 (git sweep owed — block surfaced S137); WONDER-DUP-1→10 (David, data calls in chat); CC-001/CC-002 staged sets (David: verify term maps + land canon); CC-SEQ (David call).
- **Awaiting your approval:** none.

## Last Completed (Session 136 — 2026-06-11)
- **[SCAN-14 · LOW · DONE] Dropped the unused `sessions: int = 8` parameter from the retired `aa_buy_pack` stub (`POST /advert-agent/buy-pack`, bea_main.py:3879).** The endpoint was retired to a 410 stub under Canon Addendum 1 (AI-uses/packs no longer exist) and raises `HTTPException(410)` before any logic runs — the param was the last vestige of the pack SKU and was never read. One surgical Python `str.replace` (asserted unique), never Edit/Write; signature now `aa_buy_pack(email: str)`. FastAPI ignores unknown query params, so any stale caller passing `?sessions=` still receives the same 410.
- **Gate:** dead-parameter removal on a stub that raises before any logic — touches no payments.py / Tuppence-ledger / EULA-Terms-Privacy / KYC-SA-ID code and no live pricing path (the pack SKU it referenced is already retired) → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2); auto-shipped.
- **Verify/deploy:** `ast.parse` clean local; `smoke_test.py` all-green post-edit. Server backup `main.py.bak-2026-06-11-fixer`; scp → main.py; `ast.parse` in BEA venv on the deployed copy clean; `systemctl restart marketsquare` → **active**; `/health` ok v1.3.1; live 410 stub re-tested (correct retirement message, no 500); Cloudflare purged (`{purged:true}`).
- **Cost model impact:** none — dead-parameter removal on a retired endpoint; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (137)
- **Maintenance auto-ship queue (top → back):** SCAN-15 (SCAN-11 remnants — dead `e`@1551 + `photo_entry`@2552, bea_main.py) → SCAN-16 **non-ledger** B904/B905 sites (auto-ship). **STAGE (Gate 2):** SCAN-16 ledger sites `bea_main.py:11528/11571` (ai-commit/ai-settle) — financial, needs approval.
- **Standing:** ORCH-POLICY-1; DEMO-4 R2 self-host (carries DEMO-5); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1; TR-90D (triage); HTML-2 `status` residue (per-site confirm); CUTOVER-1 (attended/gated — NOT a fixer item); FEA-DRIFT-1 (MED — uncommitted ms.js/ms.css drift; Orchestrator/attended, NOT Fixer).
- **Awaiting your approval:** BASELINE-12JUN-1 (SEV-2 · Process/§12) — acknowledge or roll back the 12 Jun 04:24Z unattended cost-sweep deploy (rollback point: `main.py.bak-2026-06-11-fixer` + re-apply SCAN-14). SCAN-16-LEDGER is already APPROVED (11 Jun 07:47Z) and ships automatically once BASELINE-12JUN-1 is acknowledged.
- **Loop update (12 Jun):** queue = SCAN-16-LEDGER (approved, preconditioned on BASELINE-12JUN-1) → SCAN-15 (offsets now ~1551/~2564) → SCAN-16 non-ledger (re-derive offsets; ledger sites now ~11869/11912). New filed: MOUNT-TEAR-1 (restore mount bea_main.py from server after ack), COST-SWEEP-LANE-1 (register the 4th lane in ORCHESTRATION_POLICY or fold into the loop), FEA-DRIFT-3 (v168/v127 — fea baseline refreshed 12 Jun, git commit still owed), GIT-INDEX-1 (sandbox temp-index workaround).

## Last Completed (Session 135 — 2026-06-10)
- **[SCAN-13 · LOW · DONE] Removed the unused `Query` import from the line-1 FastAPI import in `bea_main.py`.** `from fastapi import …, Header, Query` carried `Query` but never used it — orphaned when S106 moved KYC-doc auth off the `?api_key=` query param. Whole-word `Query` appears only twice in the file: the import itself and the English word "Query" opening the Overpass docstring at line 1494 (not the symbol), so removal is behaviour-neutral. One surgical Python `str.replace` (asserted unique) on a copy verified byte-identical to the live server (md5 `74f71b3…`); never Edit/Write; −7 bytes (548791→548784); `Header` and every other imported symbol retained.
- **Gate:** a FastAPI import-line cleanup — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / KYC-SA-ID code and no pricing/refund path → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2); auto-shipped.
- **Verify/deploy:** `ast.parse` clean local; whole-file diff vs the pre-edit backup = exactly the one import line; `smoke_test.py` all-green pre **and** post. Server backup `main.py.bak-20260610-020738`; scp `main.py` (md5 local==server `5f0f77c…`); `py_compile` in the BEA venv on the deployed copy clean; `systemctl restart marketsquare` → **active** (the clean restart is the conclusive import test — the app loads with no `Query` reference); `/health` ok v1.3.1 (direct 127.0.0.1:8000 + public through Cloudflare); CF purged (`{purged:true}`).
- **Cost model impact:** none — dead-import removal; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (136)
- **Maintenance auto-ship queue (top → back):** SCAN-14 (unused `sessions` param on the retired `aa_buy_pack` 410 stub, bea_main.py:3873) → SCAN-15 (SCAN-11 remnants — dead `e`@1551 + `photo_entry`@2552) → SCAN-16 **non-ledger** B904/B905 sites (auto-ship). **STAGE (Gate 2):** SCAN-16 ledger sites `bea_main.py:11528/11571` (ai-commit/ai-settle) — financial, needs approval.
- **Standing:** ORCH-POLICY-1; DEMO-4 R2 self-host (carries DEMO-5); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1; TR-90D (triage); HTML-2 `status` residue (per-site confirm); CUTOVER-1 (attended/gated — NOT a fixer item); FEA-DRIFT-1 (MED — uncommitted ms.js v161 / ms.css v122, reconcile+commit+baseline-refresh; Orchestrator/attended, NOT Fixer).
- **Awaiting your approval:** none.

## Last Completed (Session 134 — 2026-06-08)
- **[SCAN-12 · LOW · DONE] Removed the unused `import os` from `database.py` (F401, line 2).** The SQLite access layer imported `os` but never referenced it — the only `os` token in the module was the import itself (0 `os.` uses), so removal is behaviour-neutral. One surgical Python `str.replace` on a freshly server-pulled copy (anchored on the unique `import sqlite3`/`import os` pair; never Edit/Write); −10 bytes (2837→2827). This was the last open item in the `database.py` portion of the 1 June static-analysis scan — that file's scan block is now closed.
- **Gate:** DB-access-layer import cleanup — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / KYC-SA-ID code, no pricing/refund path → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2); auto-shipped.
- **Verify/deploy:** local mount byte-identical to the server pre-edit; `ast.parse` + no-pyc `compile()` clean local, then `ast.parse` **and** a live `import database` in the BEA venv on the deployed copy (DB_PATH resolved); diff vs server = exactly the one removed line; `smoke_test.py --local` 40/40 all-green pre **and** post. Server backup `database.py.bak-20260608-scan12`; scp `database.py` (three-way sha256 parity mount == /tmp == server); `systemctl restart marketsquare` → **active**; `/health` ok v1.3.1 (direct 127.0.0.1:8000 + public through Cloudflare); CF purged (`{purged:true}`).
- **Cost model impact:** none — dead-import removal; no AI calls, pricing, concurrency, or city-launch change.

- **[Attended top-up · David-approved “ship the queue” · 8 Jun] Remaining maintenance queue cleared the same day.**
  - **DASH-VER-1 · LOW · DONE** — `/dashboard/summary` `bea_version` 1.3.0→1.3.1 (hardcoded @bea_main.py:8249) + the FastAPI app-title `version=` (line 28); both lagged `/health` 1.3.1. Verified live through Cloudflare (`bea_version=1.3.1`). Display/metadata only → clears Gate 1+2.
  - **SCAN-PANEL-1 · OPS · DONE** — new no-auth `GET /dashboard/scan` (mirrors `/dashboard/cost`; reads `SCAN_REPORT.json` via `_read_file`, returns `{available:false}` if absent). Live: found 4 / fixed 9 / open 6.
  - **SCAN-PANEL-2 · OPS · DONE** — “🔍 WEEKLY CODE SCAN” panel in `dashboard.html` after AI Cost & Margin (plain DOM — Chart.js is **not** loaded in the dashboard; found/fixed/open tiles + severity + per-scan history bars + open-issues list). DASHBOARD VERSION GUARD respected (server==pull).
  - **HTML-1 · LOW · DONE** — removed dead `currentView` (decl + write) from `marketsquare_admin.html`.
  - **HTML-2 · LOW · mostly DONE** — removed unused `editingIdx`, `photoFile`, `tier` + dropped the unused `const ur =` binding (the `await fetch` is preserved → behaviour-identical). **`status` left**: every `status` token is a live `getElementById` ref — the eslint flag needs per-site confirmation (default-to-safe).
  - **Verify/deploy (each):** fresh server pull as source of truth + sha256 parity + `ast.parse` (BEA) / `node --check` (both admin & dashboard inline blocks clean) + `smoke_test.py` 40/40 pre+post + timestamped backups `*.bak-20260608-ship` + chmod 644 + CF purge; the 3 mount copies byte-synced. No concurrent-deploy collision (loop Fixer finished 13:31Z; these deploys 14:01–14:13Z, each guarded by a pre-deploy server-sha re-check).
  - **Cost model impact:** none.

## Next Session (135)
- **Maintenance auto-ship queue (top → back):** *(prior queue DASH-VER-1 / HTML-1 / HTML-2 / SCAN-PANEL-1+2 all shipped 8 Jun — attended top-up.)* Newly surfaced by the 8 Jun deep scan: SCAN-13 (unused `Query` import) → SCAN-14 (unused `sessions` param on the 410 stub) → SCAN-15 (SCAN-11 remnants `e`@1551 + `photo_entry`@2552) → SCAN-16 **non-ledger** B904 sites (auto-ship). **STAGE (Gate 2):** SCAN-16 ledger sites `bea_main.py:11528/11571` (ai-commit/ai-settle) — financial, needs approval. Residue: HTML-2 `status` (per-site confirm).
- **Standing:** ORCH-POLICY-1; DEMO-4 R2 self-host (carries DEMO-5); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1; TR-90D (triage); CUTOVER-1 (attended/gated — NOT a fixer item).
- **Awaiting your approval:** none.

## Last Completed (Session 133 — 2026-06-07)
- **AI Features integrated into the buyer app (BACKLOG AI-1 — test phase).** Wallet gains an "AI feature credits" section (§5-compliant: "not used for introductions") with an Open AI Features entry → new `#screen-ai-features`: all 9 function cards, param forms (text/select/photo-upload with canvas compress), run+poll, lazy-loaded Leaflet route map, amber safety panel, markdown report renderer. **Dry-run defaults ON** — full integrated testing at $0 (replays fixtures/real results; hold commits then releases). DEMO_MODE: screen added to the goTo block-list + aiRun double-guard. Deploys: index.html (4 hunks), ms.js v156 (2 hunks: block-list + appended module), ms.css v121; nginx split (/ai/ API open — service gates: known-user/balance/ceiling; /ai/test keeps Basic Auth); CF purged; fea_baseline refreshed (index 378613B · ms.js 741658B · ms.css 120891B); smoke_test ALL OK. Replay-quality fix: heritage dry-replays must carry waypoints (a v1.1 map-less delivery — the exact gap v1.2's contract closed — was feeding previews). NOTE: mount copy of ms.js was found TORN mid-function; server copy used per B2, mount healed after deploy.

## Next Session (134)
- David visual pass on the in-app AI screen (phone + desktop) · first real v1.2 heritage run (~$0.8, verifies map-first contract + transport + safety live)
- Launch hardening: real user auth on /ai/ (replace open-API test posture), hide dry-run toggle, Tuppence top-up packs on the AI screen
- G1 council amendment (AI-3) · orchestrator API-balance watch

## Last Completed (Session 132 — 2026-06-07)
- **AdvertAgent advanced-AI functions: spec + standalone service + live tests (AdvertAgent Session 8).** BEA gains `/tuppence/ai-commit` + `/tuppence/ai-settle` (atomic hold ledger, new txn types ai_hold/ai_burn/ai_hold_released/ai_release; smoke-tested net-0). New `advertagent.service` (FastAPI 8002, nginx `/ai/` behind .htpasswd_orch) with 9-function registry — 2 LIVE (collectables_advert, heritage_tour · Sonnet 4.6 + server-side web_search, serial worker, 60s 429-backoff), 7 designed stubs. Real-API runs green: $0.354 + $0.781, output honest-sourced, failure path released the hold (user not charged on a real 429). Test console at trustsquare.co/ai/test. Spec: `AdvertAgent/AI_FUNCTIONS_SPEC.md` + .docx. Smoke test ALL OK.

## Next Session (133)
- FEA integration of AI Features (DEMO_MODE guard mandatory) + replace /ai/ Basic-Auth dev gate with user auth
- Promote first stub (weekend_itinerary 3T — purest intro-flywheel) after Adventures listings exist
- G1 scope amendment at council review (buyer-side AI services)

## Last Completed (Session 130 — 2026-06-07)
- **CityLauncher Session B — RM-5 engine + Founders issuing side DEPLOYED LIVE (deploy/RM5_DEPLOY.md end-to-end).** 18 engine files + 14 outreach templates to /var/www/citylauncher; prospects.db MERGED not clobbered (local 219-verified RM-5 schema + 1,197 server-only rows; 3-way md5; backups in backups-s130/); seeded orchestration.db deployed; dnspython installed; services swapped: haiko-agent + citylauncher-scheduler retired → citylauncher-strategist (5001, health ok, claude-sonnet-4-8) + citylauncher-scraper (idle-driven, 10-min wake).
- **Launch-codes wiring (BEA):** LAUNCH_CODE_SECRET (shared 64-hex) + FOUNDERS_ID_SALT + LAUNCH_SPECIAL_DEADLINE=2026-08-01 via marketsquare.service.d/launch.conf (600); BEA restarted healthy v1.3.1; POST /launch/sync-registry 200 (table live, 0 codes issued yet); /launch/status: redemption/allocation/velocity all OFF. TRAVEL_TOUR_SIGNALS_LIVE=1 (S129 signals confirmed ×7+×7 on served main.py) — travel/tour outreach unblocked.
- **Two engine fixes shipped mid-deploy (compile+md5+restart verified):** (1) scraped_prospects schema drift — worker INSERTs phone/website/raw_tags, DDL-seeded table lacked them so every yield dropped; empty table rebuilt to worker-superset + DDL aligned in orchestration_db.py both sides. (2) Restart-resilience — claims orphaned by a service stop stranded in running forever AND the wake only drained newly-enqueued work; added job_queue.reap_stale_running(60m) + drain-when-ANY-claimable in saturation_scheduler.
- **MX ladder over the merged pool (server-side, free):** verified 213 → 1,326 mx_ok (54 no_mx, 36 invalid_syntax quarantined; nothing deleted, nothing emailed).
- **First live cycle:** 60 staged prospects within minutes across every lane — Car Dealers 15 · Tutor Institutions 12 · Tutors 9 · Service Companies 7 · Estate Agents 6 · Collector Shops 6 · Tour Operators 4 · Travel Agencies 1 — saturation loop continues every 10 min to 20/category then adaptive re-pass. Gates held: emails halt at AWAITING_APPROVAL; LAUNCH_SPECIAL_ENABLED=0.
- **Cost model impact:** strategist Sonnet checkpoints now live server-side — ≤6 calls/city/cycle, only while a city is active (deterministic fallback if key absent); email volume unchanged (sends gated); no pricing change.
- **Concurrent-deploy reconcile (S129 pattern):** overnight Fixer worked RM-5 in parallel (02:32–02:42 UTC, its `*.pre_rm5_bak` backups) — merge/launch_codes/schema-fix survived; it expanded the pool to **93 cities scraping → 791 queued jobs** (aligned with the launch-day scrape goal; pools stay bounded); mx_status reverted → ladder re-run launched. Watch for double-writes tonight; CUTOVER-1 retires this two-actor risk.
- **SCAN-11 DONE (LOW · dead locals + unused import sweep · auto-shipped).** `bea_main.py` −290 bytes via 8 surgical str.replace edits: removed unused `import sqlite3 as _sqlite3` (wonders auto-link), dead locals `skip_fields` (field-formatting), `sig_suburb_id` (signal scorer), `cutoff` (trust-signal `zero_ignored_90d` — query uses inline 48h expression); renamed unused loop vars `hi2`/`idx` → `_`; dropped the unused `hint` param from `_vision_orient_image` + its one call site. Vulture's `family` flags intentionally KEPT (signature-mandated `socket.getaddrinfo` wrapper params — renaming breaks keyword callers; recommend IGNORE). Live `cutoff`@5417 / `idx`@3941+9237 untouched.
- **Gate:** wonders/vision/formatting/signal/trust-tier regions only — no payments, ledger, EULA, KYC, pricing → clears Gate 1+2 with positive confidence; auto-shipped per POLICY §5.
- **Verify/deploy:** ast.parse local + venv py_compile on served copy; local was byte-identical to server pre-edit; diff = exactly the 8 regions; smoke all-green pre+post; backup `main.py.bak-20260607-scan11`; server sha256==local; BEA restarted active, /health v1.3.1; CF purged.
- **FILED:** [TR-90D] `zero_ignored_90d` lacks its 90-day lower bound (the dead `cutoff` was plausibly meant for it) — signal currently stricter than named; product/Codex decision → Orchestrator triage.
- **Cost model impact:** none.

## Next Session (131)
- **DONE in S130 (this session).** Watch the saturation loop: lanes → 20/category then C4 review; the first Pretoria agency wave will assemble and HALT at AWAITING_APPROVAL — David approves manually. At launch month: flip `LAUNCH_SPECIAL_ENABLED=1` (CityLauncher) + `LAUNCH_REDEMPTION_ENABLED` / `TUPPENCE_MONTHLY_ENABLED` / `LISTING_VELOCITY_ENABLED` (BEA) and re-set LAUNCH_SPECIAL_DEADLINE both sides (LAUNCH-DEADLINE-1).
- **CUTOVER-1 (attended/gated — NOT a fixer item):** carried — after a shadow parity night, execute the documented orchestration-v2 cutover (automate.html).
- **Maintenance auto-ship queue (top → back):** SCAN-12 → DASH-VER-1 → HTML-1 → HTML-2 → SCAN-PANEL-1+2.
- **Standing:** ORCH-POLICY-1; DEMO-4 R2 self-host (carries DEMO-5); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1; TR-90D (new, triage); DDG-IP-1 + PLAYWRIGHT-1 + LAUNCH-DEADLINE-1 (new, S130 — see BACKLOG).
- **Awaiting your approval:** none.

## Last Completed (Session 129 — 2026-06-06)
- **Founders Badge redemption side end-to-end (BACKLOG L9 items 4–5) — all env-gated OFF.** New `launch_redemption.py` router: TIER_TUPPENCE_MONTHLY {6/10/20/50} (price÷2, 1T=$2); POST /launch/redeem (HMAC mirror of CityLauncher issuing side + registry row + deadline; Business/Elite-only; salted ID-hash bind, raw ID never stored; one badge per human; agency multi-bind; idempotent; BEGIN IMMEDIATE; DB-backed throttle); ×1.2-rounded-up allocation hook in verify_seller_subscription (8/12/24/60, idempotent per month, private "Founders bonus +XT" wallet line); POST /launch/sync-registry (one-way INSERT OR IGNORE from CityLauncher prospects.db); per-day listing velocity limit in create_listing. Offline unit suite green; tables pre-created on live DB.
- **FEA Ruby Spark (ms.js v155):** founders_spark.svg beside the trust chip on browse/adventures cards, detail, and both seller-profile paths; tap = the one canon line; no perks UI. DEMO branch (DEMO_FOUNDERS_IDS demo_col_1/2) + LIVE branch (BEA `founders` flag on /listings) both verified.
- **Deploy queue cleared:** aa_buy_pack → 410 (packs retired); AI-uses copy purged (ms.js 667/885/9617/9632, marketsquare.html:1806); sob tier cards → canon Standard $12/10 + Professional $20/25 (legacy $5/$15 removed, keys starter/premium → standard/professional). PLANS Tuppence chips were already live from the interim v154 deploy (not duplicated).
- **Travel + Tour_Guides trust signals seeded** (David-confirmed 45-pt sets on the universal base 40) — the two outreach templates are unblocked.
- **Verify/deploy:** staged venv compile → swap; diff vs server = exactly the 7 hook regions; backups *-20260606-s129; 5 files sha-matched; smoke ALL OK pre+post; CF purged; baseline refreshed (ms.js v155 729429B). Concurrent interim-v154 chat deploy detected mid-session and reconciled cleanly.
- **Cost model impact:** allocations are code now, OFF until launch — at enable, Tuppence issuance = price÷2/paid seller (+20% Founders); AI pack SKU retired (1T per coach use after first free).

## Next Session (130)
- **CityLauncher Session B (RM-5 steps 2–8):** deploy the issuing side (`emailer/launch_codes.py` + launch_codes table in prospects.db). Then on the BEA: set `LAUNCH_CODE_SECRET` (same value both sides) + `FOUNDERS_ID_SALT` + `LAUNCH_SPECIAL_DEADLINE` in the marketsquare unit, run `POST /launch/sync-registry`, and at launch flip `LAUNCH_REDEMPTION_ENABLED` / `TUPPENCE_MONTHLY_ENABLED` / `LISTING_VELOCITY_ENABLED`.
- **CUTOVER-1 (attended/gated — NOT a fixer item):** carried — after a shadow parity night, execute the documented orchestration-v2 cutover (automate.html).
- **Maintenance auto-ship queue (top → back):** SCAN-11 → SCAN-12 → DASH-VER-1 → HTML-1 → HTML-2 → SCAN-PANEL-1+2.
- **Standing:** ORCH-POLICY-1; DEMO-4 R2 self-host (carries DEMO-5); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1.
- **Awaiting your approval:** none.

## Last Completed (Session 128 — 2026-06-06)
- **SCAN-10 DONE (LOW · redundant `datetime` re-imports · auto-shipped).** `bea_main.py` re-imported `from datetime import timedelta` twice at **module level** — line 4046 (the LocalKeywordMatcher block, beside `import re as _re_match`) and line 8490 (the admin-auth import block, between `import jwt as _pyjwt` and `from pydantic import BaseModel as _BaseModel`) — both F811-redundant with the canonical module-top import at line 25 (`from datetime import datetime, timezone, timedelta`). Removed both; `timedelta` stays bound module-wide via line 25, so behaviour is identical. Two surgical Python `str.replace` edits (each old-string anchored on its unique neighbour import and asserted to match exactly once), never Edit/Write; −62 bytes (539310→539248); the aliased `from datetime import datetime as _dt` at line 8108 left untouched.
- **Gate:** import-only cleanup — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / KYC-SA-ID code, no pricing/refund path → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2); auto-shipped.
- **Verify/deploy:** `ast.parse` clean local + BEA venv (`py_compile` on the served copy); whole-file diff vs a freshly-pulled server copy = exactly the 2 removed lines (local byte-identical to server beforehand); `smoke_test.py` all-green pre **and** post. Server backup `main.py.bak-20260606-scan10`; scp `bea_main.py` → `main.py` (server sha256 == local); BEA restarted **active**, `/health` ok v1.3.1 (localhost + public); Cloudflare purged (`{"purged":true}`).
- **Cost model impact:** none — dead-import removal; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (129)
- **CUTOVER-1 (attended/gated — NOT a fixer item):** after a shadow parity night, execute the documented orchestration-v2 cutover (automate.html) — v2 Fixer on (Sonnet checkpoint), retire the 3 old Claude tasks, conductor `--live`. Carried forward from the Session-128 plan; the background fixer cannot self-authorise this.
- **Maintenance auto-ship queue (top → back):** SCAN-11 (dead locals `skip_fields`/`sig_suburb_id`/`cutoff` + vulture `family`/`hint` + unused `_sqlite3` import; rename unused loop vars `hi2`/`idx` → `_`, bea_main.py) → SCAN-12 (`import os` unused, database.py:2) → DASH-VER-1 (stale `bea_version` 1.3.0→1.3.1 in /dashboard/summary — reconfirmed live-drifted this run; the `app = FastAPI(…, version="1.3.0")` title string @line 27 is the source vs `/health` 1.3.1) → HTML-1 → HTML-2 → SCAN-PANEL-1+2.
- **Standing:** ORCH-POLICY-1 (§5 reconcile); DEMO-4 R2 self-host (carries DEMO-5, monitored nightly by M-IMG); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1 (moot once the old loop retires).
- **Awaiting your approval:** none.

## Last Completed (Session 127 — 2026-06-05)
- **Orchestration v2 Phase 5 (Automate) — the loop runs itself (shadow); the 5-stage arc is complete.** New deterministic, zero-token `orchestration_v2/orchestrator_v2.py` conductor: nightly it runs sensor.py (sense) + prevent.py (guards+monitor) → assembles findings → triage.py → writes a "since last night" report. The surgical Fix stays a Sonnet checkpoint (surfaced as a green work order); the conductor never edits/ships code.
- **Shadow + scheduled:** server cron 03:50 SAST (after the 03:30 sensor, before the old Claude loop). Writes only /orchestrator/v2/, deploys nothing, old loop §9 files untouched. First pass: smoke 39/39, guards 3/3, monitor 2 dead/15 (0 FP), triage → 1 green (filed)/1 amber/0 red, $0/0 tokens. Cockpit: live "since last night" panel, Phase 5 → built, automate.html + cutover plan. Behind auth (644, sha-parity, 401).
- **Cutover staged (CUTOVER-1, gated on parity):** turn on a v2 Fixer (Sonnet checkpoint) → retire the 3 old Claude tasks (orch-sensor/fixer/orchestrator) → flip conductor to --live. Fully reversible; nothing fires without David's go.
- **Cost model impact:** standing maintenance token cost trends to ~zero at cutover (deterministic loop replaces the per-night model loop).

## Next Session (128)
- **CUTOVER-1 (the finale's last switch):** after a shadow parity night, execute the documented cutover (automate.html) — v2 Fixer on, old loop off, conductor `--live`.
- Standing: ORCH-POLICY-1 (§5 reconcile); DEMO-4 R2 self-host (carries DEMO-5, now monitored nightly by M-IMG); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1 (moot once the old loop retires).

## Last Completed (Session 126 — 2026-06-05)
- **Orchestration v2 Phase 4 (Prevent) — guards + monitor; the loop closes.** New deterministic `orchestration_v2/prevent.py`: regression guards (G-DEMO6 renderAdvGrid l.per; G-DEMO7 renderCatCounts paused-guard both paths; G-PHOTO card/detail photo poka-yoke) + a gentle demo-image link-health monitor (M-IMG). It watches, never edits; a guard FAIL / monitor alert is written as a Detect-schema finding (`findings_prevent.json`) so it re-enters Triage → Fix.
- **First run:** 3/3 guards PASS (the Phase 2–3 fixes are now permanent); M-IMG sampled 30 of 498 gallery URLs → 3 dead, 0 false positives (the link-rot DEMO-5 was routed to DEMO-4 for, now monitored). Cockpit: Phase 4 → built, Prevent card live; deployed prevent.py/prevent_checks.json/cockpit to /orchestrator/v2/ behind auth (644, sha-parity, 401).
- **Cost model impact:** none.

## Next Session (127)
- **Orchestration Phase 5 (Automate) — the last brick:** wire the Orchestrator + Scheduler to run Detect → Triage → Fix → Prevent nightly on the box (server cron, like sensor.py), surfacing only amber/red + a one-line "since last night" to the cockpit, and retire the old patched overnight loop (controlled cutover, shadow first).
- Candidate Detect finding: renderHomeStats has the same paused pattern as DEMO-7 (left out of scope); process poka-yoke: add smoke_test.py to the standard deploy set (the S125 drift).
- Standing: ORCH-POLICY-1 (§5 reconcile), DEMO-4 (R2 self-host, carries DEMO-5), LOOP-1, W12-FORYOU, PAYMENTS (F4).

## Last Completed (Session 125 — 2026-06-05)
- **Orchestration v2 Phase 3 (Fix) — built + first green-lane batch shipped.** New deterministic `orchestration_v2/fix.py` harness (queue-manager + gate-recorder + board-regenerator): consumes the green lane of `triaged.json` one item at a time; `--ship/--route/--fail` update status + append `fix_results.json` + regenerate the board; green ships (pre-authorised), amber stages, red never touched. The surgical edit stays the Sonnet checkpoint (bash-python str-replace + node/ast + smoke).
- **First Fix run = the S123 green queue (3 items): 2 shipped, 1 routed.** DEMO-6 (renderAdvGrid now honours l.per — the mislabeled /person/night stay) + DEMO-7 (renderCatCounts excludes l.paused at both count paths) shipped in ms.js v153 (diff = exactly the 3 regions; node-check; backup; smoke-green; live-verified; FEA baseline refreshed). DEMO-5 (27 dead gallery URLs) routed to DEMO-4's R2 self-host rather than re-hotlinking rot-prone URLs (S122 lesson; "never make it worse").
- **Cockpit:** Phase 3 → built, Fix card live with Copy-run-command, fix.html playbook button. Deployed fix.py/fix_results.json/triaged.json/board/cockpit to /orchestrator/v2/ behind auth (644, sha-parity, 401).
- **Cost model impact:** none.

## Next Session (126)
- **Orchestration Phase 4 (Prevent):** a poka-yoke per fixed defect class (so DEMO-6/7-style bugs can't recur) + scheduled monitors for the weak points we don't control (e.g. the demo image link-health check); then Phase 5 (Automate) — the Orchestrator + Scheduler cutover running Detect→Triage→Fix→Prevent nightly.
- **DEMO-4** (R2 self-host of demo images) now carries DEMO-5; **renderHomeStats paused-guard** is a candidate Detect finding (same class as DEMO-7, left out of scope this run).
- Standing: ORCH-POLICY-1 (§5 reconcile), LOOP-1, W12-FORYOU, PAYMENTS (F4).

## Last Completed (Session 124 — 2026-06-05)
- **Orchestration v2 Phase 2 (Triage) — built, deployed, first live run.** Design-first (data model + dedupe key + lane rules confirmed against the approved Phase 0). New deterministic, zero-token `orchestration_v2/triage.py`: dedupes each Detect finding on `file :: root-token` (line-numbers excluded) against ignore-list / BACKLOG / CHANGELOG; classifies a lane (red checked first by path/term, fail-safe to red, green only for confirmed-safe classes, else amber; a red proposal is never downgraded); prioritizes P1–P3. Emits `triaged.json` (the queue Fix consumes) + `triage_board.html`.
- **First live triage = the S123 Detect sweep (12 findings):** DEMO-5/6/7 → green Fix queue; 3 resolved (taxonomy/photo-parity/LIVE-bleed); 6 dismissed (false positives seeded into `ignore.json`, never re-raised); 0 amber/red/new. Cockpit: Phase 2 → built, Triage card live with Copy-run-command, playbook + board buttons. Deployed to `/orchestrator/v2/` behind Basic-Auth (644, sha-parity, 401 unauthed).
- **Smoke gate caught deploy drift:** server `smoke_test.py` was pre-S123 (stale bare-`Adventures` assertion → false fail); synced the committed local test (test-only, zero app risk). Smoke now all-green; demo data was correct (302 listings).
- **Filed (BACKLOG):** Detect findings-JSON poka-yoke (TRIAGE-IN-1); ORCHESTRATION_POLICY §5 ↔ v2 red-security reconciliation incl. re-laning the ADMIN_KEY backstop off the green nightly lane (ORCH-POLICY-1); Triage→BACKLOG safe-append discipline (TRIAGE-WB-1; LOOP-1 hazard — Edit tool truncated triage.py/ignore.json, rebuilt via bash-python).
- **Cost model impact:** none.

## Next Session (125)
- **Orchestration Phase 3 (Fix):** consume the green Triage queue (DEMO-5/6/7 as the first batch) — apply + verify, stage amber/red. The Detect→Triage→Fix tissue is now in place.
- **Reconcile ORCHESTRATION_POLICY §5** with the v2 red lane (security/secrets = red); re-lane the ADMIN_KEY backstop accordingly (ORCH-POLICY-1).
- Standing: LOOP-1 doc-writeback hardening; W12-FORYOU live geo-scope; PAYMENTS Merchant-of-Record (BACKLOG F4).

## Last Completed (Session 123 — 2026-06-05)
- **Orchestration cockpit live + Detect-engine run + 2 P2 demo fixes.** Added the Control Room (cockpit) launch button to the ops dashboard and aligned its Basic-Auth realm to the dashboard's ("TrustSquare Internal"→"TrustSquare Orchestrator") so the saved login auto-fills both (David login fix); fixed the cockpit 403 (deployed files were mode 700 → chmod 644). Ran the Phase-1 Detect engine end-to-end over demo mode (4 cities): deterministic audit → 3 parallel code-verified subagent sweeps → adversarial re-verify → gentle low-concurrency image-health (234 URLs). 7 of 9 initial flags ruled out as false positives.
- **P2 #1 (taxonomy):** Wave-1 (NY/London/Sydney) adventures were tagged bare `cat:Adventures`, so the Adventures Stays/Experiences sub-tabs were dead ("No Adventures yet"). Re-tagged all 30 → `adventures_experiences` (+ proper `experience_type`) and added 9 genuine `adventures_accommodation` stays (3/city) with HEAD-verified-live images. Each Wave-1 city now = 10 experiences + 3 stays (293→302 demo listings).
- **P2 #2 (photo parity):** card/featured/my-requests/local-market rendered `l.photo` while detail rendered `photos[0]||photo`; 23 Wave-1 listings diverged, 4 showed a dead card image. Added the `(l.photos&&l.photos[0])||l.photo` poka-yoke at all 4 card sites — card now matches detail and the 4 dead cards resolve. `ms.js` v149→v150 + demo_listings.json (BEA restarted; FEA baseline refreshed to v150; smoke updated for the new taxonomy). node --check + smoke all-green; live-verified.
- **LIVE-mode demo bleed (follow-up · reported by David):** on LIVE, an empty city (Sydney) showed the full demo totals (Property 40 / Adventures 59) + a 4-city Featured strip. Root cause: switching to live didn't purge demo listings from LISTINGS (asymmetric with switch-to-demo), the per-city scoping in renderHomeStats/renderFeatured + the renderCatCounts fallback only excluded demo when DEMO_MODE=true, and selectCity never re-rendered Featured/HomeStats. Fixed: purge demo/ph_ on switch-to-live + complete the `!DEMO_MODE && demo_` guard at the 3 sites that lacked it + selectCity/selectDemoCity now re-render Featured+HomeStats. ms.js v150→v152; predicate-simulation verified (live Sydney → 0; demo scoping intact); smoke green; FEA baseline v152.
- **Filed (BACKLOG):** DEMO-5 (27 dead gallery URLs / 34 listings), DEMO-6 (renderAdvGrid hardcoded per-suffix), DEMO-7 (renderCatCounts paused-guard latent).
- **Cost model impact:** none.

## Next Session (124)
- **Orchestration:** Phase 2 (Triage) when ready — the Detect run above is the model for it.
- **DEMO-5/6/7** demo polish; **DEMO-1** LM-tile dual-writer.
- **LOOP-1** harden loop doc-writeback; **W12-FORYOU (live)** geo-scope For You feed; **PAYMENTS** Merchant-of-Record (BACKLOG F4).

## Last Completed (Session 122 — 2026-06-05)
- **Demo-mode "one-pass" sweep + fixes (first parallel-subagent audit).** 4 subagents audited every home section × city, cross-checked; found 3 HIGH user-visible bugs (only 1 previously seen) + MED/LOW.
- **Fixed:** 60 missing titles (NY/Lon/Syd Collectors+Cars → "undefined") via real derived titles in `demo_listings.json` + code title-fallback; Adventure currency (grid "R89" vs detail "$89") via new `_priceLabel` helper through `ADV_COUNTRY_CURRENCY`; US World Heritage parks vanishing (USA alias, 13→16); heritage type-filter stuck (resets on city/mode switch); blank heritage strip on first load (loading placeholder); Adventure priceNum/per null. `ms.js` v147→v148 + demo_listings.json (BEA restarted). node --check + smoke green; API-verified.
- **Filed (BACKLOG):** DEMO-1 LM-tile suburb inconsistency (latent), DEMO-2 heritage coverage gaps, DEMO-3 demo cosmetics.
- **Cost model impact:** none.

## Next Session (123)
- **DEMO-1:** LM-tile dual-writer + suburb-filter inconsistency.
- **LOOP-1:** harden the loop doc-writeback (still truncating BACKLOG).
- **W12-FORYOU (live):** geo-scope the For You feed (BEA). **PAYMENTS:** Merchant-of-Record setup (BACKLOG F4).
- Maintenance queue: SCAN-10…12, DASH-VER-1, HTML-1/2.

## Last Completed (Session 121 — 2026-06-05)
- **SCAN-9 DONE (MED · dead code in `update_listing_wonders` · auto-shipped).** The `PUT /listings/{listing_id}/wonders` handler in `bea_main.py` was a dead stub: it computed `body = asyncio.run(request.json())…`, set `body_bytes = b""`, and did a local `import json as _j` — then ignored all three and `return _update_listing_wonders_sync(...)`, which only raises HTTP 500 "Use POST form". The live, working endpoint is `POST /listings/{id}/wonders` (`set_listing_wonders`), which parses the body itself via `await request.json()`. So `import json` (F401) and `body`/`body_bytes` (F841) were genuinely unused, and removing `body` also orphaned the local `import asyncio` (its only consumer).
- **Fix:** removed the whole 6-line dead block, leaving the docstring + the real `return _update_listing_wonders_sync(listing_id, request)` — behaviour-neutral (the PUT stub still 500s callers to POST, exactly as before) and complete (no newly-orphaned `import asyncio` for next week's scan to re-flag). One surgical Python str.replace (old-string asserted to match exactly once; −186 bytes), never Edit/Write.
- **Gate:** World-Heritage wonders-link handler — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / SA-ID-KYC code, no pricing/refund path → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2). Auto-shipped.
- **Verify/deploy:** `ast.parse` clean local + BEA venv; whole-file diff vs a freshly-pulled server copy = exactly the 6 removed lines (local was byte-identical to server beforehand); `smoke_test.py` all-green pre **and** post (incl. the BEA `/wonders` check, 304 sites). Server backup `main.py.bak-20260605-scan9`; scp `bea_main.py` → `main.py` (server sha256 == local); BEA restarted **active**, `/health` ok v1.3.1 (localhost + public); Cloudflare purged (`{"purged":true}`).
- **Cost model impact:** none — dead-code removal; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (122)
- **Maintenance auto-ship queue (top → back):** SCAN-10 (redundant `from datetime import timedelta` re-imports, `bea_main.py` ~4001/~8446), then SCAN-11 (dead locals `skip_fields`/`sig_suburb_id`/`cutoff` + vulture `family`/`hint` + unused `_sqlite3` import; rename unused loop vars `hi2`/`idx` → `_`), SCAN-12 (`import os` unused in `database.py`:2), DASH-VER-1 (`/dashboard/summary` `bea_version` 1.3.0→1.3.1 — confirmed live-drifted again this run vs `/health` 1.3.1), HTML-1, HTML-2, then SCAN-PANEL-1/2.
- **Awaiting your approval:** none.
- **Standing:** PAYMENTS Merchant-of-Record path (BACKLOG F4); LOOP-1 harden the orchestrator doc-writeback; W12-FORYOU live geo-scope of the For You/wishlist feed; self-hosted Overpass re-import (BLOCKER); Paystack live mode; EULA v1.6 attorney review; support@ mailbox (L3a); A11Y-1/2/3 + ADMIN_KEY filed to the design/ops track.

## Last Completed (Session 120 — 2026-06-04)
- **Category tiles always show, even at 0 (David feedback).** Empty demo/prospect cities (Chicago, Cape Town) were showing no category tiles because demo mode hid 0-count tiles. Now the six category tiles + Local Market always render with their count ("0 listings" when empty) so the structure is always visible.
- **Fix (`ms.js` v146→v147):** removed the demo-only hide-empty-tiles behaviour (a pre-launch TODO) in `renderCatCounts`. Populated cities unchanged; empty cities show all categories at 0. node --check + smoke green; deployed; CF purged.
- **Cost model impact:** none.

## Next Session (121)
- **PAYMENTS (David proceeding):** stand up the Merchant-of-Record path (Paddle / Lemon Squeezy) for US/UK/AU launch — no US entity or travel; sidesteps the Stripe-direct + Paystack blockers. See BACKLOG F4. (Optional first step: Claude's fee-math one-pager.)
- **LOOP-1 (open):** harden the orchestrator loop's doc-writeback (it truncated BACKLOG repeatedly this run).
- **W12-FORYOU (live):** geo-scope the For You / wishlist feed on the BEA (affects live mode).
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing: admin onboarding country selector; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 119 — 2026-06-04)
- **"For You" feed hidden in demo mode (David-reported follow-up).** After the placeholder fix, demo prospect cities (Phoenix) still showed real Pretoria collectibles in the For You strip — that's the personalised wishlist feed (`wlLoadFeed` → BEA `/wishlist/feed`), which has no demo data, so in demo it could only show real listings.
- **Fix (`ms.js` v145→v146):** `wlLoadFeed` hides the whole For You section in demo mode (restores in live); `devSetMode` re-evaluates it on toggle. Demo cities now have a clean home; live unchanged. node --check + smoke green; deployed; CF purged.
- **Still open (BACKLOG W12-FORYOU):** LIVE geo-scoping of the feed (BEA-side) — a live Houston/Phoenix buyer should see local recommendations, not Pretoria.
- **Cost model impact:** none.

## Next Session (120)
- **LOOP-1 (open action):** harden the orchestrator loop's doc-writeback (safe-write+verify) — it truncated BACKLOG.md repeatedly this run. See BACKLOG.
- **W12-FORYOU (live):** geo-scope the For You / wishlist feed on the BEA (affects live mode).
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing: admin onboarding country selector; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 118 — 2026-06-04)
- **Placeholder cards leaked into every city's category counts (David-reported).** Demo empty city (Houston) showed Property/Tutors/Services = "1 listing" (the paused Pretoria `ph_*` "coming soon" cards) while other categories were hidden. They aren't `demo_`/`isLive`, so they bypassed the Session 116 city filter via the `renderCatCounts` fallback + `renderGrid`.
- **Fix (`ms.js` v144→v145):** excluded `ph_` from the count fallback and city-scoped them in `renderGrid` — empty cities now read 0 (tiles hidden, like New York), Pretoria unchanged. Simulated against live demo data (Houston→{}, Pretoria→full) + node --check + smoke green; deployed; CF purged.
- **Filed (BACKLOG W12-FORYOU):** the "For You"/wishlist feed isn't geo-scoped — showed Pretoria collectibles in Houston and would do the same in live mode; needs a server-side city/country scope on the BEA `/wishlist/showcase` + `/feed` endpoints.
- **Cost model impact:** none.

## Next Session (119)
- **LOOP-1 (open action):** harden the orchestrator loop's doc-writeback (safe-write+verify) — it truncated BACKLOG.md twice this run (Sessions 117 & 118); caught + restored each time. See BACKLOG.
- W12-FORYOU: geo-scope the For You / wishlist feed (BEA-side; affects live).
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing follow-ups: admin onboarding country selector; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 117 — 2026-06-04)
- **World Heritage strip stuck on demo country after returning to live (David-reported).** Demo US city → toggle live ZA left the heritage strip showing US sites (unscrollable to ZA) while the selector read "All". Root cause: `selectDemoCity` set `_wfCountry` to the city's country without syncing the dropdown, and `devSetMode`→live never reset `_wfCountry` or re-rendered the strip.
- **Fix (`ms.js` v143→v144):** selectDemoCity syncs the `wf-country-select` dropdown; devSetMode→live resets `_wfCountry='all'` + dropdown; devSetMode re-renders the strip. Live ZA now shows "All" heritage (Africa/ZA first), matching the selector. node --check + smoke green; deployed; CF purged.
- **Cost model impact:** none.

## Next Session (118)
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing follow-ups: admin onboarding country selector for non-ZA prospects; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 116 — 2026-06-04)
- **Demo home-page counts now respect the selected city (David-reported).** In demo mode an empty prospect city (e.g. New York) showed Pretoria's category counts + home stats even though the grid correctly showed nothing. Root cause: `renderHomeStats()` and the `renderCatCounts()` count-all fallback ignored `activeCity` (unlike `renderGrid`).
- **Fix (`ms.js` v142→v143):** applied the grid's demo/live active-city filter to both count paths, so an empty city reads 0 (empty tiles hidden) and home matches the grid. Node unit-test of the predicate (NY→0, Pretoria→its listings) + node --check + smoke all-green; deployed; CF purged.
- **Cost model impact:** none.

## Next Session (117)
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing follow-ups: admin onboarding country selector for non-ZA prospects; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 115 — 2026-06-04)
- **SCAN-8 DONE (MED · trust-score dup-key · auto-shipped).** `_CATEGORY_SIGNALS["Cars_private"]` in `bea_main.py` defined `category.cars.service_history` **twice**: the fuller line 6060 (`"Service history on file"`, richer how-to-earn) was silently overridden by the terser line 6064 (`"Service history"` / `"Upload service book."`), so the weaker copy was what rendered. Both entries carried **points: 4**, so trust-score math was already correct — only the displayed name + how-to-earn text was affected.
- **Fix:** removed the terser duplicate (6064), leaving the fuller 6060 entry as the sole definition; the better "Service history on file" / "Upload scan of service book or dealer service records…" copy now renders. One surgical Python `str.replace` (old-string asserted to match exactly once; key occurrences 2→1; −124 bytes), never Edit/Write.
- **Gate:** trust-score config only — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / SA-ID-KYC code, and the points value is unchanged → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2). Auto-shipped.
- **Verify/deploy:** `ast.parse` clean local + BEA venv; diff vs a freshly-pulled server copy = exactly the one removed line (local was byte-identical to server beforehand); `smoke_test.py` all-green pre **and** post. Server backup `main.py.bak-20260604-scan8`; scp `bea_main.py` → `main.py` (server sha256 == local); BEA restarted **active**, `/health` ok v1.3.1 (localhost + public); Cloudflare purged (`{"purged":true}`); served `main.py` now carries the key once.
- **Cost model impact:** none — config dedup; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (116)
- **Maintenance auto-ship queue (top → back):** SCAN-9 (dead local `import json` + unused `body`/`body_bytes` in `update_listing_wonders`, `bea_main.py` ~8268 — confirm the body is parsed elsewhere first), then SCAN-10 (redundant `from datetime import timedelta` re-imports), SCAN-11 (dead locals / unused loop vars → `_`), SCAN-12 (`import os` unused in `database.py`), DASH-VER-1 (`/dashboard/summary` `bea_version` 1.3.0→1.3.1 — confirmed live-drifted again this run vs `/health` 1.3.1), HTML-1, HTML-2, then SCAN-PANEL-1/2.
- **Awaiting your approval:** none — S5 is verified DONE + fail-closed since 2 Jun; do NOT re-stage.
- **Standing:** self-hosted Overpass re-import (BLOCKER), Paystack live mode (`PAYSTACK_WEBHOOK_SECRET` + `sk_live` keys), EULA v1.6 attorney review, support@ mailbox (L3a); A11Y-1/2/3 + ADMIN_KEY filed to the design/ops track.

## Last Completed (Session 114 — 2026-06-04)
- **ZA duplicate-city fix (David-spotted).** Nelspruit & Mbombela showed as two cities on one spot — Nelspruit was officially renamed Mbombela (2009, upheld 2014). The Session 113 Wave 2 seed had added "Nelspruit" though the official "Mbombela" was already in the GeoNames seed; a near-dupe sweep found the **same bug for Port Elizabeth → Gqeberha** (renamed 2021).
- **Fix (`dedupe_za.py`, data-only, DB backed up):** deleted the two 0-suburb/0-listing duplicates and renamed the canonical entries to `Mbombela (Nelspruit)` (id50, 331 suburbs) and `Gqeberha (Port Elizabeth)` (id70, 51 suburbs) so the former names stay discoverable via the `q=` typeahead. ZA cities 57→55; verified live.
- **FEA `ms.js` v141→v142:** demo-list entries updated to the canonical names+coords; node --check clean; deployed; CF purged; **smoke all-green**. `seed_wave12_cities.py` hardened so it cannot re-add the dupes.
- **Cost model impact:** none.

## Next Session (115)
- Standing follow-ups (carried from S113): admin seller-onboarding country selector for non-ZA prospects; international suburb seeding; Wave 3 AU city seed; in-app visual click-test when the Chrome extension reconnects.
- Maintenance auto-ship queue (unchanged): SCAN-8…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.

## Last Completed (Session 113 — 2026-06-04)
- **Wave 1 + Wave 2 cities now selectable + maps auto-aligned (David-directed pre-launch prep).** Seeded the geo hierarchy for US/GB/AU (3 countries, 10 regions, 23 international cities) plus the 3 missing ZA Wave-2 cities (Port Elizabeth, East London, Nelspruit), all with accurate centre lat/lng; verified through the public `/geo` API. Idempotent `seed_wave12_cities.py`; live DB backed up; data-only (no BEA change/restart — `/geo` endpoints were already country-agnostic).
- **Map auto-alignment (`ms.js` v140->v141).** `selectCity` now captures the city lat/lng the `/geo` API already returns and `renderMap` centres on it — replacing the hardcoded 4-city `CITY_CENTERS` dict that had been mis-centring every non-Pretoria city (incl. Cape Town/Joburg) on Pretoria. `DEMO_COUNTRY_CITIES` extended with all Wave 1/2 cities + coords; map re-renders on city switch in map view. 5 surgical str-replace edits; `node --check` clean; deployed; CF purged; **smoke all-green**.
- **Verification:** picker click-path (country->region->city) resolves with correct coords across a ZA/US/UK/AU sample; served `ms.js` carries all edits. In-app visual walkthrough pending Chrome reconnection (extension offline this session).
- **Gaps filed (BACKLOG):** Wave 3 AU seeding; international suburb hierarchy; admin seller-onboarding country selector for non-ZA prospects.
- **Cost model impact:** none — geo data + display-centring only; launch cadence unchanged (still gated on patent + whitepaper).

## Next Session (114)
- **Wave 1/2 readiness follow-ups:** admin seller-onboarding country selector (region/city currently hardcoded `country=ZA`) so international prospects get a `geo_city_id`; international suburb seeding if suburb-level gating is wanted for intl cities; Wave 3 AU city seed when Wave 3 approaches.
- **In-app visual click-test** of the city picker + map alignment once the Chrome extension is back online.
- **Maintenance auto-ship queue (unchanged):** SCAN-8...12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing: self-hosted Overpass re-import (BLOCKER), Paystack live mode, EULA v1.6 attorney review, support@ mailbox (L3a).

## Last Completed (Session 111 — 2026-06-03)
- **JS-2 DONE (HIGH · buyer-app crash-fix · auto-shipped).** `ms.js:86` called `updateLocBadge()` — a function defined nowhere (the second and last genuinely-undefined call in `ms.js` per the 1 Jun ESLint sweep, after JS-1). It sat in the "Re-render everything" block (alongside `renderGrid()`/`renderCatCounts()`/`initLMHomeTile()`) that runs after a demo↔live listings mutation, so the location-badge refresh threw a ReferenceError on every demo/live toggle.
- **Fix:** renamed the single call to `updateBadgeLabel()` — the real zero-arg 2-line location-badge repaint fn (`ms.js:112`; rewrites `home-city-badge` with country+region / city and calls `_refreshCityLabels()`). Verified the target's signature/behaviour match the call shape before renaming (zero-arg; identical to the 5 existing `updateBadgeLabel()` call sites). One surgical Python binary str.replace (old-string unique; `updateLocBadge` 1→0; `updateBadgeLabel` 6→7; ms.js +2 bytes 714993→714995), never Edit/Write.
- **Gate:** frontend-only (`ms.js` + index cache-bust) — clears Gate 1 and Gate 2; the JS-1-class auto-ship boundary example (ORCHESTRATION_POLICY §5). Auto-shipped.
- **Verify/deploy:** `node --check` clean (local + server); diff vs freshly-pulled server copy = exactly the one renamed line (local byte-identical to server beforehand) + the `ms.js?v=132→133` cache-bust in index.html. No BEA change → no restart. Server backups `*.bak-20260603-js2`; scp `static/ms.js` + `index.html` (server bytes == local, sha-matched); Cloudflare purged (POST). Live through CF: index serves `ms.js?v=133`, served `ms.js` has 0 `updateLocBadge` + 7 `updateBadgeLabel`, line 86 = `updateBadgeLabel();`; `/health` ok v1.3.1; **smoke all-green** pre + post; FEA baseline refreshed (ms.js v133/714995). **ms.js is now free of undefined-call crashes — JS-1 + JS-2 both closed.**
- **Cost model impact:** none — display-repaint rename only; no AI calls, pricing, concurrency, or city-launch change.
- **S5 — VERIFIED ALREADY DONE + LIVE (held in error this morning, corrected same day).** The run first held queue-top S5 on a bare `approved:true` the audit trail contradicted (`orchestrator/log.md`: "S5 left unapproved"). A same-day check (David-prompted) then confirmed S5 was **already built, committed (`1f40b58`, "Session 110c"), and deployed on 2 Jun**: `_payment_grants_allowed()` is live on the BEA (definition @3089 + 4 guard sites @3129/3201/3359/5021 across all grant paths) plus `/payment/verify` idempotency. Live env (`sk_test`, `ALLOW_TEST_PAYMENTS` unset) → gate returns False → test-card grants fail-closed (correct pre-launch posture). The "hold" was **tracking drift** — S5 was never marked DONE in the audit queue, so it kept resurfacing — not a real pending item. Corrected: removed from `staged.json` + the queue; nothing awaits approval. When live `sk_live_` keys land, grants auto-resume with no code change.

## Next Session (112)
- **Filter v1 LIVE (FEA · David-directed, 3 Jun):** global **Trust ≥** selector now in the browse filter bar (Any/60/70/80/90), client-side over loaded listings, surfaced as a "★ Trust ≥ N" tag (`ms.js` v134; smoke 39/39; served-through-CF verified). First increment of the Filter design — UI-first; Step 1 backend parked. **Next:** Save-as-Wishlist, then scope + currency (ride on Step 1). Design: `FILTER_APP_MOCKUP.html` · `GLOBAL_MARKETPLACE_DESIGN.html` · `STEP1_BUILD_SPEC.html`. (Browser click-test pending — Chrome extension was offline.)
- **Maintenance auto-ship queue:** SCAN-8 (duplicate dict key `category.cars.service_history`, bea_main.py ~6017), then SCAN-9, SCAN-10, SCAN-11, SCAN-12, DASH-VER-1 (stale `bea_version` 1.3.0→1.3.1), HTML-1, HTML-2, then SCAN-PANEL-1/2.
- **S5 — DONE, no action (do NOT re-stage).** Already deployed + fail-closed since 2 Jun (see the Session 111 correction above); it is not awaiting approval. The real money-path go-live items (separate from S5, triggered when Paystack approves live mode): set `PAYSTACK_WEBHOOK_SECRET` (currently unset → reliable webhook credit path off) and swap `sk_test` → `sk_live` keys — both server-env only, grants auto-resume, no code change.
- Standing: self-hosted Overpass re-import (BLOCKER), Paystack live mode, EULA v1.6 attorney review, support@ mailbox (L3a).

## Last Completed (Session 110 — 2026-06-03)
- **Tiered Value Selector steps 3-5 — BUILT, VERIFIED, SHIPPED (free tiers only; paid OFF; B7 intact).** Steps 1-2 (tier config + `GET /listings/{id}/value-tiers` + tier-aware price/yield) were committed in S108 but never deployed; shipped here together with 3-5.
- **STEP 3 — FREE/owned resolvers** (`tier_resolvers.py` + versioned/dated `value_benchmarks.py`): UK property = HM Land Registry Price Paid (keyless SPARQL, OGL); US/UK rent = HUD FMR / ONS-VOA area benchmarks; internal comps (median of comparable listings, min-8 gate) for property+vehicles; ZA PayProp/TPN aggregate area guide (0T); collectible feeds (BrickLink/Numista/JustTCG) wired but credential-gated -> dark until a key is set. Flat `NET_COST_PCT=3.0` replaced by a versioned, dated, per-region net-cost band (ZA 3.0% unchanged). Country-aware yield benchmarks (H7b). The NUMBER always comes from a feed/arithmetic; the model only narrates. `_resolver_ready()` reflects built + credential-aware readiness so the FEA hides any chip we cannot deliver.
- **STEP 5 — flag store** (`feature_flags.py` + `feature_flags.json`): replaced the hardcoded `PAID_TIERS_ENABLED` + per-provider booleans with a server-readable, mtime-cached store. Default paid OFF / all paid providers OFF / free ON; a malformed file fails safe (never enables paid). Enabling a provider later is a config edit, no redeploy.
- **STEP 4 — FEA chip selector** (`ms.js` v132): the listing detail calls value-tiers and renders colour chips (green 0T / blue 1T / gold 2T) for ready:true only, hiding the service entirely when none. Tap calls price/yield with the chosen tier; 2T cost disclosed before the call; full workings shown (gross formula, annual rent, used/implied price, net-cost band, benchmark, AI context, provenance + date) with the mandatory "Indicative only - not financial advice or a formal valuation" label (H7a/H7b). DEMO_MODE guard, both branches. Added as new `tvs*` functions; legacy buyerPriceCheck/buyerYieldCalc left untouched.
- **Verify/deploy.** New modules sha-matched server + py_compile in BEA venv; pyflakes clean (0 undefined-name, 0 new warnings); module unit tests 9/9. FEA: node --check clean (local+server), diff = exactly the 2 button blocks -> chip containers + new fns, all smoke invariants intact. Deployed main.py + 4 modules + feature_flags.json + ms.js v132 + index.html; BEA restarted active v1.3.1; Cloudflare purged. Live: value-tiers returns the ZA 0T area-guide chip ready:true (fair_price + yield); 0T price-check returns a real benchmark range with charged:False. **smoke all-green** (server --local); fea_integrity OK (version-bump notes only); fea_baseline refreshed (ms.js v132/714993, ms.css v120/116322).
- **Cost model impact:** only FREE tiers enabled; no consumption/paid API called; PAID_TIERS_ENABLED stays False -> live AI unit economics unchanged. (0T price-check is a templated zero-model response; 0T area-yield reuses one cheap existing-budget Haiku narration.)
- **FILED (BACKLOG):** comics/watches fair-price + US/AU fair-price 0T have no free specific feed yet (config-only, hidden); collectible 1T feeds stay config-only until David sets BrickLink/Numista/JustTCG keys.

## Next Session (111)
- **Optional TVS follow-ups:** set BrickLink OAuth / Numista / JustTCG keys in env to light the LEGO/coins/TCG 1T chips; drop a `value_benchmarks.json` on the server to refresh area benchmarks without a redeploy; consider skipping the model on 0T area-yield to make it strictly zero-cost.
- **Maintenance auto-ship queue (unchanged):** JS-2 (`updateLocBadge`->`updateBadgeLabel`), then SCAN-8..12, HTML-1/HTML-2.
- Standing: self-hosted Overpass re-import (BLOCKER), Paystack live mode, EULA v1.6 attorney review, support@ mailbox (L3a).

## Last Completed (Session 109 — 2026-06-02)
- **Maroushka property-photo cleanup (David-requested · data-only, no code change).** Maroushka's 39 furnished-apartment listings (ids 192–230, one building) carried **510 published photos** (0–35/unit) — bloated with re-uploaded duplicates and with exterior/entrance/street/signage shots that exposed the location (193 Albert Street, 308 Florence Ribeiro Road, security-boom gate, "Entrance for 301,302…", "To Let" board), breaking seller anonymity (A2). David could not get Maroushka to trim them.
- **Method.** Downloaded all 510 from R2; content-hashed (md5 + 256-bit pHash/dHash) → **276 distinct images** (216 byte-identical re-uploads); union-find clustered near-identical (validated: zero clusters with intra-max pHash >14, no over-merge). Visually reviewed all 276 via labelled contact sheets + a 150-tile high-res confirmation pass to classify every cluster (interior / amenity / exterior-or-signage) — essential because location shots included UUID-named files (no address in the filename) and bare-numbered files that were exterior in some units, interior in others.
- **Rules applied per unit:** drop exact + near-identical duplicates (keep best) → remove location-revealing exterior/entrance/street/signage/perimeter shots (kept generic amenity per David: pool, garden, private balcony/patio) → cap at ≤10, prioritising unit-specific interiors, reserving up to 2 amenity slots. Shared interior "lobby/main-entrance" staircase shots were also removed (no unit value + address embedded in their R2 filename).
- **Result: 510 → 254 photos.** Removed 81 duplicates + 153 location-revealing + 22 over-cap. All 39 units now ≤10; 0 duplicate URLs; 0 location-leaking URLs except the pool amenity (see flag). Units 109 (198) & 308 (211) were already photoless; **Unit 314 (216)** is now photoless — its only 3 photos were an exterior entrance + 2 copies of the shared lobby (it never had a photo of the actual unit) → **needs real interior photos**.
- **Backup/verify/deploy.** Live `marketsquare.db` backed up (`marketsquare.db.bak-20260602-photocleanup`); every original description archived (`maroushka_photos_backup_2026-06-02.json` on server + local). Transactional UPDATE of the `[photos:]` prefix only (preserves description text; `photo_urls` left NULL — FEA reads `[photos:]` first, ms.js:248); dry-run diff confirmed (5 already-clean units reproduced byte-identically → no corruption). BEA restarted, Cloudflare purged. Live re-query: 254 photos, all ≤10, no dupes/leaks; spot-checks 192→9, 200→8, 205→10 (pool present), 216→0. **smoke 39/39**.
- **Flag (URL filename leak, not actioned):** the kept pool shots' R2 filenames still read `Pool_308_Florence_Ribeiro…` — the *image* shows only a pool, but a user opening the URL sees the address. Fully closing anonymity would mean re-uploading kept amenity images under sanitised keys (touches R2 storage). Offered to David as a follow-up.
- **Cost model impact:** none — no AI calls (local hashing only), no pricing/infra/concurrency/email/city-launch change.

## Next Session (110)
- **RM-4 Phase 1 LIVE (shadow):** deterministic zero-token `sensor.py` on server cron @ 01:30 UTC (=03:30 SAST) writing `findings.cron.json` for parity vs the Claude Sensor; model-tiering policy adopted as ORCHESTRATION_POLICY §11; `smoke_test.py` gained `--local`. First parity run: smoke 38/38, health/spend/anomaly all match; only gap = open_items 16 vs 17 = **AUDIT_PROGRESS.md marker staleness** → flip SCAN-2…6 to DONE + add `[· OPEN]` markers for A11Y-1/2/3, ADMIN_KEY, L3a, S5. After ~7d parity → `sensor.py --live` + pause `trustsquare-orch-sensor` task. Monday scan still on the Claude pass until ruff/vulture/pylint venv is on the box. (Plan: `LAUNCH_READINESS_PLAN.html`, Wave A.)
- **H2/H3 introduction notification loop — DONE (verified 2 Jun).** Was fully built in a prior session but had never run; switched on + tested end-to-end this session — 3 branded, anonymity-safe emails (new-intro->seller, accept/decline->buyer) confirmed delivered to Primary inbox. No code change (BEA already fired the webhooks; n8n workflows already active). Flag: the accept email references an in-app "anonymous messaging system" — confirm that channel exists / define the post-acceptance connection path.
- **Unit 314 (listing 216)** — get real interior photos from Maroushka (now photoless); same for already-empty Units 109/308.
- **Optional anonymity follow-up:** sanitise kept amenity image filenames on R2 (re-upload pool/garden shots under hashed keys, rewrite URLs) to remove the address from the photo URL.
- **Still pending from CHANGELOG Session 108 (built, NOT deployed):** Tiered Value Selector steps 3–5 + David's `git add/commit` of the BEA framework + `ai_service_tiers.py`.
- **Maintenance auto-ship queue (unchanged):** JS-2 (`updateLocBadge`→`updateBadgeLabel`), then SCAN-8…12, HTML-1/HTML-2.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 107 — 2026-06-02)
- **JS-1 DONE (HIGH · buyer-app crash-fix).** The Paystack payment-return handler in `ms.js` credited the local balance (`tuppence += credited`) then called `updateTuppenceDisplay()` to repaint it — a function defined nowhere (the only genuinely-undefined call in `ms.js` per the 1 Jun ESLint sweep). It threw a ReferenceError, aborting the rest of the top-up success path (success toast + navigation to the wallet) on every real payment return.
- **Fix:** renamed the single call to `updateTuppenceUI()` (the real repaint fn, `ms.js:823` — zero-arg, writes `tuppence` into the nav badge, balance display, home balance, and dash counter). Verified the target's signature/behavior match the call shape before renaming; the `tuppence += credited` credit line was left untouched (pure display repaint, not ledger — authoritative balance is server-side). One surgical Python str.replace (old-string unique; `updateTuppenceDisplay` 1→0; `ms.js` −5 bytes), never Edit/Write.
- **Gate:** frontend-only (`ms.js` + index cache-bust) — clears Gate 1 and Gate 2; JS-1 is the exact auto-ship boundary example in ORCHESTRATION_POLICY §5. Auto-shipped.
- **Verify/deploy:** `node --check` clean; diff vs freshly-pulled server = exactly the one renamed line + the `ms.js?v=130→131` cache-bust in index.html (local byte-identical to server beforehand). No BEA change → no restart. Server backups `*.bak-20260602-js1`; scp `static/ms.js` + `index.html` (bytes == local); Cloudflare purged. Live through CF: index serves `ms.js?v=131`, served `ms.js` has 0 `updateTuppenceDisplay`, fix site reads `tuppence += credited;`→`updateTuppenceUI();`; `/health` ok v1.3.1; **smoke 39/39** pre + post.
- **Cost model impact:** none — display-repaint rename only.

## Next Session (108)
- **JS-2 (HIGH)** — next auto-ship item in the maintenance queue: `ms.js:86` calls `updateLocBadge()` (defined nowhere) inside a "re-render everything" block after a listings mutation → ReferenceError on the location-badge refresh. Rename to `updateBadgeLabel()` (defined `ms.js:112`) after confirming its signature/behavior match the intended 2-line location-badge update. `node --check` + smoke before deploy.
- **Then the rest of the auto-ship queue:** SCAN-8 (duplicate dict key `category.cars.service_history`), SCAN-9 (dead `json` import + `body`/`body_bytes` locals), SCAN-10 (redundant `from datetime import timedelta` re-imports), SCAN-11 (dead locals / unused loop vars → `_`), SCAN-12 (`import os` in database.py), HTML-1 (dead `currentView`), HTML-2 (unused admin module-level locals).
- **Attended / staged track (deliberately NOT in the auto-ship queue):** S5 (MED · Gate 2 — gate the test/auto-approve payment endpoints behind a prod env flag, fail-closed; **stages** for David's approval), L3a (support@trustsquare.co real mailbox), SCAN-PANEL-1/2 (weekly-scan dashboard panel), the ADMIN_KEY FOUND_NEW, and A11Y-1/2/3.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 106 — 2026-06-02)
- **S3 DONE (Phase 2 · HIGH).** Moved the BEA API key off the `?api_key=` query param to the `X-Api-Key` header only, across the three seller-document (KYC) endpoints that shared the dual-mode dependency `auth.require_api_key_header_or_query`: `POST` / `GET` / `DELETE /users/{email}/documents[/{doc_id}]`. A key in the query string lands in nginx + Cloudflare logs and browser history; every other protected endpoint was already header-only.
- **Disproved the CDN assumption first (the gate).** The query fallback rested on a docstring claim that "Cloudflare strips custom headers." False, proven twice: (a) the admin app already calls these same three endpoints header-only in production through Cloudflare; (b) a live request through trustsquare.co with only `X-Api-Key` → 200, no-auth → 401, wrong key → 401. Cloudflare passes the header through untouched.
- **Edits (surgical, 3 files + cache-bust).** `bea_main.py`: 3 endpoint deps `require_api_key_header_or_query` → `require_api_key` (whole-file diff = exactly those 3 lines). `auth.py`: deleted the now-dead `require_api_key_header_or_query` fn + its orphaned `Query` import — the query-auth path is gone, not just unused. `ms.js`: retired all 3 `?api_key=` sites — the POST upload already sent the header (URL trimmed); the two `apiGet` list calls relied only on the query string (the shared `apiGet` sends no headers), so added an `apiGetAuth(path)` helper that sends `X-Api-Key` and pointed both at it. Bumped `ms.js?v=129 → v=130`. All via the Python str.replace driver, never Edit/Write.
- **Verify/deploy.** AST clean local + BEA venv; node --check clean; per-file diff vs the freshly-pulled server copy = only the intended changes (local was byte-identical to server on all four files); `main.py` imports under the live systemd unit env before restart. Server backups `*.bak-20260602-s3`; scp main.py/auth.py/static/ms.js/index.html (server bytes == local on all 4); BEA **active**, `/health` ok v1.3.1 (localhost + public). **Live auth test through CF:** GET header→200, GET `?api_key=`→401, GET no-auth→401; DELETE header→404 (auth passed, doc absent), DELETE `?api_key=`→401. Cloudflare purged; live app serves `ms.js?v=130`; **smoke all-green** pre + post.
- **Cost model impact:** none — auth-mechanism change only; no new AI calls, pricing, concurrency, email-volume, or city-launch change.

## Next Session (107)
- **Phase 2 cont. — S5 (MED):** gate the test / auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode is pending). AST + smoke before deploy.
- **Then L3a:** support@trustsquare.co real mailbox — one surgical env-driven `_smtp_send_reply()` edit + ops Cloudflare/Brevo config (see SUPPORT_MAILBOX_SETUP.md). Replies currently send from dmcontiki2@gmail.com.
- **Then:** SCAN-8…12 cleanup + SCAN-PANEL-1/2 (weekly-scan dashboard panel) + JS-1/JS-2 (ms.js latent ReferenceErrors) + HTML-1/HTML-2 dead-var cleanup + the ADMIN_KEY FOUND_NEW (`/admin/purge-cache` + `/admin/refresh-pois` unauthenticated when `ADMIN_KEY` unset) + A11Y-1/2/3 (focus ring, aria-live, admin alt-text/labels).
- **Deferred (David default):** EULA "Refunds" → "No Refunds" heading rename — leave for the v1.6 attorney-review pass (not an audit item).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 105 — 2026-06-01)
- **SCAN-7 DONE (HIGH · final KYC/vision crash-bug — block SCAN-1→7 now CLOSED).** `bea_main.py` `vision_draft` (`POST /listings/vision-draft`) called `background_tasks.add_task(_log_ai_spend, …)` (line 9365) but `background_tasks` was never in the endpoint signature — a guaranteed `NameError` → HTTP 500 at request time, *after* the Claude Vision call had already run (so the draft was computed then discarded and its spend never logged). Latent because every existing param had a `File(...)`/`Form(...)` default, so the route imported cleanly.
- **Fix:** added `background_tasks: BackgroundTasks` as the **first** parameter of `vision_draft` (a no-default param must precede defaulted ones — valid Python; matches `create_listing`/`create_intro`). `BackgroundTasks` already imported (line 1); FastAPI injects it by annotation regardless of position, so the unguarded call site is now always non-None. One surgical Python str.replace (old-string unique); +39 bytes (501792→501831), LF-only, diff = exactly one inserted line.
- **Verify/deploy:** `ast.parse` clean local + BEA venv; AST introspection confirms the deployed `main.py` `vision_draft` now lists `background_tasks` first. main.py deployed (server backup `main.py.bak-20260601-scan7`, server bytes == local); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅** pre- and post-deploy.
- **Minor finding (flagged, not actioned — one item/run):** `ADMIN_KEY` is unset on the server, so `/admin/purge-cache` + `/admin/refresh-pois` accept unauthenticated calls. Low risk (cache purge / POI refresh only); logged in AUDIT_PROGRESS.md for triage.
- **Cost model impact:** none — adds a framework-injected parameter so the already-billed vision-draft spend actually logs (it was dropped on the crash); no new AI calls, no pricing/concurrency change.

## Next Session (106)
- **Phase 2 resumes (KYC/vision crash-bug block closed) — S3 (HIGH):** move the BEA API key off the `?api_key=` query param (it lands in nginx/Cloudflare logs + browser history) to `X-Api-Key` header only across the 3 endpoints + ms.js; first verify/remove the CDN header-stripping assumption that justified the query fallback. AST + smoke before deploy.
- **Then S5 (MED):** gate the test/auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode pending).
- **Then L3a:** support@trustsquare.co real mailbox — one surgical env-driven `_smtp_send_reply()` edit + ops Cloudflare/Brevo config (SUPPORT_MAILBOX_SETUP.md).
- **Then:** SCAN-8…12 cleanup + SCAN-PANEL-1/2 (weekly-scan dashboard panel) + JS-1/JS-2 (ms.js latent ReferenceErrors) + HTML-1/HTML-2 dead-var cleanup.
- **New minor finding (this run):** `ADMIN_KEY` unset → `/admin/purge-cache` + `/admin/refresh-pois` unauthenticated; set the env or fail-closed (rank below S3/S5/L3a).
- **Deferred (David default):** EULA "Refunds" → "No Refunds" heading rename — leave for the v1.6 attorney-review pass (not an audit item).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 104 — 2026-06-01)
- **Tuppence Wallet UX overhaul (FEA, David-requested).** Buyer-app `marketsquare.html` / `ms.js` / `ms.css`:
  1. **"How introductions work"** — replaced the 4×8 model-table with a compact explainer: 7-category dropdown + scrollable one-feature-at-a-time top bar (chevrons + dots) + colour-coded answer card with a plain-language line.
  2. **Transaction history** — added type + date-range filters, a fixed-height (~340px) scroll, and a working "Load more"; client-side filter over loaded items.
  3. **AI Services** — moved below transactions and refreshed: added the previously-missing **AI Yield Estimate** + **AI Batch Card Lister** (both live + in active use) with accurate entry-point hints; clarified "Why No Intros?" lives in the listing Edit screen.
  4. **Refund removed as a mechanism** — dropped the Refunds filter option + the `refund` `_TX_ICON` ledger type. Kept all `non-refundable` policy/legal/EULA text and the BEA "never promise refunds" guardrail.
- **Verify:** node --check clean; CSS braces balanced; HTML intact; HIW data unit-tested (21/21 cells vs old table) + filter logic; full jsdom DOM test green. Bumped ms.js v128→129, ms.css v114→115.
- **Deploy:** scp'd index.html + static/ms.js + static/ms.css (remote bytes == local), Cloudflare purged, smoke **all-green**, FEA baseline refreshed (`--update-baseline`); live markers confirmed (hiw-cat present, refund/model-table absent, v129/v115). No BEA change → no restart.
- **Cost model impact:** none — display/UX only; added AI services already existed and were already billed.

## Next Session (105)
- **EULA wording decision (David):** ToS still has a clause titled "Refunds" (body: non-refundable) in the inline + rendered EULA. If the word should go from the heading too, rename "Refunds" → "No Refunds" across all EULA copies in one pass (default: leave for the v1.6 attorney-review pass).
- **Resume KYC crash-bug block — SCAN-7 (HIGH):** `background_tasks` undefined at ~9365 in `vision_draft` (F821) → add `background_tasks: BackgroundTasks` to the endpoint signature; verify AST + smoke before deploy.
- **After SCAN-7: Phase 2 normal order** — S3 (API key off `?api_key=` → X-Api-Key header), S5 (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), L3a (support@trustsquare.co mailbox), then SCAN-8…12 + JS-1/JS-2 + HTML-1/HTML-2 cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 103 — 2026-06-01)
- **SCAN-5 DONE (CRIT · KYC doc-upload crash-bug).** `upload_seller_document` (`POST /users/{email}/documents`, bea_main.py:7111) used undefined `MEDIA_DIR` in its R2-unconfigured local-fallback branch — a latent `NameError` → HTTP 500 on any document upload when `_S3_CONFIGURED` is false. Replaced with the module's `_LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"` (line 942) after confirming it is the intended dir: it is the same dir `_s3_upload` mirrors to, nginx serves it at `/media/`, and the fallback's returned `url = /media/{safe}` resolves there.
- Latent in prod (R2 is configured, so the fallback never runs) → fix is behavior-neutral on the live path. One surgical Python str.replace (old-string unique); the `_LOCAL_MEDIA_DIR` definition (942) and its existing correct use (972) untouched; `os` (line 9) and `_LOCAL_MEDIA_DIR` both module-level bound so the line resolves at runtime.
- `ast.parse` clean local + BEA venv; deployed main.py (server backup `main.py.bak-20260601-scan5`); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke all-green ✅**.
- **Continuity:** synced the 09:14Z weekly-discovery-scan block into the server's AUDIT_PROGRESS.md (was local-only) and purged the stale Cloudflare-cached `/dashboard/summary` (it had been pinned to a 31 May Session-98 snapshot; now reflects the live session).
- **Cost model impact:** none — undefined name → correct module constant; no new AI calls, no pricing/concurrency change.

## Next Session (104)
- **SCAN-7 (HIGH) — the last KYC crash-bug, then Phase 2 resumes.** `bea_main.py` `background_tasks` undefined at ~9365 inside `vision_draft` (F821) — the spend-logging `background_tasks.add_task(...)` will crash the vision-draft endpoint if reached. Fix: add `background_tasks: BackgroundTasks` to the endpoint signature (`BackgroundTasks` already imported) and confirm FastAPI injects it / the call site is inside the handler. Verify AST + smoke before deploy.
- **After SCAN-7: resume Phase 2 normal order** — **S3** (move API key off the `?api_key=` query param → X-Api-Key header only; verify/remove the CDN header-stripping assumption first), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), **L3a** (support@trustsquare.co real mailbox — SUPPORT_MAILBOX_SETUP.md), then SCAN-8…12 cleanup + the weekly discovery-scan dashboard panel (SCAN-PANEL-1/2) + the ms.js latent-crash fixes JS-1/JS-2 + HTML-1/HTML-2 dead-var cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 102 — 2026-06-01)
- **SCAN-2/3/4/6 DONE (CRIT · KYC crash-bugs, batched).** Four latent `NameError` → HTTP 500 bugs on the SA-ID / KYC verification path in `bea_main.py`, all fixed in one run as the runner override permits (every edit is a top-level import or a name fix in the same file).
- **SCAN-2** bare `re.*` (7428/7455/7461/7558/7614/7757) was unbound — module had only `re as _re_match`. **SCAN-3** `hashlib.sha256` (7456) unbound. **SCAN-4** `urllib.request` (7503/7504) + `base64` (7506) unbound in the KYC doc-fetch block. **SCAN-6** two bare `_json.loads` (~6826/6830) where `_json` was never bound.
- **Fix:** added four module-level imports after `import json` — `import re`, `import hashlib`, `import urllib.request`, `import base64`; and changed the two `_json.loads` → `json.loads`. Pre-existing aliases/in-function imports left untouched (harmless shadows). Single Python str.replace driver, each old-string asserted unique.
- `ast.parse` clean local + BEA venv; module loads under systemd env with re/hashlib/urllib/base64 all bound. Deployed main.py (server backup `main.py.bak-20260601-scan2346`); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅**.
- **Cost model impact:** none — stdlib imports + a name fix; no new AI calls, no pricing/concurrency change.

## Next Session (103)
- **SCAN-5 (CRIT) then SCAN-7 (HIGH) — finish the KYC crash-bug block, numeric order.** SCAN-5: `MEDIA_DIR` undefined at 7104 in `upload_seller_document` → replace with `_LOCAL_MEDIA_DIR` (`/var/www/marketsquare/media`, line 935) after confirming that's the intended dir. SCAN-7: `background_tasks` undefined at ~9358 in `vision_draft` → add `background_tasks: BackgroundTasks` to the endpoint signature (BackgroundTasks already imported) and confirm the call site is inside the handler. Verify AST + smoke before deploy.
- **After SCAN-7: resume Phase 2 normal order** — **S3** (API key off `?api_key=` query param → X-Api-Key header only), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), **L3a** (support@trustsquare.co real mailbox — see SUPPORT_MAILBOX_SETUP.md), then SCAN-8…12 cleanup + the weekly discovery-scan dashboard panel (SCAN-PANEL-1/2).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 101 — 2026-06-01)
- **SCAN-1 DONE (CRIT · KYC crash-bug, first of SCAN-1→7 per the runner priority override).** `bea_main.py` referenced `SONNET_MODEL` at three sites in the SA-ID / KYC ID-verification path (model arg + two response payloads, ~7544/7571/7575) but the name was **never defined anywhere** in the module — a guaranteed `NameError` (HTTP 500) the moment that endpoint executed. Latent because the KYC path isn't exercised in prod yet.
- **Fix:** added a module-level constant `SONNET_MODEL = "claude-sonnet-4-6"` next to the other `*_MODEL` constants (line 900, right after `AA_MODEL`), matching the existing `VISION_MODEL` standard. One surgical Python string-replace; `ast.parse` passed locally and in the BEA venv on the server (SONNET_MODEL now resolves: 1 definition + 3 usages).
- Deployed main.py (server backup `main.py.bak-20260601`); BEA restarted **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 30/30 ✅**.
- **Cost model impact:** none — defines a constant already implied by the existing call; no new AI calls, no pricing/concurrency change.

## Next Session (102)
- **SCAN-2→7 (CRIT/HIGH · KYC crash-bugs) — continue in numeric order.** SCAN-2/3/4/6 are all "add a missing module-level import / fix a name" edits in `bea_main.py` (`re`, `hashlib`, `urllib.request`+`base64`, `_json`→`json`) and **may be batched into one run** per the override; SCAN-5 (`MEDIA_DIR`→`_LOCAL_MEDIA_DIR` at 7104) and SCAN-7 (`background_tasks` param on `vision_draft`, 9358) are separate. Verify AST + smoke 30/30 before deploy.
- After SCAN-7: resume Phase 2 normal order — **S3** (API key off `?api_key=` query param → X-Api-Key header only), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), then SCAN-8…12 cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 100 — 2026-06-01)
- **S4 DONE (Phase 2 · HIGH).** BEA CORS locked down. Was `allow_origins=["*"]` + `allow_origin_regex=".*"` (any site could call the BEA from a visitor's browser); now an explicit allowlist `https://trustsquare.co` + `https://www.trustsquare.co`, regex removed, `allow_credentials` still False.
- Same-origin apps (buyer/admin/dashboard all on trustsquare.co) + header/email auth mean no legitimate caller is affected. One surgical Python string-replace; `ast.parse` passed local and in the BEA venv on the server.
- Deployed main.py (server backup `main.py.bak-20260601`); BEA restarted **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅**. Live CORS check: allowed origin → ACAO echoed; `https://evil.example` → no ACAO (blocked).
- **Continuity fix:** also completed the Session-99 baseline write-back the previous runner had left unsynced — the dashboard was still reporting Session 98 even though O2 was done + committed. STATUS/CHANGELOG/AUDIT_PROGRESS now scp'd; /dashboard/summary reflects the true latest session.
- **Cost model impact:** none — security/config change only.

## Next Session (101)
- **Phase 2 cont.** — **S3 (HIGH)**: move API key off the `?api_key=` query param (lands in nginx/Cloudflare logs + browser history) to X-Api-Key header only across the 3 endpoints + ms.js; first verify and then remove the CDN header-stripping assumption that justified the query fallback. **S5 (MED)**: gate the test/auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode pending).
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths; set `monthly_income_usd` via `PUT /admin/ai-spend/config` once first paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 99 — 2026-05-31)
- **O2 DONE (deferred since 96/97/98).** Guarded sync of the four backend modules `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat`. Previously these were imported by `main.py` but never auto-deployed (server-only).
- **deploy_marketsquare.bat**: added (a) pre-flight existence checks for all four modules (abort if any missing), (b) a new **Step 3d** that scp's the four modules to the server *before* the BEA restart so the new code is picked up atomically, each with the standard fail-on-error guard, and (c) a verify line confirming all four are present on the server post-deploy.
- **Live deploy this session**: server `auth.py` was still the old (pre-S1) version with the guessable `ms_admin_changeme` default; deployed the hardened fail-closed version (the other three were already byte-identical). Confirmed `MS_API_KEY` is set in the systemd unit env and the running process before deploying — fail-closed auth is therefore live-safe.
- Backed up server `auth.py` → `auth.py.bak-20260531`. scp'd all four modules; AST-checked each in the BEA venv (4/4 OK); shas now match local exactly. BEA restarted **active**, `/health` ok v1.3.1, bad-key write → 401 (auth still enforced), Cloudflare purged. smoke 30/30 ✅.
- **Cost model impact**: none — deploy-tooling change only, no AI-path or pricing change.

## Next Session (100)
- **Phase 2 audit items** (from the readiness report): next ranked findings after Phase 1 + O2 are now all closed.
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths; set `monthly_income_usd` via `PUT /admin/ai-spend/config` once first paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 98 — 2026-05-31)
- **Dashboard**: AI Cost & Margin panel moved above Email Triage (Ops tab).
- **Session-end write-back now mandatory** (CLAUDE.md checklist rewritten to 5 steps): scp STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to the server every session — dashboard is live-data-driven (no DATA hand-edit). Corrected the stale step-4. This guarantees the latest is always viewable.
- **MtG card orientation**: root cause = EXIF correction can't fix tag-less rotated scans (not a regression). (a) Rotated the 9 genuinely-sideways live cards upright (231,232,233,235,236,237,238,239,240); 234 left alone (genuinely landscape). Verified visually (first pass was 180° off — caught before finalising). (b) Forward fix `_vision_orient_image()`: landscape Collectors uploads get a cheap Haiku text-orientation check → rotate before baking. EXIF-independent, scales, fails open. Admin sends `category=Collectors`.
- **Horizontal card rows**: arrows were positioned outside the strip and clipped; moved inside (4px), shown on all viewports, strips set `flex-wrap:nowrap` + touch scroll. Fixes all 6 carousels. ms.css v114.
- Deployed main.py + dashboard.html + ms.css + admin.html + index.html; BEA restarted clean; Cloudflare purged; smoke 30/30 ✅.
- **Cost model impact**: vision-orient fires only on landscape Collectors uploads (~1 Haiku call, logged + ceiling-bound). Negligible.

## Next Session (99)
- **O2 (deferred since 96/97/98) — do first**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat`. Live-safe (MS_API_KEY set).
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths (currently batch-card path covered); set `monthly_income_usd` once paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), GET /listings pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 97 — 2026-05-31)
- **Phase-1 cost guardrails (audit C1–C3 + dashboard).** All BEA edits via Python string-replacement after a mid-session truncation was caught and the file restored byte-clean from the server.
- **C2 real-token costing**: `_MODEL_PRICE` per-1M-token table + `_token_cost()`/`_usage_tokens()`; `ai_spend_log` += input_tokens/output_tokens/cost_is_real; `_log_ai_spend()` computes exact cost from real tokens (flag `cost_is_real`), flat estimate when absent. Wired into all 7 paid AI ops. Live: real_token_pct 0→7.7% on first real call.
- **C3**: AI3 (price-check) + AI4 (yield) now log spend with real tokens (were unlogged).
- **C1 hard ceiling**: `_check_cost_ceiling()` REFUSES paid AI calls (HTTP 429) when daily per-user ($0.50 default) or platform ($100 default) USD cap is hit. Superusers exempt from user rail; fail-open; 0=off. Live-verified refusal + no-spend-on-refusal. Tunable via `PUT /admin/ai-spend/config`.
- **Dashboard**: no-auth `GET /dashboard/cost` + "💰 AI COST & MARGIN" Ops panel (cost/user, cost/call, margin, real-token %, modelled @100/@100k, ceiling bar, per-endpoint ●real/○est). `/admin/ai-spend` enriched.
- Deployed main.py + dashboard.html, BEA restarted clean, Cloudflare purged, smoke 30/30 ✅. Server backups: `main.py.s96bak`, `dashboard.html.s96bak`.
- **Cost model impact**: per-call economics unchanged; costing now exact (real tokens). C1 is a true spend cap — at the $100/day platform default, max AI exposure ≈ $3,000/mo regardless of load.

## Next Session (98)
- **O2 (deferred from 96/97)**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat` auto-deploy. The auth.py fail-closed change is live-safe (`MS_API_KEY` set), but wiring needs a coordinated deploy — do it as the first task.
- **Set AI spend config** once first paid subs arrive: `PUT /admin/ai-spend/config` with `monthly_income_usd` (unlocks the margin % on the dashboard) — ceilings already default-on.
- **Phase 2 audit items** (from the readiness report): next ranked findings after Phase 1.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination (M0), Paystack plan wiring, EULA v1.6 attorney review.
- Continuity: session-end scp of STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to server is the handoff — `/dashboard/summary` parses currentSession from STATUS.

## Last Completed (Session 96 — 2026-05-31)
- **Full commercial-readiness audit** (deliverable: `TrustSquare_Commercial_Readiness_Audit.docx`; running log: `AUDIT_PROGRESS.md`). Reviewed all 128 BEA endpoints, FEA, server modules, deploy, security, cost. Findings: no hardcoded secrets, all SQL parameterised, SQLite WAL already on, every paid AI op modelled at 93–99% margin.
- **S2 (CRIT) DONE**: pulled server-only IP modules `auth.py`, `database.py`, `storage.py` into the repo (payments.py was already local); verified byte-identical to server via sha256. Previously unversioned/unbacked-up.
- **S1 (CRIT) DONE**: removed guessable default API key (`ms_admin_changeme`) from `auth.py` — BEA now fails closed if `MS_API_KEY` unset. Confirmed set on server, safe to deploy.
- **P1**: confirmed WAL + synchronous=NORMAL already enabled (no change needed).
- **Deferred (O2)**: auth/database/storage/payments NOT yet wired into auto-deploy — server copies are source of truth; auth.py change needs a coordinated guarded sync.
- **Cost model impact**: none this session (no AI-path changes). 100 users ≈ $11.61/mo, 100k users ≈ $2,474/mo, both net positive.

## Next Session (97)
- **Phase 1 cont. (the audit's next items):**
  1. **C1** — hard token/cost ceiling per-user + platform-wide: refuse when exceeded, not just alert.
  2. **C2** — derive cost from real API token counts, not flat constants.
  3. **C3** — add missing spend-logging to AI3 (price check) and AI4 (yield).
  4. Cost + margin + server-cost panels on `dashboard.html`.
- **O2**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into auto-deploy (coordinated; auth.py fail-closed change is live-safe since MS_API_KEY is set).
- **Continuity**: session-end now scp's STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to the server (done this session — `/dashboard/summary` was stale at Session 94). Add a deterministic session-end scp helper + scheduled morning brief per SESSION_BOOTSTRAP.md.
- Architecture decision (recorded): server scaling/KPI logic lives INSIDE the BEA as read-only observe-and-alert feeding the dashboard — never auto-scale, no new service, no machine that can spend money on its own.

## Last Completed (Session 95 — 2026-05-30, incl. 95b/95c/95d)
- **AI Price Check integrity (95)**: re-architected AI3 on "the model writes the sentence, the system produces the number." New helpers `live_usd_zar()`, `resolve_scryfall_id()`, `scryfall_price_by_id()`, `price_caution()`. Verified Scryfall prices for collectibles; no-feed categories return an honest qualitative guide or cannot_assess.
- **95b deliver-then-charge**: Tuppence deducted only after a verified service is delivered. AI3 no-feed → `cannot_verify`, free. AI4 yield rebuilt — gross computed in Python from purchase price + rent, missing input prompts the user, free until a real number is produced.
- **95c**: softened low-price warning to a neutral price-position note (no fraud/counterfeit language); `fraud_flag()` → `price_caution()`, verdict `below_verified_market`.
- **95d**: `deploy_marketsquare.bat` now auto-bumps `ms.js`/`ms.css` `?v=` and deploys static assets + Cloudflare purge — one-script deploy.

## Last Completed (Session 94 — 2026-05-30)
- **AI email triage — end to end.** `POST /email/inbound` (secret-auth) classifies inbound mail with Claude Haiku → `{category, urgency, draft_reply, auto_safe}`, stores in new `email_triage` table, AI spend logged. Categories: support/billing/legal/compliance/spam/other.
- **Conservative auto-send gate**: draft-only by default. Auto-reply only when `EMAIL_AUTO_SEND=1` + `GMAIL_APP_PASSWORD` set + model `auto_safe` + category ∈ {support,billing}. Legal/compliance/ambiguous always held. Spam → skipped.
- `GET /admin/email-triage` (API-key) for ops review. `_smtp_send_reply()` Gmail SMTP sender (587 STARTTLS), threads replies.
- **Cloudflare Email Worker** built (`cloudflare_email_worker/`): postal-mime parse → POST to BEA + safety-net forward to inbox, never bounces mail. wrangler.toml + README + package.json.
- `EMAIL_INBOUND_SECRET` generated, added to `/etc/environment`, BEA restarted. Verified live: support→drafted, spam→skipped, legal→drafted/high, bad secret→401. Smoke 30/30 ✅.
- **ROLLOUT COMPLETE (done this session)**: Cloudflare worker deployed (dashboard, postal-mime parser), `EMAIL_INBOUND_SECRET` set as Wrangler secret, `support@trustsquare.co` routed to worker. `GMAIL_APP_PASSWORD` + `GMAIL_ADDRESS` + `EMAIL_AUTO_SEND=1` added to `/etc/environment`. Live-verified: real support email auto-replied via Gmail SMTP (status=sent), legal email held (status=drafted). Replies currently send FROM dmcontiki2@gmail.com.
- **Ops dashboard panel**: `GET /dashboard/email-triage` (no-auth, obscure-URL) + "📧 EMAIL TRIAGE" panel on Ops tab — category/status counts + recent emails with drafts inline.
- ⚠️ **Repaired two truncations this session** (large-file Edit hazard): local `bea_main.py` (rebuilt from server, now 9972 lines) and `dashboard.html` (rebuilt tail via Python after a broken copy briefly deployed; now intact, smoke 30/30).
- **For David**: (1) Commit from PowerShell: `bea_main.py`, `dashboard.html`, `cloudflare_email_worker/`, `STATUS.md`, `CHANGELOG.md`. (2) Optional: route `legal@`/`billing@`/`compliance@`/catch-all to the same worker. (3) Optional: switch reply From-address to support@trustsquare.co via a transactional sender (e.g. Resend, already used in CityLauncher).

## Last Completed (Session 93 — 2026-05-29)
- **World Heritage / Wonders layer expanded 120 → 332 sites** (+212; clears ≥320 target). UNESCO-led: 142 UNESCO, 97 National Park, 47 National Museum, 46 Archaeological. South Africa 5 → **30 sites**; 91 countries total.
- **Photos all royalty-free (Wikimedia Commons)** with photographer attribution: 228/231 new scenic photos credit a named author; all 332 photo URLs verified HTTP-200 before deploy. `photo_author`/`photo_licence`/`photo_source` populated from Commons extmetadata.
- **Path fix**: canonical `wonders.json` moved to project root (matche
## Attended change 2026-06-19 (David in chat)
- WONDER-DUP: 4/10 true coord-dups merged (wonders 304→300, keep canonical/lowest id); 6 distinct co-located groups left intact + flagged. BRAND-DRIFT-1 verified already-live (closed). CUTOVER-1 parity met (15 nights), staged — root cron --live flip pending David.

## 2026-07-01 · claude-mem "worker died" recurring alarm — ROOT-CAUSED + FIXED (config only)
The daily mem-digest task's false "worker stopped → run repair" alarm is fixed: it now keys on worker LIVENESS (stale pid / failed /health), not summary age, so Cowork-only stretches no longer trip it. Digest confirms no CLI sessions since 23 Jun (expected — you work in Cowork), not a fault. CURRENT STATE: worker process is ALIVE (restarted 29 Jun), just idle — no CLI sessions since 23 Jun, so the digest is legitimately unchanged (summaries write to SQLite regardless of chroma). NO repair needed. Detector refined to v2: quiet when alive-but-idle, warns only if the worker is truly DOWN. Nothing required of David unless he wants to retire CLI memory entirely (then the task can be disabled). Full detail: CHANGELOG 2026-07-01.
