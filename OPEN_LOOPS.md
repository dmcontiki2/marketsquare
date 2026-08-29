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
