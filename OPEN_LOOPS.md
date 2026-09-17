# OPEN LOOPS — the one place that answers "what is open, what is next"

**This file is the single source of truth for open threads on TrustSquare.**
It exists so *Claude* is the integrator, not David. Everything else (STATUS.md prose,
audit reports, chat threads) FEEDS this file; David reads only this.

## The rule (structural, not a reminder)
1. **Every session reads this file FIRST** (it is in the /start boot-up).
2. **Every session that opens or closes a loop EDITS this file LAST** — before ending.
   A loop that lives only in a chat transcript does not exist. Put it here or it's lost.
3. **Ranked top-down. David reads until he stops caring and stops.** He never sorts.
4. **One line per loop.** Detail lives in the linked file, never here. If this file grows
   past one screen, that's the signal to CLOSE loops — never to start a second list.
5. Owner tag: **[C]** = Claude can just do it (reversible → done, then reported).
   **[D]** = genuinely David's call (deploy / spend / legal / irreversible).

Durable "do it later" (not active) stays in **BACKLOG.md → Deferred items**. Not duplicated here.

**Last reconciled: 2026-08-20 (attended).** Previous reconciliation 14 Aug — six days in which
this file was not the integrator it claims to be: L2 had been class-fixed on 16 Aug and still sat
here as live work. Rule 2 says the session that closes a loop edits this file LAST; the honest
reading is that sessions closed loops and did not. **1 DAY to soft-public (Fri 29 Aug) · 4 days to full launch (Mon 1 Sep) — RUL-001.**
*Day-count refreshed 2026-08-28 by the pre-soft-launch third-party sweep. It was written on
20 Aug and had quietly aged eight days into a false statement — an undated countdown is the
same defect class as an undated status assertion (the ONETAP_SETUP.md "(this is today)" lesson).*

---


## 🔴 BLOCKING NOW
*(nothing proceeds until these clear)*

> **Section state 2026-08-28: the one row printed here (B1) is DISCHARGED and no longer blocks
> anything.** It is left in place because this file has no compiler and edits stay additive
> (CHANGELOG-COLLISION-1 class) — it moves to CLOSED at the next attended reconciliation.
> **Do not read this heading as "secrets rotation blocks launch". It does not, and has not
> since 22 Aug.**

> **26 Aug 2026 — B1 is DISCHARGED by probe; it is sitting in the wrong section.**
> The third-party sweep re-verified it this morning: `SECRETS_REGISTER.md`'s "Still burnt" table is
> EMPTY, **RG-0146 and RG-0147 are LOCKED and green on today's ledger run**, and the row's own text
> has said "ROTATION COMPLETE" since 23 Aug. It stays printed here only because this file has no
> compiler and edits are kept additive (CHANGELOG-COLLISION-1 class) — **move it to CLOSED at the
> next attended reconciliation.** Residue, neither of them blocking: David deletes the two superseded
> Cloudflare tokens; FOUNDERS_ID_SALT rotate-or-accept is Claude's pending call.
>
> **28 Aug 2026 — FOUR OF THE FIVE ITEMS THIS NOTE NAMED AS BLOCKING ARE DISPROVEN BY PROBE.**
> The 26 Aug wording below is kept for the record and corrected here rather than silently
> overwritten. Re-probed live this morning (05:0x–05:2x UTC) by the pre-soft-launch sweep:
> `GET /launch-api/prospects/list` → **401 `X-Launch-Key required`** (the anonymous-PII hole is
> shut and deployed) · `/static/post_deploy_status.json` → **`migrations ok, "none pending"`**,
> generated `2026-08-28T03:08:38Z` (the chain is unjammed) · full `script-src` CSP served on both
> `/` and `/terms` (`default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com
> https://cdnjs.cloudflare.com; … object-src 'none'; frame-ancestors 'self'`) · origin **port 22
> OPEN 3/3** (`SSH-2.0-OpenSSH_9.6p1`). **Only the fifth is still true.**
>
> **What genuinely threatens 29 Aug, as of 28 Aug, is exactly two things and they are the same
> thing twice — nothing would tell David the site is down over launch weekend:**
> **(1)** the external uptime watcher is **built 22 Aug and still not deployed — day 6**
> (L8 below · ledger RG-0138 · DAVID_QUEUE D4), and **(2)** the RED-alert Resend key in
> `/etc/marketsquare/resend.watch.conf` is **dead — day 3** (DW-076 · DAVID_QUEUE D3), re-probed
> from the box at 04:39 UTC today and still refused. Both are David's by RUL-037 (root on the box
> + credentials). Neither is code and neither needs a deploy.


| # | Loop | Owner | Single next action | Opened | Source |
|---|------|-------|--------------------|--------|--------|
| B1 | **Production secrets exposed, twice — ROTATION IN PROGRESS 22 Aug.** Nine credentials rotated and PROBED (5 self-issued + Resend 422 + Paystack 200 + JWT). Two structural defects fixed: `/etc/environment` was 0644 world-readable holding nine secrets (now 0600; `msdeploy` had a login shell), and a correct write reported success while production held the revoked Paystack key — card payments were down unreported. The exposure list in DW-029/DW-057 was under-counting by nine. Inventory now machine-checked: `SECRETS_REGISTER.md` + RG-0146 (red until clean), RG-0147 LOCKED. | [D]+[C] | **ROTATION COMPLETE — corrected 23 Aug by the third-party sweep (this cell was mid-rotation text):** SECRETS_REGISTER.md 'Still burnt' table is EMPTY (REGISTER_VERIFIED 2026-08-22) and RG-0146 is LOCKED and passing ('no credential is still marked BURNT'). All ten resolved: HETZNER_S3 ×2 (rotated, actually Cloudflare R2, media-scoped), ANTHROPIC_API_KEY, CF_CACHE_TOKEN, EMAIL_INBOUND_SECRET, RELAY_INBOUND_SECRET, NUMISTA (rotated+probed), JUSTTCG (rotated then deliberately UNSET — licence, RG-0148), MS_DEPLOY_TOKEN (re-minted), COMMAND_SECRET (deleted — nothing consumed it), TRAVELPAYOUTS_TOKEN (UNROTATABLE-ACCEPTED, dated reasoning). Google ACCOUNT password changed 22 Aug. Residue: David deletes 2 superseded Cloudflare tokens; FOUNDERS_ID_SALT is Claude's pending call. CLOSE this row at the next attended reconciliation. | 2026-08-07 / 2026-08-20 | DAILY_WATCH DW-029, DW-057 · SECRETS_REGISTER.md |

## 🟠 LIVE LOOPS (open, need to move) — ranked

| # | Loop | Owner | Single next action | Opened | Source |
|---|------|-------|--------------------|--------|--------|
| L5 | **Fix-agent phase-aware + operational path proven** — pre-launch now: only legal+costly gate, design gets IMPLEMENTED not backlogged (David 9 Aug scoping); runs as root (repo owner), shadow-clean on the real queue. Agent still OFF. | [D]+[C] | Deploy -> re-run the shadow dry-run as root with MAINT_PHASE=prelaunch -> read the design changes it proposes on real faults. Then close: state-dir out of repo + confirm the server can pass its own anonymity gate. | 2026-08-09 | this session |
| L6 | **BIT-AIM-1: FEA probes mis-aimed** — BIT board live (13's timer works) but degraded 5/8: B-FEA-SHELL/EXAMPLE/CONTRACT all fail because BIT_BASE=localhost:8000 carries no FEA. Per-probe base needed (nginx+gate-token on box, or edge+named-UA). | [C] | Tomorrow's maintenance loop (or attended): registry per-probe base + runner resolve + verify on the 15-min board. | 2026-08-11 | changelog.d 2026-08-11-b4-6 |
| L8 | ~~External uptime monitor~~ **✅ DEPLOYED 28 Aug 2026** — Worker `trustsquare-uptime` on Cloudflare's edge, cron `*/5`, PROBED `ok:true kv:true` 11:31:54 UTC. **RG-0138 promoted OPEN → LOCKED.** Built 22 Aug, undeployed 6 days, shipped on the eve of soft-public. *Residual, stated not hidden: the PROBE half is proven, the ALERT half is not — no successful send has been observed. First heartbeat 06:00 UTC Sat 29 Aug; if it does not arrive by ~08:30 SAST the alert path is still dead.* | [D] done | Check the inbox Sat morning, then roll LAST_HEARTBEAT forward in `ops/cloudflare/UPTIME_DEPLOYED.md` | 2026-08-14 | closed 2026-08-28 |
| L3 | **SCOREBOARD-1 shipped-not-live** — agent + guards + nightly wiring in repo (7/7 tests); probes OFF until enabled. | [D] | Next deploy carries it, then run `enable_scoreboard.bat` once. | 2026-08-03 | CHANGELOG SCOREBOARD-1 |
| L7 | **Tooling-through-the-gate** — GATE-ENFORCE-2 (13 Aug) raises the origin token gate; on-box/edge tooling reading data endpoints anonymously (maintenance-loop intake, server smoke data probes) will 401. UA-EDGE-1's sibling. Ledger already fixed (reads via reviewer cookie). | [C] | NARROWED same day: agent verified UNAFFECTED (localhost default; RG-0053 now asserts it structurally). Remaining: attended off-box tools (fault_reconcile, cost sweep) need the reviewer cookie when next used; server smoke data probes need cookie or localhost vantage. | 2026-08-13 | changelog.d 2026-08-13-gate-enforce-activated |

## ⚪ DECISIONS AWAITING DAVID / COUNSEL — ranked

| # | Decision | Owner | Single next action | Opened | Source |
|---|----------|-------|--------------------|--------|--------|
| D4 | **privacy.html UK/US/AU supplements** — verified 2 Aug: NEW work, never drafted (EULA got §13.6 Country Schedules on 23 Jul; privacy.html has zero UK/US/AU content). | [C] | David confirms scope → Claude drafts. | 2026-07-23 | STATUS.md S149 |

| D7 | **Wave-1 send: how do email recipients get past the pre-launch Unlock gate?** Deep links + all 9 showcase adverts are DONE; a cold click lands on the editor-PIN gate (by design, REMOVE-BEFORE-LAUNCH). Either wave-1 waits for launch, or Claude builds a read-only `?listing=` preview that bypasses the gate for a single advert (data already publicly readable pre-launch). Test send follows this call. | [D] | Rule: wait-for-launch / build preview bypass. | 2026-08-02 | this session |
| D9 | **FLIP-DRILL-1: pick the hour** — runbook ready (`FIRE_DRILL_RUNBOOK.html`). DEFERRED by David 5 Aug 2026 ("needed, just not now") — STANDS OVER till after launch (David, 11 Aug). | [D] | David names a quiet hour when ready; Claude keeps the log. | 2026-08-03 | this session |
| D10 | **Travelpayouts tours programs — RESUBMITTED 22 Aug 2026 (David's word, per RUL-041).** The 5 Aug decline (*'website under development or not yet ready'*) blocked GYG · Viator · Welcome Pickups · Booking.com and 22 others; 26 programs auto-connect on approval. Submitted with the site answering publicly and the changed face being real (EULA v1.14 live, gate down, honesty labelling in flight) — not a resubmit-unchanged. Aviasales flights Data API unaffected. **TRAVELPAYOUTS_TOKEN is UNROTATABLE** (one permanent token per account, copy-only, verified on the API page 22 Aug) — accepted risk, reasoned and dated in SECRETS_REGISTER.md, policed by RG-0146. | [C] | **OUTCOME READ 24 Aug 2026 — DECLINED AGAIN, same reason.** Probed at app.travelpayouts.com (project Trustsquare, ID 758984): *"20 programs are currently unavailable… Your website is currently under development or not yet ready. Please complete setting up your site and re-submit your Project for review."* Available **26** / blocked **20** — Booking.com, Viator and GetYourGuide all still blocked. The 22 Aug "we've connected you to relevant brands" email is their generic template, NOT an approval (evidence-ladder: email READ said yes, dashboard PROBE said no; the probe wins). Per RUL-041: do NOT resubmit unchanged — the next submit waits until the site's changed face is materially different (soft launch, 29 Aug, is the natural moment, and the timing call is David's). Their dashboard is meanwhile offering **+25% GetYourGuide rewards, expiring 24 Aug, to switch the Drive loader back on** — declined; all five Drive functions stay Off. Safe lane BUILT instead: travelpayouts_partners.py (TP-LINKOUT-1), server-side 302s, host allowlist, dark by flag, RG-0181. Original standing rule unchanged: commercial lane only — server-side or link-out, NEVER a TP script (RG-0025). | 2026-08-05 | RUL-041 · scheduled follow-up |
| D11 | **Maroushka's TS-0022 letter drafted** — the retest letter IS the remediation (9 pre-fix covers need her re-upload; class fix RG-0047 live). | [D] | Say "send" (chat) or POST retest-send. | 2026-08-11 | Records/FAULT_RECONCILE_2026-08-11.md |
| D12 | **Arm the Maintenance Agent** — deploy DONE (David's 09:08 TSL, release 127b6a6): BIT timer posting, first Tier-2 verdict honest NOT READY (patch-apply), MAINT-B4-6 rewrite fallback built+proven, migration 015 re-runs Tier 2 next deploy. | [D] | Next deploy (tonight's nightly or /TSL) → read static/maint/b4_tier2.json; if READY: one paste from MAINT_ARMING_RUNBOOK.md (after a /backup). | 2026-08-11 | changelog.d 2026-08-11-b4-6 |
| D14 | **Designer-role binding** (5 Aug boundary redraw item 2) — guidelines now written (DESIGN_CHANGE_GUIDELINES.md); until bound, you are the gate by default. | [D] | Rule: you / a design agent / both. No urgency before launch. | 2026-08-11 | MAINTENANCE_AGENT.md amendment |
| D15 | **Study & Work-Abroad Advisor (Maroushka's idea, 22 Aug — RUL-042).** Positioning RULED: preparation is ours, based on actuals (possible / typically needed / viability, risks, opportunities); partner education & immigration agencies take the Dossier and provide the actual plans and guidance — that handoff IS the introduction. Assessment on disk: ~$0.50–1.00/report vs 5T = $10, existing 5T deep-dive class, no paid feed, ~70% reuse, MVP 3–5 sessions (one corridor first). | [D] | TEASER: DECIDED 22 Aug (David — 'build it now, no risk to baseline') — built as SAW-1 (static page + banner + manifest line, RG-0158 OPEN), rides the next deploy. UPDATE 23 Aug: 5T CONFIRMED + build GREENLIT + work-route example added (RUL-043); videos full-length, SHELVED until spec approved. Remaining to David: deploy timing (rides next TSL) · agency outreach approach (education + placement agencies — sending is his) · the video unshelve moment. Plus a business action: recruit 2–3 founding education/immigration agencies (same lane as travel agencies). | 2026-08-22 | RUL-042 · STUDY_WORK_ABROAD_ADVISOR_ASSESSMENT — nice.docx |
| D16 | **Founders Badge — parked (RUL-047).** All customer-facing mention removed 23 Aug; machinery dormant (env-gated OFF, never minted). Reserved for ONE once-off occurrence as a premier-subscription injection once a customer base exists. | [D] | David names the occasion (Christmas / Black Friday class) post-settling; no urgency, no session may re-surface badge copy before it. | 2026-08-23 | RUL-047 · PRICING_CANON §4 |

> **28 Aug 2026 — D16 DISCHARGED BY RUL-060** (that is DAVID_QUEUE D7, distinct from this
> file's D7 row): David named and spent the once-off founders occasion as the LAUNCH WINDOW —
> `enable_launch_special.bat` run 28 Aug, hard close 2026-09-01, CityLauncher wave lane only;
> the orchestration agency lane stays clean under RUL-047's needles, and the park resumes
> automatically post-window. The D16 row moves to CLOSED at the next attended reconciliation.

## ✅ CLOSED — last 7 days

- **L2 CLOSED 2026-08-20 (reconciliation — it had actually been fixed on 16 Aug and nobody moved the row).** "git-on-FUSE stale .lock files every commit" is class-fixed, not worked around: **GIT-LOCK-3** made both lanes self-heal — every git-writing .bat calls `git_unlock.bat` first (clears a stale lock ONLY when no git.exe is running, so it can never race a live commit), and every sandbox git WRITE runs `scripts/git_unlock.py`, which RENAMES lock-class files into `.git/stale_locks/` because FUSE blocks unlink. All sandbox reads use `GIT_OPTIONAL_LOCKS=0` so read-only git can never plant a lock. EVIDENCE: both files present on disk, and tonight's full ledger run reports **`[  ok  ] RG-0015`**, which tripwires the whole class LIVE (a lock stranded >60 min turns the ledger red the same day). The row survived four days past its own fix — that lag is the reason this file now carries a "last reconciled" stamp.

- **D8 CLOSED 11 Aug 2026** — Stays/B&B fully live: code rode the 05:06 /TSL, David ran media_push, STAY_IDS already wired (336/337/338), outreach hrefs already flipped (verified idempotent). 
- **D13 CLOSED 11 Aug 2026** — TS-0018 referent named by David = the dashboard Launch Blockers column; removed same day (VIZ-MAPS-4); fault closed.

- **L4 CLOSED 11 Aug 2026** — the tester fault channel is LIVE in fact: flag on, 30 reports filed through it, ACKs + retest letters flowing (register at 21 verified / 4 closed after today's AMBER-SWEEP-1).
*(short tail; drop rows older than 7 days)*

- **D10 CLOSED 5 Aug 2026** — David approved the fault-intake privacy wording; clause landed in privacy.html as §13 "Reporting a problem" (Changes renumbered §14). Contact = support@trustsquare.co (matches §9 rights address). Rides the next deploy; required-before-flag-opens-wide condition is now met on disk.

- **[D] AFFILIATE GATE CLOSED 2 Aug 2026 (evening)** — David's ruling, attended: gate cleared, **full Drive on**. Presented with the on-disk state (SS6.1A disclosure live in EULA v1.11; counsel ratification + accountant tax/VAT treatment outstanding; Drive auto-inject broader than the curated gate) David chose "Gate cleared — full Drive on". All Drive monetization functions enabled on trustsquare.co ("running at full capacity"). Residual items now ORDINARY follow-ups, not blockers: counsel ratifies SS6.1A wording at next revision; accountant classifies TP commission income (foreign-source, HK payer) when it first accrues; per-click-out disclosure line ships with the planner UI. data_flights/tours flags are no longer legally blocked. Ref: changelog.d TP-DRIVE-2.
- **D1 CLOSED 2 Aug 2026** — "publish the latest EULA": already true at origin (lifecycle clauses live as §§4.6–4.9 + §§14.5–14.6 since v1.10, 23 Jul; v1.11 current on terms.html + in-app gate + modal). Found & fixed in closing: the CDN edge was serving stale **v1.3 (17 May)** on /terms — purged same day, class locked as ledger **RG-0024** (edge stamp must equal origin stamp).
- **D5a CLOSED 2 Aug 2026 (night)** — all NINE email-showcase adverts live and deep-linked: property 315–317 (28 Jul), cars 318–320 (28 Jul, healed: real specs replacing cloned Hilux fields, sort prices fixed, super flag + false attestation cleared then correctly re-stamped), adventures 321–323 (born clean via migration 001). All four templates flipped (2 anchors per card). Remaining test send rides the D7 gate ruling.
- **L1 CLOSED 2 Aug 2026 (evening)** — the pending release SHIPPED via the ONE-deploy engine's first live run: v421→v422, health ok, deep-link ms.js + Saturday's work + DEPLOY-CONSOLIDATION-1 + the Stays sweep all live. MSJS-DRIFT / VERSION-KEY flags clear next audit.
- **D5b CLOSED 2 Aug 2026** — David's ruling: standardize on **"Stays"**. Swept buyer/seller-facing surfaces (filter chip + ADV-SYNC-1 state loop + seller picker + onboarding dropdown + 2 home tiles; ms.js/marketsquare.html, node --check green, live-verified on v422). EULA's formal "Adventures Accommodation" untouched by design — renames at the next counsel revision.
- **D6 CLOSED 2 Aug 2026** — David's call: proceed as-is; post-filing disclosure of reverse-intro + Rank accepted as a small risk alongside the new referrals. **Wave 1 is NOT blocked on counsel.** The drafted attorney email stays in Gmail drafts should he still want the answer.
- **D2 / D3 REMOVED 2 Aug 2026** (David: "re-open when the time is right") → parked in BACKLOG.md → Deferred items; counsel register (LEGAL_VERSIONS.md A6) still tracks the fork consolidation as the authority.

- **[H1] OPEN 24 Aug 2026 — Swap-harness bench command (the missing gauge).** The AI swap harness exists (ai_provider.py seam: AI_ACTIVE + ADAPTERS{anthropic,openai,scaleway,gemini} + TASK_MODEL; gauges: failover/eval_golden_set.py). Missing: ONE command — scripts/harness_bench.py <provider> <model> — that runs the golden set against a candidate via the seam and prints a champion-vs-candidate scorecard (pass rate, $/Mtok in+out, latency) so a RUL-009 decision takes one command, not a research errand. Trigger example: OpenAI's 21-Aug GPT-5.6 Sol promo cut ($4/$20 through 21 Nov 2026). While building it: verify TASK_MODEL's openai rows are current — the 11-Jul vendor doc flagged them as gpt-4o-era. Selection stays MANUAL per RUL-009; the bench measures and executes only.
- **[H2] WATCH 24 Aug 2026 — DeepSeek Harness (agent runtime, NOT the app seam).** MIT-licensed plugin-first agent runtime released 13 Aug (deepseek-ai/deepseek-harness, v0.1 dev preview, ~95k stars in 2 days). Different layer from ai_provider.py: it runs AGENTS (control loop, tool registry, sandbox, sessions); our seam is in-app inference plumbing. Ruling context: supplier-fallback doctrine + pre-launch freeze say a 5-day-old v0.1 framework never enters the live money path. Possible POST-LAUNCH fit: ops/auditor-agent runtime, or host for the H1 bench. Re-assess at /housekeep vendor re-scan once it has a stable release + security track record. Bias note recorded: assessed by Claude (Anthropic); Harness is positioned as a Claude Code rival.

---

## 2026-08-30 (appended — append-only, this file has no compiler)

- **[C] ZOOM-HMI-1 — the category view becomes a narrowing funnel. DESIGN RATIFIED, UNBUILT.**
  David ratified it 30 Aug (RUL-076) after tapping both prototypes. Build rides the FIRST
  POST-LAUNCH window alongside the RUL-065 listing-friction batch (RG-0205/0206/0207) — same
  window, same discipline. Spec: `ZOOM_HMI_SPEC.md`. Ledger: RG-0221 (OPEN; prints READY TO LOCK
  when it ships). **Binding constraint from David: he sees it on the ACTUAL APP before the field
  does** — flag-dark in the real app, locally first, then the gated sandbox RUL-075 already
  schedules for 30 Oct (shared, not duplicated).
- **[D] ZOOM-HMI-1 arming.** Flipping the flag in the field is David's act, not the CTO's — it
  changes the front door of every category. Nothing to do until the build lands.
- **[D] Travel funnel endpoint.** The natural conclusion for tours/stays/guides is a PLAN, not a
  listing — the Expedition Dossier handed to a partnered agency, which IS the Tuppence
  introduction. Commercial shape, David's call, needed before the travel lane is armed.
- **[C] SQUIRE-1 — the Pro subscriber's personal agent. RULED 30 Aug (RUL-077), UNBUILT.**
  Spec: `SQUIRE_SPEC.md`. Ledger RG-0224 (OPEN). **Builds AFTER Zoom** — a brief is a Zoom path
  plus prose, so Squire first would write the matching engine twice. Same flag-dark discipline:
  David sees it on the real app before the field, arming is his act.
- **[D] Does Pro ($20) include Global buyer reach ($5)?** Without it a Pro subscriber's Squire is
  confined to one city, which blunts its best cases (the collector hunting nationally, the parent
  comparing tutors across a metro). CTO recommendation: include it — reach is a query filter, not
  a cost. Bundling is a pricing call, so it is David's. Needed before Squire's build starts.
- **[D] DISCHARGED 30 Aug (RUL-078) — "Does Pro include Global reach?"** Answered: **yes, automatically.**
  The [D] row above is left in place because this file is append-only; it moves to CLOSED at the next
  attended reconciliation. Residue is a build task, not a decision: `_buyer_tier()` must consult the
  seller subscription (RG-0224 criterion 9). Squire's build shape and acceptance criteria are also
  APPROVED and closed to re-litigation.
- **[D] Pricing page — two different $5 products.** *Starter* ($5, seller slots) and *Global* ($5,
  buyer reach) are separate purchases and Starter does NOT include reach. Needs the two axes drawn
  visually apart before the pricing page is next touched. Naming/positioning is David's.
- **[D] ONE $5 TIER — principle ruled 31 Aug (RUL-080), mechanism still David's.** Supersedes the
  "two different $5 products" row above, which is left in place (append-only). Three $5 products exist
  and ALL pre-date 30 Aug: Starter (slots), Global (buyer reach), Agency Pro seat (RUL-048). CTO
  recommendation: fold Global reach into Starter. **Not executed on launch eve** — `wishlist_subscriptions`
  is a live Paystack-backed table. Scheduled: first post-launch pricing pass, before the pricing page
  is next touched.

- **D10 — 3rd resubmit 2 Sep 2026 06:00 SAST** (post-launch, David's word). Dashboard: "We're reviewing your Project… a few days." Outcome check by PROBE ~7 Sep; a decline goes to contact support in writing (RUL-041).
- **D10 — OUTCOME READ 7 Sep 2026 07:00 SAST: DECLINED a 3rd time (PROBED, dashboard banner).** "20 programs are currently unavailable" — two reasons now: the old "under development or not yet ready" PLUS a NEW one: "doesn't currently have enough traffic… stable monthly traffic for at least three consecutive months." Submit button active again (review concluded). GYG/Viator/Booking.com still blocked; Aviasales flights unaffected. Per RUL-041 NOT resubmitted; support note DRAFTED at TRAVELPAYOUTS_SUPPORT_NOTE_2026-09-07.md asking which reason is deciding and what "not ready" means. If traffic is deciding, earliest resubmit ~Dec 2026. **Reserved to David: send the note.** Ref: changelog.d/2026-09-07-tours-review-outcome.md

## 2026-09-14 (appended — append-only, this file has no compiler)

- **[C]+[D] RUL-126 — THE BASELINE CHANGES ONCE.** All open post-launch design work is now ONE
  batch, plan of record `BASELINE_BATCH_2026Q4.md`. Build order: Zoom (RG-0221) → DCB-001
  (RUL-127) ∥ credential claims (RG-0216) + private-seller VEL entries (RUL-129) → Squire
  (RG-0224) → Quick app /quick/ (RUL-124/125) → $5 fold (RUL-128) → funds gauge (RG-0203) →
  agency letters (RG-0346). Flag-dark throughout; **arming is David's act.**
- **[C] REPAIR LANE, not in the batch:** the false "You're offline" banner, and no service worker
  controlling the live page — the second blocks web push (RUL-122) and the install offer
  (RUL-123), and the Quick app shares that worker. Fixed on their own schedule per RUL-126(c).
- **[C] CLOSED 14 Sep — listings 383 and 384 deleted** from production via the
  seller-authenticated route; both re-probed 404. The "keep or delete" row is answered.
- **[C] CLOSED 14 Sep — DCB-001 gate filled** (RUL-127), eleven weeks after the dossier was scored.
- **[D] CLOSED 14 Sep — RUL-080's reserved mechanism chosen** (RUL-128): fold Global into Starter.
  Residue is a build task, not a decision: migrate live `wishlist_subscriptions` rows at the same
  price, never cancel-and-re-sell.
- **[D] CLOSED 14 Sep — the Property / Local Market credential gap ruled** (RUL-129).
- **[D] STILL RESERVED:** the travel funnel endpoint (Expedition Dossier as the introduction —
  blocks ARMING the travel lane, not building Zoom) · designer-role binding (D14) · the Agency
  Pro $5 seat (RUL-048), which RUL-128 deliberately did not fold.
- **CORRECTION to the 2 Sep BUILD_QUEUE:** RG-0205/0206/0207 (listing-friction batch) shipped
  4 Sep and RG-0208 (intro reminder ladder) is in `bea_main.py` — all four were being carried as
  open work by a generated file that had gone stale. Verified in source, not recalled.

### 2026-09-14 (appended) — the repair lane SHIPPED, and the Wednesday build is scheduled

- **[C] CLOSED — OFFLINE-TRUTH-1 + SW-REGISTER-1 are LIVE on trustsquare.co.** Deploy ref advanced
  to ceba06b via the RUL-092 relay; `ms.js?v=628` serving. VERIFIED IN DAVID'S OWN CHROME, not from
  the API: one service-worker registration at scope `https://trustsquare.co/`, state `activated`,
  **`navigator.serviceWorker.controller` true** (it was null on 13 Sep) · no banner while online ·
  copy reads "You're offline — some things won't load" · a spurious `offline` event fired at the
  live page did NOT raise the banner, which is the exact latch that put the false message in front
  of David. Zero console errors. Ledger RG-0363 + RG-0364 green.
- **This unblocks RUL-122 (web push) and RUL-123 (add-to-home-screen at first publish)** — both were
  built and unreachable because nothing controlled the page.
- **[C] SCHEDULED — the RUL-126 baseline batch build, Wed 17 Sep 2026 18:00 SAST** (trigger
  `trig_015ezDrj6JKMhnLc2u2Rt2Rr`, bound to David's PC, push + email on completion). Brief carries
  the build order, the rendered-app proof standard, and the working rules (mount str-replace, git
  unlock, diff-against-server, ?v= bump, request_deploy.py).
- **[D] ONE CLICK, AND IT IS THE ONLY ONE:** the task was created on `claude-opus-5`. David asked
  for **Fable 5.1 at Extra effort**. A device-bound task's model CANNOT be patched through the API
  — the server refuses it ("set the model inside the signed session_request edit"), because the
  binding signs the prompt to that machine. **David sets model = Fable 5.1 and effort = Extra in
  the task's settings in the Claude desktop app.** Stated rather than left to be discovered at
  18:00 on Wednesday.

- **[D] NEW 14 Sep — Buzz EULA clause drafted, NOT applied.** David asked for Buzz to be provided
  as-is with a both-sides off switch, written into the EULA. Drafted at
  `EULA_CLAUSE_BUZZ_DRAFT_2026-09-14.md` and routed to the EULA revision track rather than edited
  in, because that document has an external review track. Three corrections are in the draft:
  "voetstoots" is a sale-of-goods term and does not reach a service (and CPA s55/s56 cannot be
  contracted out of); "no complaints allowed" cannot be written at all; and CPA s49 requires the
  limitation to be conspicuous and acknowledged, not buried — which is why the same words already
  appear on screen where the switch is (built and live-bound 14 Sep). **David's call: adopt, amend,
  or send to counsel.**
- **[C] DONE 14 Sep — Buzz closing is symmetric.** One close ends it both ways, the other party is
  told without blame, and only the closer can reopen. Fixes a real flaw in Claude's first build: a
  per-side switch let the party who switched off keep buzzing the other — a one-way megaphone, and
  in an employer/worker pair that is worse than no channel. 34 endpoint checks green; close and
  reopen driven in a rendered browser.
- **[C] DONE 14 Sep — Buzz capacity fault found and fixed.** David asked what it costs if it
  escalates. Bandwidth is a rounding error (37 GB/month at 500k pairs against 20 TB), but `/buzz`
  was a sync endpoint holding one of ~40 shared worker threads for up to 8s (slow push) or 20s
  (email) — **the same threads that serve listing pages**, so 2–5 buzzes/sec would have saturated
  the SITE. Push now capped at 2s (intro lane keeps its 8s default), email queued off the request,
  and `buzz_log` given 90-day retention — it was the only part growing without a ceiling (23 GB/yr
  at that size on an 80 GB disk). Working: `BUZZ_CAPACITY_2026-09-14.md`. 40 endpoint checks green.
- **[C] NOTED, not caused by Buzz:** `database.py` sets no `busy_timeout`, so SQLite write
  contention surfaces as an immediate "database is locked" rather than a short wait. App-wide and
  pre-existing; one line whenever that file is next open.
- **[D] NEW 14 Sep — which icon installs, and for whom.** David's requirement ("it will link to the
  trustsquare app to then download and create an icon") and RUL-124(d) (the Quick app has its own
  coloured tile) point at different icons. Claude's read, built into the explainer not the code:
  the LISTER gets the Quick tile at first publish, the person she SENT it to gets the full
  TrustSquare tile. `genie/QUICK_SPREADER.html`. **One icon cannot serve both — David's call.**
- **[D] 14 Sep — the Quick app needs ONE more deploy.** LANDSCAPE-1 (the sideways cut-off) and
  ANOTHER OPTION (the free-text area tile, [[RUL-135]]'s sibling — FILTER-DATA-2 applied to the
  spreader) are in `quick.html` and `genie/HARNESS.html` and verified, but not live.
- **[C] NOTE for any concurrent session, 14 Sep:** this session holds `quick.html`,
  `genie/HARNESS.html`, `scripts/regression_ledger.py` and the top of `CHANGELOG.md`.
  Nothing else in the tree is modified — re-read before editing those four.
- **[C] DONE 14 Sep — identity is proven everywhere it is acted on, and it enforces by default.**
  Twenty-three endpoints behind the public app key took a person's identity from the request — Buzz,
  account closure, banking, KYC documents, ID upload, identity verification, Tuppence balance and
  history among them. All bound (`_actor` / `_admin_only` / `_agency_admin_or_refuse`); Buzz also
  needs the §3.8 tick, with first switching it on as the acceptance moment. 43 checks green, the
  acceptance screen driven in a rendered browser, RG-0371 sweeps every route and fails on six
  mutations. Zero identity endpoints remain unbound. [[RUL-135]] · `genie/BUZZ_SECURITY.html`.
  **Nothing waits on David except the deploy itself**; `BUZZ_BIND=0` reverses the lot without one.
- **[C] DONE 14 Sep — the spreader's three modes are built.** One engine, and exactly one place that
  knows a mode exists (`finish()`): stranger-listing keeps the full coaching and carries the ONE ask,
  at the end; member-listing re-asks nothing and shows one score line; looking answers "is it there"
  in five, then stops. 8 categories × both tails walked headless — 16/16 correct, 0 errors.
  `genie/QUICK_THREE_MODES_BUILT.html`. Local only, not deployed.
- **[D] NEW 14 Sep — the traders phone-around is built and is NOT ruled.** David said he was "just
  wondering" about the Maurice case; Claude built it capped at five, as N individual buzzes (never a
  broadcast, never a group thread), each still under that pair's own switch and closed state. It is
  the one genuinely new behaviour rather than a re-dressing of Buzz. **Keep, cap differently, or pull
  it until the app side is ported — David's call.** Removal is one line.
- **[C] DONE 14 Sep — per-category comms live in the Quick Listing.** RUL-132 as a data table, not
  branches; each row badged ruled / not-ruled on screen. All eight categories driven in a browser,
  two real faults found and fixed in the process. Phase two — porting it to the app — is not started.
- **[C] DONE 17 Sep — the whole baseline batch is built flag-dark and proven in the rendered app.**
  All nine items of `BASELINE_BATCH_2026Q4.md` §1 behind one flag (`baseline_q4`, default 0); the
  live app is unchanged until armed. Rendered proofs: `BASELINE_BATCH_PROOFS_2026-09-17.html`.
  Deploy requested (RUL-092); ledger live halves go green when it lands. Detail: plan §6.
- **[D] 17 Sep — arm the baseline.** See it locally first, then the 30 Oct sandbox, then
  `POST /admin/flags {baseline_q4:true}` (+1 page). Nothing else in the batch waits on anyone.
- **[D] 17 Sep — after arming, three field measurements are yours:** DCB-001 time-to-publish
  before/after and David Jnr's retest; the Quick five-tap walk on a real phone; a dated AI vendor
  balance per lane on the +1 card (the gauge reads NOT MEASURED until then).
