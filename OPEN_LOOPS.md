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

**Last reconciled: 2026-09-18 03:3xZ (stand-up, mechanical — SO-3/RUL-037; second pass after David's 03:1xZ approval closed six more rows).** **Third pass 2026-09-18 09:0xZ: L3 closed against production evidence (David: "Please close it"); LIVE LOOPS now holds L7 alone.**
**Fourth pass 2026-09-18 19:2xZ (stand-up, mechanical): L7 CLOSED as EXPIRED — LIVE LOOPS is now EMPTY. D11 and D15 corrected: each named an action that no longer exists.**
**Fifth pass 2026-09-19 19:1xZ (stand-up, mechanical): D14 CLOSED — RUL-013 answered it on 15 Aug, four days after it was opened, and the row never caught up (39 days misreported as a pending decision). D10's waiting condition corrected: it expired at soft launch, 21 days ago. D16 OPENED — the 92-role beta slate is holding a live lane and existed only in a commit message. L8 opened: the design tier is declared but has no live caller.** Previous
reconciliation 2026-08-20 — **twenty-eight days** in which this file was not the integrator it
claims to be. The cause is now named rather than deplored: every stand-up between 2 Aug and
18 Sep ran cloud-only with **no write path to this repo**, so sessions could read this file and
could not edit it. Rule 2 was unenforceable, not ignored. The mount is the fix; reconciliation is
mechanical from here and happens every run, attended or not.

**Day-count REMOVED, not refreshed.** The line that stood here ("1 DAY to soft-public · 4 days to
full launch") was written 20 Aug, corrected once on 28 Aug, and had since aged into a flatly false
statement: full launch was **1 Sep 2026** and the site has been live for 17 days. An undated
countdown is the same defect class as an undated status assertion (the ONETAP_SETUP.md "(this is
today)" lesson) and the correct fix is to delete the counter, not to re-date it — a counter nobody
is obliged to wind will always be wrong again.

---


## 🔴 BLOCKING NOW
*(nothing proceeds until these clear)*

**EMPTY as of 2026-09-18.** B1 (production secrets) moved to CLOSED below with its discharging
probe. Nothing blocks anything. This heading stood with a discharged row under it for 27 days
while three separate notes explained, inside the row, that it was discharged — the explanation is
not the reconciliation.

## 🟠 LIVE LOOPS (open, need to move) — ranked

| # | Loop | Owner | Single next action | Opened | Source |
|---|------|-------|--------------------|--------|--------|
| L8 | **The `design` task tier is DECLARED but has no live caller.** RUL-013 sent design work to the allocated design agent from 1 Sep; `AI_BASELINE.json` carries `tiers/design` (openai gpt-5.6-sol, scaleway standby, ceiling 4000) and says in its own `_doc`: *"Envelope DECLARED, not measured — no live caller exists yet."* So the lane David was told would take design work has, 18 days after it opened, never been called. | [C] | Wire the first real caller and re-derive the envelope from real call shapes, then the golden run its gate requires. Technical throughout — no part of this is David's. Recorded here (not as a new ledger entry) because a concurrent lane is writing `scripts/` and RG numbering is not safe to race. | 2026-09-19 | RUL-013 · AI_BASELINE.json `tiers/design` · closure of D14 |

## ⚪ DECISIONS AWAITING DAVID / COUNSEL — ranked

| # | Decision | Owner | Single next action | Opened | Source |
|---|----------|-------|--------------------|--------|--------|
| D16 | **The 92-role beta slate (RUL-150) — which roles TrustSquare opens with.** `ROLE_SLATE_REVIEW.md`, created 19 Sep for David's review discussion, is marked up to **61 IN · 19 LATER · 19 OUT** across ~102 role rows, and the roles/employer lane is **held pending his review** (commit `758a9de`). It existed only in a commit message and a working file — not here — which is the failure mode rule 2 of this file exists to stop. | [D] | The rows are largely decided; what is genuinely his are the five OPEN QUESTIONS at the head of that file: split or drop the "Miner"/"Industry worker" sector buckets · where Chef sits · which roles make police clearance effectively mandatory (child contact / home access) · which employers to approach first · the four taps per class. Launch scope, so his. | 2026-09-19 | ROLE_SLATE_REVIEW.md · QUICK_LISTING_SPEC.md Part II · RUL-150/151/152 |

| D9 | **FLIP-DRILL-1: pick the hour** — runbook ready (`FIRE_DRILL_RUNBOOK.html`). DEFERRED by David 5 Aug 2026 ("needed, just not now") — STANDS OVER till after launch (David, 11 Aug). | [D] | David names a quiet hour when ready; Claude keeps the log. **Note 18 Sep 2026: the condition this was deferred ON — "till after launch" — lapsed at full launch on 1 Sep, 17 days ago. Still genuinely his (naming the hour); no longer waiting on anything.** | 2026-08-03 | this session |
| D10 | **Travelpayouts tours programs — RESUBMITTED 22 Aug 2026 (David's word, per RUL-041).** The 5 Aug decline (*'website under development or not yet ready'*) blocked GYG · Viator · Welcome Pickups · Booking.com and 22 others; 26 programs auto-connect on approval. Submitted with the site answering publicly and the changed face being real (EULA v1.14 live, gate down, honesty labelling in flight) — not a resubmit-unchanged. Aviasales flights Data API unaffected. **TRAVELPAYOUTS_TOKEN is UNROTATABLE** (one permanent token per account, copy-only, verified on the API page 22 Aug) — accepted risk, reasoned and dated in SECRETS_REGISTER.md, policed by RG-0146. | [D] | **OUTCOME READ 24 Aug 2026 — DECLINED AGAIN, same reason.** Probed at app.travelpayouts.com (project Trustsquare, ID 758984): *"20 programs are currently unavailable… Your website is currently under development or not yet ready. Please complete setting up your site and re-submit your Project for review."* Available **26** / blocked **20** — Booking.com, Viator and GetYourGuide all still blocked. The 22 Aug "we've connected you to relevant brands" email is their generic template, NOT an approval (evidence-ladder: email READ said yes, dashboard PROBE said no; the probe wins). Per RUL-041: do NOT resubmit unchanged — the next submit waits until the site's changed face is materially different (soft launch, 29 Aug, is the natural moment, and the timing call is David's). Their dashboard is meanwhile offering **+25% GetYourGuide rewards, expiring 24 Aug, to switch the Drive loader back on** — declined; all five Drive functions stay Off. Safe lane BUILT instead: travelpayouts_partners.py (TP-LINKOUT-1), server-side 302s, host allowlist, dark by flag, RG-0181. Original standing rule unchanged: commercial lane only — server-side or link-out, NEVER a TP script (RG-0025). **CONDITION EXPIRED — corrected 2026-09-19.** This row said the next submit waits for a materially changed face, *"soft launch, 29 Aug, is the natural moment"*. Soft launch happened 29 Aug and FULL LAUNCH happened 1 Sep; the trigger fired 21 days ago and the row went on describing it as future. The row is also mis-tagged **[C]** while its own text says *"the timing call is David's"* — per RUL-041 the resubmit is his word, so the tag is wrong, not the rule. **Single next action, unchanged in substance: David says resubmit (or not).** Nothing technical is waiting. | 2026-08-05 | RUL-041 · scheduled follow-up |
| D11 | **Maroushka's TS-0022 letter drafted** — the retest letter IS the remediation (9 pre-fix covers need her re-upload; class fix RG-0047 live). | [D] | **ACTION CORRECTED 18 Sep 2026 — "retest-send" DOES NOT EXIST.** `grep` finds no `retest-send` route in `bea_main.py`; the only fault-letter endpoints are `/admin/faults/{fid}/close-draft` and `/admin/faults/{fid}/close-send`. **NO-RETEST-1 (David, 11 Aug 2026 — the same day this row was opened) retired the retest lane in his own words: "there are no retests… the retest-wait status is retired", legacy rows migrated by `migrations/012`.** The row therefore asked him for 38 days to fire an endpoint his own ruling had deleted. Live mechanism, unchanged in substance: GET close-draft → David approves → POST close-send, which closes the fault and stamps `verified_at`. Still his: the send. | 2026-08-11 | Records/FAULT_RECONCILE_2026-08-11.md |
| D15 | **Study & Work-Abroad Advisor (Maroushka's idea, 22 Aug — RUL-042).** Positioning RULED: preparation is ours, based on actuals (possible / typically needed / viability, risks, opportunities); partner education & immigration agencies take the Dossier and provide the actual plans and guidance — that handoff IS the introduction. Assessment on disk: ~$0.50–1.00/report vs 5T = $10, existing 5T deep-dive class, no paid feed, ~70% reuse, MVP 3–5 sessions (one corridor first). | [D] | TEASER: DECIDED 22 Aug (David — 'build it now, no risk to baseline') — built as SAW-1 (static page + banner + manifest line, RG-0158 OPEN), rides the next deploy. UPDATE 23 Aug: 5T CONFIRMED + build GREENLIT + work-route example added (RUL-043); videos full-length, SHELVED until spec approved. Remaining to David: ~~deploy timing (rides next TSL)~~ **— DISCHARGED 18 Sep 2026: the teaser is LIVE, probed 200 at `/static/studyabroad_teaser.html`, and has been since before 24 Aug, when RUL-050 deliberately retired its index banner (unlisted, still live). Deploys also stopped being David's at RUL-092 (3 Sep). Two reasons this limb was never his.** · agency outreach approach (education + placement agencies — sending is his) · the video unshelve moment. Plus a business action: recruit 2–3 founding education/immigration agencies (same lane as travel agencies). | 2026-08-22 | RUL-042 · STUDY_WORK_ABROAD_ADVISOR_ASSESSMENT — nice.docx |

## ✅ CLOSED — last 7 days

### Closed 2026-09-19, fifth pass (stand-up, mechanical — SO-3/RUL-037).

- **D14 CLOSED 2026-09-19 — "Designer-role binding" was ALREADY RULED, and the row never caught up.**
  D14 was opened 11 Aug asking David to rule *"you / a design agent / both"*, with the note *"No urgency
  before launch"*. **RUL-013 answered it on 15 Aug — four days later** — in terms: *"FROM 1 SEP: Fable is
  OUT — design work returns to the allocated design agent or its swapped-out option (the 'design' task
  tier: openai gpt-5.6-sol, scaleway standby)."* **DATED PROBE, 19 Sep 2026:** `AI_BASELINE.json` carries
  `tiers/design`, whose own `_doc` cites RUL-013 and the post-1-Sep design lane, with a ceiling of 4000
  tokens in `pinned_constants`. So the answer is not only made, it is wired. **LAG: 35 days** ruled-but-open
  (15 Aug → 19 Sep), of which 18 days were after the "before launch" condition itself expired on 1 Sep.
  Second consecutive stand-up to find rows in David's queue that were already facts — the classification
  defect, not a new one. The one thing genuinely left is technical and is now **L8** above: the tier has
  no live caller. That is Claude's, and it never was his.

### Closed 2026-09-18, fourth pass (stand-up, mechanical — SO-3/RUL-037). LIVE LOOPS is now EMPTY.

- **L7 CLOSED 2026-09-18 — "Tooling-through-the-gate" EXPIRED, not fixed. Its premise stopped being
  true at full launch.** The row (opened 13 Aug) said GATE-ENFORCE-2 raises the origin token gate, so
  on-box/edge tooling reading data endpoints anonymously **will 401**, leaving attended off-box tools
  needing the reviewer cookie. PROBE 2026-09-18 19:0xZ, anonymous `curl`, no cookie and no token:
  `/ai/functions` **200** (serves the full function list) · `/review/verify` **200 `{"valid":true}`** ·
  `/dashboard/bit` **200** · `/dashboard/maint` **200**. Nothing 401s, so there is no cookie for an
  attended tool to need. This is **the same discharge that closed D7 this morning** — the gate came
  down at full launch, **1 Sep 2026** — and L7 is its sibling: one row described the gate stopping
  *people*, this one described it stopping *our own tools*, and both stopped being true on the same
  day for the same reason. Closing D7 without sweeping for its siblings is why this survived another
  17 days. **LAG: 17 days.** The nginx `auth_request` catch-all machinery is still in the tree
  (`bea_main.py` comments, migration 016) and is dead in the same sense as D7's `showGate()` — a
  housekeeping pass, not a loop.

- **THE HEADING IS NOW HONEST: 🟠 LIVE LOOPS holds no rows.** Stated plainly because the file's own
  rule 3 says David reads top-down until he stops caring: for the first time since this file was
  created, a reader who stops at the first two headings has read the whole truth — nothing is
  blocking and nothing is live. Every remaining row is in DECISIONS AWAITING DAVID, and two of those
  were corrected today for naming actions that no longer exist.

**Shipped this run (not loop closures — defects found while probing the loops):**

- **EULA-FOOTER-1 — the published EULA contradicted itself on its own version number.** `eula_clean.html`
  opened with *"Version 1.17 · Last updated 18 September 2026"* and closed, 1,109 lines later, with
  *"— End of TrustSquare Terms of Use / EULA v1.16 —"* plus a v1.16 country-schedule line. Both were
  **live**: `GET /terms` served the 1.17 header and the 1.16 footer in the same document. Fixed at THE
  SOURCE and propagated by THE ONE WRITER — `scripts/eula_sync.py` → *"synced: terms.html, ms.js"*, then
  `--check` → *"EULA in sync (120332 bytes) across eula_clean.html, terms.html, ms.js"*, and all three now
  read v1.17 top and bottom (`v1.16` occurrences: **0, 0, 0**). Not edited in `terms.html`, which is
  generated — that was L11's mistake this morning and it is not repeated.
- **This also corrects a figure inside RG-0400.** That entry says the seller box is *"1.10 behind"* a
  published **v1.17**; until tonight the published footer said v1.16, so the entry was right about the
  fork and arithmetically unprovable from the document it cited. It is now exactly seven versions.
- **RG-0238 GREEN — the word "vetted" is off the listing surface.** `ms.js` told a seller *"let a **vetted**
  local agent carry it"*. RG-0238 bans exactly that word, unqualified, as a representation about a person's
  future conduct (CHILD-SAFETY-WORDING-1, from David's own 1 Sep framing). Now reads *"let a local agent
  carry it"* — the offer is unchanged, the claim we cannot stand behind is gone. `grep vetted ms.js` → **0**;
  `node --check` green. One occurrence in the tree; `marketsquare.html` and `quick.html` were already clean.
- **A PROBE METHOD WAS WRONG AND IS NAMED HERE.** This morning's L11 closure cited *"zero `legal@` routes"*
  on the live `/privacy`. Cloudflare's email obfuscation (`email-decode.min.js`) is active on that page, so
  **every address is hex-encoded and a live `grep` for `legal@` returns zero whether or not it is there** —
  the check could not have failed. Re-run properly by decoding the `cfemail` payloads: `/privacy` = **16 ×
  support@, 0 × legal@** (the claim holds, now on evidence), `/terms` = 10 × legal@, 9 × support@, 3 ×
  compliance@, matching the deliberate IP-takedown/arbitration carve-out. The finding is the method, not the
  result: a probe that cannot return a negative is not a probe.


### Closed 2026-09-18, second pass — David: *"I approve all changes, please implement and close all of them."*

- **L3 CLOSED — SCOREBOARD-1 is LIVE in production, proven end to end, not proven by having queued it.**
  David, 18 Sep 2026: *"Please close it."* The queued action DID report: `run_bat
  MarketSquare\enable_scoreboard_unattended.bat` returned **rc=0 at 05:35:23** ("FLAG ON", 13 probes,
  est $0.00021). Verified afterwards ON THE PRODUCTION BOX, not from the result file:
  `launch_switches.scoreboard_enabled = 1` in `/var/www/marketsquare/marketsquare.db`, and
  `ai_scoreboard_probes` holding real rows. **The row's own close-test was wrong and is corrected
  here: there is NO "live scoreboard surface" to re-probe.** SCOREBOARD-1 has no HTTP route by
  design — `grep` for a scoreboard route in `bea_main.py` returns nothing; it is a nightly
  background agent whose artifact is `ai_scoreboard.json`. Asking for a surface that was never built
  would have kept this row open forever.
  **The gap that check found, and it was real:** the bat's step 2 runs `--probe --force --report`,
  which prints a report and does NOT write the json — only `run_nightly()` does. So after 05:35 the
  flag was on and the artifact did not exist. Closed by running the agent's own scheduled entry
  point once against production: `ai_scoreboard.run_nightly()` → "probe round done — 13 probes,
  est $0.00018" → **"ranking written -> /var/www/marketsquare/ai_scoreboard.json"** (4,463 bytes,
  09:01Z; probe total 13 → 26). The whole nightly path is now walked, not assumed.
  **The loop itself is alive:** `journalctl -u marketsquare` shows the BEA startup task firing at
  01:33 every night (16, 17, 18 Sep), each time logging *"scoreboard: disabled ... no probes sent"* —
  correct behaviour while the flag was off, and the proof the scheduler was never the problem. The
  19 Sep 01:33 run is the first that does real work. Reverse: `disable_scoreboard.bat`.

- **D4 CLOSED — all four country supplements are IN `privacy.html`, not drafted beside it.** Supplement A
  (United Kingdom — UK GDPR/DPA 2018: lawful-basis list, Art 22 position, IDTA/UK Addendum transfers, PECR
  cookie position, ICO), B (United States — CPRA notice-at-collection, sensitive-PI position, no-sale/no-share,
  10-day ack / 45-day response, non-discrimination, plus eight other states with an appeal route), C (Australia
  — APPs 1,2,3,5,7,8,11,12,13, the APP 8.1 accountability sentence, NDB, OAIC) and **D (European Union — France
  and Portugal, added the same session, closing L12)**. The three EULA cross-references that promised this text
  existed — Schedules A5, B4, C4 — are now true, and D5's French one with them. `privacy.html` 8,132 → 25,368
  bytes, parses clean.
- **The Article 27 question is ANSWERED, not flagged.** David's instruction was explicit: do not leave it open
  with a flag or a pending permission. It was settled by reading the code rather than by deferring: identity
  verification sends the uploaded document to a vision model that **extracts the printed name and ID number and
  compares them to what the seller typed** — no facial recognition, no biometric template, no 1:1 or 1:N match,
  no liveness. `id_verify_provider.py`'s own header calls the selfie-match tier *"a strictly higher tier,
  deliberately left as a future lane"* and the provider key defaults to `stub` (disabled); the only liveness
  wording in the tree sits behind a literal `[COUNSEL REQUIRED: insert provider]` placeholder in a mockup. Under
  Art 4(14) a photograph is biometric data only through specific technical processing allowing unique
  identification — OCR of a name and a number is not that. So no Article 9 processing occurs, the Art 27(2)
  exemption limb holds, and **A2 and D2 say so in those words** rather than naming a representative that does not
  exist or carrying a bracket. **It is a determination with a tripwire, which is why it is not a flag:**
  **RG-0397** goes RED the day any biometric or liveness processing enters the identity path, or the published
  basis drifts from what the code does — proven against four mutations, clean at baseline. Same pattern as
  TRAVELPAYOUTS_TOKEN (accepted, dated, policed by RG-0146). *Stated plainly because it is a legal position taken
  in David's name: overruling it is one line, and appointing a representative would still be his spend.*
- **L10 CLOSED — the false breach clause is gone from the live policy.** §7 no longer promises "within 30 days"
  to everyone. It now names the shortest period each law requires: POPIA as soon as reasonably possible, **UK GDPR
  72 hours to the ICO**, Australia's 30-day assessment plus notice as soon as practicable, and US state law without
  unreasonable delay. D8 repeats the 72 hours for the EU. This was a live published commitment to miss a statutory
  deadline by 27 days.
- **L11 CLOSED — one rights inbox.** `privacy.html` now routes every privacy, POPIA, UK GDPR, CCPA/CPRA and
  Australian Privacy Act request to **support@**, and the EULA's contact row was changed to match (v1.16 → **v1.17**,
  18 Sep). **CORRECTED SAME SESSION — the first attempt was in the wrong file and was reverted.** I edited
  `terms.html`, which is GENERATED. `eula_clean.html` is THE SOURCE and `scripts/eula_sync.py` is the one writer
  of `terms.html` and of the `_EULA_HTML` literal in `ms.js` — the copy users actually accept. A concurrent lane
  ran the sync and correctly restored v1.16/`legal@` over my edit, exactly as EULA-FORK-1 (14 Aug) was built to
  do after the three copies silently forked and users were accepting an older agreement than the one published.
  Worse, my version had shipped to `terms.html` alone, so for about twenty minutes the published page said v1.17
  while the in-app acceptance modal still said v1.16 with `legal@` — **I had recreated the exact fork that
  machinery exists to prevent.** Redone at the source and synced: `eula_sync.py --check` reports *"EULA in sync
  (120,332 bytes) across eula_clean.html, terms.html, ms.js"*, and all three are PROBED live at v1.17 with the
  support@ rights row and zero `legal@` rights rows (`ms.js?v=685`). `legal@` occurrences in `privacy.html`: **0**. The EULA's other eleven `legal@` uses — IP takedown
  notices, the arbitration opt-out — were deliberately **left alone**: those are a different function and
  re-pointing them would have been a worse change than the one being fixed.
- **L12 CLOSED — see D4.** Supplement D covers France and Portugal on the same basis; D2 carries the EU Art 27
  determination and RG-0397 polices A2 and D2 together.
- **L13 CLOSED — an off-box run can no longer repaint the server's arming state.** Producer
  (`maintenance_agent.py`): when the brain probe's own refusal kind starts with `vantage:` — which MAINT-BRAIN-1
  returns precisely because that endpoint is local-only, so *"can I reach it"* IS *"am I on the box"*, and no
  second mechanism was invented — `armed`/`live`/`armed_switch` post as **None (NOT MEASURED)**, never False.
  Consumer (`dashboard.server.html`): null renders a grey **ARMING NOT MEASURED** chip, the same treatment RG-0382
  gave the brain field. The vantage also rides `mode`, which is already on the server's `_MAINT_HB_FIELDS`
  whitelist, because `bea_main.py` was held by the DEVICE-NOLAPSE-1 lane all session (SO-5) and a fix that waits on
  another file is a fix that does not ship tonight. **RG-0398**, proven against three mutations.
- **L9 CLOSED — maintenance heartbeat restored, result READ not assumed.**
  `host_queue/done/20260918-022221-520_...maint-host.result` → **rc=0 at 04:35:07 SAST**, run
  `2026-09-18T02:35:03Z`, SHADOW, 0 seen / 0 acted, heartbeat posted. The 9.2-hour gap is closed. *That same run is
  what exposed L13.*


### Reconciled 2026-09-18 (stand-up, mechanical). Six rows discharged; each carries the dated probe that discharged it and the lag it misreported.

- **B1 CLOSED 2026-09-18 — "Production secrets exposed" (opened 7 Aug / 20 Aug).** Discharged **22–23 Aug**; printed under 🔴 BLOCKING NOW until today. **LAG: 27 days at the top of the file, under a heading that says nothing proceeds until it clears.** PROBE 2026-09-18 02:2xZ: the 17 Sep full ledger run reports **369 entries · 347 LOCKED · 22 OPEN · 0 REGRESSED**, and RG-0146 (red until no credential is still marked BURNT) is not among them; SECRETS_REGISTER.md's "Still burnt" table has been EMPTY since REGISTER_VERIFIED 2026-08-22. Three separate notes *inside the row* said it was discharged and asked for it to be moved — which is the lesson: a note explaining that a row is closed is not a closed row, and a reader who stops at the heading (rule 3 says David does exactly that) reads the heading, not the note. Residue, neither blocking and both unchanged: David deletes two superseded Cloudflare tokens; FOUNDERS_ID_SALT rotate-or-accept is Claude's call.

- **L6 CLOSED 2026-09-18 — "BIT-AIM-1: FEA probes mis-aimed" (opened 11 Aug).** The row said the board was **degraded 5/8** with B-FEA-SHELL, B-FEA-EXAMPLE and B-FEA-CONTRACT all failing on `BIT_BASE=localhost:8000`. PROBE 2026-09-18 02:2xZ, `GET /dashboard/bit`: **`state:pass, 8/8, failing:[]`** — and the three named probes are green by name: `B-FEA-SHELL PASS size=417952 ok (disk)` · `B-FEA-EXAMPLE PASS 10 example endpoints OK (src advertagent:/ai/functions)` · `B-FEA-CONTRACT PASS 10 example endpoints OK`. The per-probe base landed; nobody moved the row. **LAG: not precisely datable from this file — which is itself the finding.** A row whose fix date cannot be recovered is a row that was closed in a transcript and nowhere else (rule 2).

- **L5 CLOSED 2026-09-18 — "Fix-agent phase-aware; Agent still OFF" (opened 9 Aug).** The three assertions in the row are all now false. PROBE 2026-09-18 02:2xZ, `GET /dashboard/maint`: **`mode:LIVE · armed:true · armed_switch:true · live:true · phase:postlaunch · brain_state:GREEN`**. The agent is not off, the phase is not prelaunch, and the operational path is not pending proof — it is running, with `agent_30d_usd 0.000238` across 14 calls against a $0.50/day budget.

- **D12 CLOSED 2026-09-18 — "Arm the Maintenance Agent" (opened 11 Aug).** **It was already armed.** This row sat in the DECISIONS AWAITING DAVID table asking him to make a decision he had already made. PROBE 2026-09-18 02:2xZ: `/static/maint/b4_tier2.json` → `ready:true`, verdict *"READY — real brain's patch gated green end-to-end"*, and `/dashboard/maint` → `armed_switch:true`. The readiness gate the row was waiting on has read READY since **2026-08-11T09:10Z**. **LAG: 38 days, 17 of them post-arming.**

- **D7 CLOSED 2026-09-18 — "How do email recipients get past the pre-launch Unlock gate?" (opened 2 Aug). EXPIRED, not answered.** The question presupposed a gate. PROBE 2026-09-18 02:2xZ: anonymous `GET /review/verify` with **no cookie and no token** returns **`{"valid":true,"scope":"review"}`** — the server admits everyone, so there is nothing for a cold click to be stopped by. The gate came down at full launch, **1 Sep 2026**. The client-side gate machinery is still in the page (`showGate()`, the PIN and magic-link screens) but never fires; that is dead code for a housekeeping pass, not a decision for David. **LAG: 17 days as a live decision after the thing it was deciding about ceased to exist.** Neither branch of its "rule: wait-for-launch / build preview bypass" is now meaningful — launch happened, and the bypass has nothing to bypass.

- **L8 CLOSED 2026-09-18 — external uptime monitor, INCLUDING the alert half (opened 14 Aug).** The row was marked ✅ DEPLOYED on 28 Aug but left in 🟠 LIVE LOOPS carrying an explicit residue: *"the PROBE half is proven, the ALERT half is not — no successful send has been observed."* **That residue is discharged, and was discharged on 5 Sep.** EVIDENCE, read today out of `ops/cloudflare/UPTIME_DEPLOYED.md`: an alert was sent with `--no-fallback` so the ssh lane was not available to it — Resend id `e83298f3-2b98-4673-8cad-080dfb0e883f` — and **the message was read back out of Gmail at 2026-09-05T07:52:27Z**, one second later, from `hello@mail.trustsquare.co`. Resend accepting is not delivery; the inbox read is the evidence, which is that file's own 28–29 Aug lesson applied to itself. Also recorded there and worth carrying forward: RG-0138 **no longer reads `LAST_HEARTBEAT` for liveness at all** — it GETs the Worker's public endpoint and requires a KV-bound result under 15 minutes old, reporting UNVERIFIED rather than RED when the running machine cannot reach the net. `LAST_HEARTBEAT` survives as INFO only. **LAG: 13 days.**

- **D16 CLOSED 2026-09-18 — Founders Badge (opened 23 Aug).** Discharged by **RUL-060 on 28 Aug**: David named and spent the once-off founders occasion as the LAUNCH WINDOW (`enable_launch_special.bat`, hard close 2026-09-01, CityLauncher wave lane only); the park resumed automatically when the window closed. The file's own note said so and asked for the move. **LAG: 21 days.**


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
