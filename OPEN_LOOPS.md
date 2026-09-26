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

**Last reconciled: 2026-09-26 19:3xZ (TENTH pass, stand-up, 19:00Z slot, on time, mechanical — SO-3/RUL-037).** **L8 CLOSED after 26 days — and its premise was WRONG, which is why four stand-ups re-probed the same zero.** The row said the `design` tier had never been called and prescribed wiring a caller. The tier was wired at the chokepoint all along (`/admin/maint/brain` accepts `task="design"`; `_MAINT_TIER_LADDER` carries it). It had no caller because **PATH_B's "routed to design backlog" was a sentence, not a mechanism**: nothing in `scripts/` wrote `DESIGN_BACKLOG.md`, TS-0027 and TS-0006 were both closed 11 Aug asserting they were routed there, and the file holds one dossier — DCB-001 — which is neither of them. Two faults said routed; zero arrived. Fixed as **DESIGN-ROUTE-1**: PATH_B files a real dossier and asks the design tier for its direction, so the tier has its first caller and the proxy assertion is gone. **L20 NARROWED to (c) alone and its own diagnosis corrected** — the row blamed a missing User-Agent; the ledger has carried one since line 84 and the real mechanism is a transient edge refusal being read as the app's verdict (**EDGE-STATUS-BLIND-1** shipped, one writer, four readers). **L21 CLOSED:** the mirror is level (`git rev-list origin/main..HEAD` = **0**), the 25 Sep stranded push executed, and the host agent completed three actions today (last 14:15:07Z) — the stall cleared and the detector that would catch the next one is live. **L18(b) discharged by probe:** the QA bot's 403 mechanism is confirmed, not guessed — the named-UA request gets 200 and only the bare urllib UA gets `error code: 1010`. **NEW, and it had already cost vision: INSTRUMENT-DOOR-1** — `GET /dashboard/bit` and `GET /dashboard/maint` still said "No auth (obscure URL)" in their own docstrings six weeks after SEC-GATE-1 (24 Sep) made both **admin**; this stand-up read both blind until it carried a credential, and DW-158 had recorded the same blindness on the daily watch. Corrected at source. **Nothing was added to David's queue this run and nothing taken out of it** — it stands at L14 (QA Tuppence), L15 (EULA v1.19), L17 (Play Console, waiting on D-U-N-S), L19 (Terms v1.19 sign-off + 11 decisions) plus the standing [D] rows. **ADDENDUM 19:4xZ — the WHOLE-BOARD VERDICT CAME BACK AND WAS READ, and it is the first clean one: `RESULT: no regressions in what COULD be checked`, 1 entry NOT EVALUATED (RG-0186, a POSIX-nginx harness that cannot match forward-slash fixtures on the Windows host — the instrument's own named vantage reason, not the site). The **2 REGRESSED of 25 Sep are gone**: RG-0028's false conviction cleared on the first board carrying EDGE-STATUS-BLIND-1, exactly as predicted, and RG-0391 was re-aimed by the maintenance loop this morning. rc=2 is UNVERIFIED, not red — and per the result's own words that is not a green board. **L20's (c) failure mode did NOT repeat:** the result landed at 19:40:47Z and this run read it before reporting, where the 24 Sep verdict sat unread for 26 hours.** **AND ONE NEW FAULT WAS FOUND BY THE POST-DEPLOY CHECK ITSELF — BIT-STORE-FLOOR-1, fixed and verified live.** At 19:36:04Z an empty POST to `/dashboard/bit` overwrote a real 8/8 board with `{"received_at": ...}` and nothing else; the panel read neither green nor red over a healthy site. Cause diagnosed, not guessed: the two empty posts (19:36:04Z, 19:42:24Z) land within seconds of this run's two app restarts, while the 15-minute timer posts real boards (19:02:29Z, 19:47:54Z) — the post-deploy BIT run races the restart, measures nothing and posts nothing. Before the fix that blanked the panel after EVERY deploy until the next tick repaired it, which is why fifteen-minute windows of blankness were never caught. NOT MEASURED now never becomes the record; proven on the live box both ways (an empty post → `state: not_measured` with the reason, a real board at 19:47:54Z → 8/8 PASS stored normally). The POSTER is still posting nothing on a deploy — recorded as **L23**. **NOT REACHED, said plainly: L13 and L16 were not started** — this run spent its hands on the three fixes above; neither is blocked and both are the next session's, and L13 was re-probed rather than carried silently.

**Earlier: 2026-09-25 20:4xZ (ninth pass, stand-up, 19:00Z slot fired 72 min late, mechanical — SO-3/RUL-037).** **L18 NARROWED and half of it SHIPPED** (QA-GATE-BLIND-1: the deploy gate graded 640/640 routes from a vantage that answered 403 before the app, passed, and then wrote that blind run over its own baseline — the bot now proves it can see the app before it may grade one, test red on the pre-fix source). **L20 OPENED — and it is the one that matters:** the whole-board verdict this pass finally reached prints **2 REGRESSED**, both of them the instrument convicting itself, and **the 24 Sep board verdict sat unread in `host_queue/done/` for 26 hours saying 'Do not deploy over this'** while eleven host actions and several deploys ran over it. **L21 OPENED and its detector shipped the same run:** `autodeploy_agent.bat` on David's PC stopped after 13:15:06Z and nothing noticed for 7h31m, leaving 5 commits stranded off the mirror (the inspection's criticals among them) — the ~20-minute loop now watches that lane. **L8 and L13 re-probed and still open**, each with its probe in the row; neither started, and said so rather than carried silently. **Nothing was added to David's queue this run and nothing taken out of it** — it stands at L14 (QA Tuppence), L15 (EULA v1.19), L17 (Play Console, waiting on D-U-N-S) plus the standing [D] rows. **What this pass could not reach: the cause of the QA bot's 403** — RG-0028's own scope text names the mechanism (the origin takes connections only from Cloudflare's ranges), but proving it needs server hands this session does not have.

**Earlier: 2026-09-18 03:3xZ (stand-up, mechanical — SO-3/RUL-037; second pass after David's 03:1xZ approval closed six more rows).** **Third pass 2026-09-18 09:0xZ: L3 closed against production evidence (David: "Please close it"); LIVE LOOPS now holds L7 alone.**
**Fourth pass 2026-09-18 19:2xZ (stand-up, mechanical): L7 CLOSED as EXPIRED — LIVE LOOPS is now EMPTY. D11 and D15 corrected: each named an action that no longer exists.**
**Eighth pass 2026-09-24 20:1xZ (stand-up, 19:00Z slot, mechanical — SO-3/RUL-037). The schedule fired on time.** **L12 and L11 both CLOSED against dated probes and shipped code (`63839fd`), not against intent** — RG-0426 re-aimed at the point of use (RG-0462) and the three orphaned instrument fixes numbered (RG-0459/0460/0461). **L8 and L13 re-probed and still open**, each with the probe in its row. **Nothing was added to David's queue this run and nothing was taken out of it by this pass** — it stands at the two rows the 24 Sep lanes opened for him (L14 QA Tuppence, L15 EULA v1.19) plus the four standing [D] decisions. **The one thing this pass could not reach: a whole-board ledger verdict.** The board was wedged at entry 24 until LEDGER-ENTRY-CEILING-1 shipped this run; it now advances, but at ~25 entries per sandbox call it needs ~18 calls, so the full run was handed to the host queue instead (`20260924-200620-614_run_py_marketsquare-scripts-regression-ledger.req`, next tick ≤20 min). Said plainly rather than estimated.

**Seventh pass 2026-09-23 20:0xZ (stand-up, 19:00Z slot, mechanical — SO-3/RUL-037). The schedule fired on time this slot — the first clean firing since 19 Sep.** **L10 CLOSED:** both actions it named were landed this run — VANTAGE-BLIND-1 ported into the regression ledger as LEDGER-VANTAGE-BLIND-1 (the four entries that were printing REGRESSED on unmounted siblings now read UNVERIFIED with a named reason), and STANDUP-WATCHDOG-1 wired into `scripts/maintenance_agent.py` beside the backup lane. Both had been held one run under RUL-140 and the tree was quiet on those paths this time. **L9 NARROWED, not closed:** Q1–Q4 — the four defects on the live seller path — were shipped by the concurrent lane and PROBED live this run, and RULINGS.md plus the genie/ working files are now committed, so both halves of the row's original complaint are discharged; Q5–Q12 and the language layer remain. **L8 re-probed and still open** (23 days declared, zero callers). **L11 OPENED:** three instrument fixes shipped this run carry no regression-ledger entry and no changelog fragment, because `scripts/regression_ledger.py`, `changelog.d/*` and `status.d/*` are all inside another lane's live work lock — rule 2's failure mode, arrived at by standing off a lock rather than by forgetting, and recorded here so it cannot be lost either way. **L12 OPENED — and it is the one that matters most for his queue:** RG-0426, the last ledger entry still addressed to David, tells him to provision an AI vendor key that is already on the box (OPENAI_API_KEY, 164 chars, in `/var/www/marketsquare/.env`, read by `ai_provider.envkey()` per ENVKEY-1, and proven live today by the maintenance brain's own 200 probe on the openai lane). The entry probes `/proc/<pid>/environ`, where a .env-sourced key can never appear, so it can only ever fail. His queue is therefore **four questions on D16 and the four standing [D] rows — nothing was added to it this run, and one item was taken out of it.**

**Sixth pass 2026-09-23 17:1xZ (stand-up, mechanical — SO-3/RUL-037). THE FILE WAS NOT RECONCILED ON 20, 21 OR 22 SEP — four days, not one.** The 21 and 22 Sep stand-ups did not run at all (no PULSE_LOG line either) and this run fired 21h48m after its 22 Sep 19:00Z slot, so one firing is covering two missed days. That is a different failure from the 2 Aug–18 Sep one: the mount is there and writes work — the schedule itself did not fire. **L9 OPENED:** RUL-162 and the twelve Quick-audit items from David's 23 Sep airport session live in `RULINGS.md` and `genie/LANG_QUICK_BRIEF.md` and nowhere else — rule 2's exact failure mode, and the second time in five days (D16 was the first). **D16 corrected:** its claim that the roles lane is *held pending review* is false — `c30c33d` shipped the Services door and a 99-row role registry on 20 Sep — and RUL-159 had already answered one of its five open questions. **L8 re-probed and still open** (dated probe in the row). **Fifth pass 2026-09-19 19:1xZ (stand-up, mechanical): D14 CLOSED — RUL-013 answered it on 15 Aug, four days after it was opened, and the row never caught up (39 days misreported as a pending decision). D10's waiting condition corrected: it expired at soft launch, 21 days ago. D16 OPENED — the 92-role beta slate is holding a live lane and existed only in a commit message. L8 opened: the design tier is declared but has no live caller.** Previous
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
| L9 | **RUL-162 and the whole 23 Sep Quick-audit list exist in a ruling row and one working file — not here, and not committed.** David's airport session on 23 Sep ruled the two-layer language design (app speaks the user's language, advert speaks the lister's, one extra language with a back-translation she approves), replaced Sesotho with Sepedi on South Africa's list, and approved per-country lists for all nine active countries. The same session logged **twelve Quick-listing defects (Q1–Q12)**, four of which break the flow on the live product: Q1 Quick is a one-way door (hand-over must land her signed in, on her draft), Q2 the app re-asks what Quick already knows, Q3 two different scores for one advert (Quick 60 vs app 80), Q4 published-but-invisible until refresh. **PROBE 2026-09-23 17:0xZ:** `grep RUL-162 OPEN_LOOPS.md` → **0**; `genie/LANG_QUICK_BRIEF.md` and `genie/LANGUAGES_QUICK_AUDIT_BOARD.html` are **untracked**, `RULINGS.md` is **uncommitted**. | [C] | Q1–Q4 first — they are live defects on the seller's path, not polish — then Q5–Q12, then the language layer tester-only per RUL-162(d). **Not started this run and deliberately so:** another session was writing `genie/`, `scripts/maintenance_agent.py`, `scripts/regression_ledger.py` and `RULINGS.md` while this stand-up ran (mtimes 16:43–17:06Z), and RUL-140 says a lane stands off a scope another lane is in. Recorded, not raced. **NARROWED 2026-09-23 19:5xZ — Q1–Q4 ARE SHIPPED AND PROBED LIVE, and the row's own ‘not committed’ complaint is discharged.** The concurrent lane landed them while this stand-up ran and the 18:47Z deploy (head `8a0dfe4`) carried them: **Q1** `POST /listings/quick-publish` answers **422** on an empty body — the route exists and validates, where the first cut answered 405 (ONE-TAP-PUBLISH-1b) — plus ARRIVAL-1; **Q2** QUICK-ANSWERS-1; **Q3** ONE-SCORER-1 (one score, not Quick 60 vs app 80); **Q4** PUBLISH-REFRESH-1. One door confirmed live: `/quick_next.html` **301 → /quick/** and `/q/services` serves the same 272,347-byte app. `RULINGS.md` is now COMMITTED (`3481dc5`) and the `genie/` briefs are tracked, so RUL-162 is no longer canon-in-a-working-file. **WHAT REMAINS AND IS THE WHOLE ROW NOW: Q5–Q12, and the language layer tester-only per RUL-162(d)** — migration 049 arms `launch_switches.lang_layer` and is on disk. Not started by this stand-up: `quick.html`, `ms.js`, `genie/*` and `roles/*` are all inside lane `lang-quick-2026-09-23`'s work lock (taken 19:55:21Z), and RUL-140 is a stand-off, not a preference. | 2026-09-23 | RUL-162 · genie/LANG_QUICK_BRIEF.md · RUL-149 (amended) · RUL-160 |
| L13 | **The BIT board exists as TWO separate files six weeks apart, and nothing asserts they agree.** `bit/bit_runner.py` is what the stand-up runs (through the Cloudflare edge); `ops/bit/bit_runner.py` is what the deploy manifest ships to `/var/www/marketsquare/bit/` and what `trustsquare-bit.timer` runs **every 15 minutes** on the box. Different inodes, no link. **PROBED 2026-09-23 20:3xZ:** the served copy is dated **11 Aug 2026** — six weeks stale — and lacks even `--verbose`/`--json`. The divergence is NOT accidental in one direction: the ops copy is a deliberate server variant (it probes `localhost:8000` and carries `BIT_AA_BASE`), which is why BIT-EDGE-BLIND-1 was fixed only in `bit/` this run and **must not** be copied over it — the server copy is immune to the edge refusal by construction, and blind-copying would have destroyed its localhost wiring. The loop is that the shared check logic has no single writer and no assertion that the two agree, so a real fix to either board silently fails to reach the other. | [C] | Factor the shared checks into one imported module with the two thin vantage wrappers on top (edge vs localhost), then a ledger entry asserting both boards resolve the same check set — the ONE-WRITER pattern `scripts/changelog_compile.py` and `status_compile.py` already use. The manifest line mapping `ops/bit/bit_runner.py` onto the served `bit/bit_runner.py` is the thing that has to change last, and `ops/autodeploy/deploy_manifest.txt` is inside lane `lang-quick-2026-09-23`'s lock this run. **RE-PROBED 2026-09-24 19:2xZ — STILL OPEN and now asserted rather than only described: `bit/bit_runner.py` (10,410 B, 23 Sep) and `ops/bit/bit_runner.py` (9,621 B, 11 Aug) are still different inodes with different md5s, six weeks apart. RG-0460 shipped this run locks BIT-EDGE-BLIND-1 in the edge copy AND carries the warning in its own scope text that the ops copy is a deliberate localhost variant which must NOT be overwritten with it — so the trap is now written where the next session will read it, not only here. The factoring itself is unstarted.** **RE-PROBED 2026-09-25 20:3xZ — STILL OPEN and unchanged: `bit/bit_runner.py` 10,410 B md5 3395caa112626bdf91921fe4c1b12783 (23 Sep) vs `ops/bit/bit_runner.py` 9,621 B md5 4fe010d94d54629509d8136d902a3335 (11 Aug) — different inodes, six weeks apart, second consecutive stand-up asserting it rather than describing it.** **RE-PROBED 2026-09-26 19:1xZ — STILL OPEN and unchanged for a THIRD consecutive stand-up: `bit/bit_runner.py` 10,410 B md5 `3395caa112626bdf91921fe4c1b12783` (23 Sep) vs `ops/bit/bit_runner.py` 9,621 B md5 `4fe010d94d54629509d8136d902a3335` (11 Aug) — different inodes, six weeks apart, no assertion that they agree. Nothing blocked it this run (the tree carried no work lock at 19:1xZ); not started because this run spent its hands on EDGE-STATUS-BLIND-1, INSTRUMENT-DOOR-1 and DESIGN-ROUTE-1. That is a choice, not a block. | 2026-09-26 | BIT-EDGE-BLIND-1 · ops/autodeploy/deploy_manifest.txt:170 · trustsquare-bit.timer · RG-0421 (ONE WRITER) |
| L14 | **E2E-HMI-1 (24 Sep): two legs of the human-interface walk were not walked** — (a) buyer intro → seller accept → 1T burn → contact reveal, and (b) ~~a Local Market seller's no-show complaint button~~ — **BUILT and proven live the same evening (LM-NOSHOW-1, commits 73d327a/7f10d6e) with a seeded accepted LM intro and no Tuppence moving**. David declined a QA Tuppence grant on 24 Sep, so both wait on that. Everything else on the board `E2E_HMI_WALK_2026-09-24.html` is fixed and read back live (commits b951503, 3450af9, 57a9f0b). | [D] | Approve 1-2 QA Tuppence (granted and reversed), then walk both legs and build/prove the LM no-show button in the same session. | 2026-09-24 | changelog.d/2026-09-24-e2e-hmi.md |
| L15 | **EULA v1.19 is drafted, not published**: five new country schedules (BW, DE, KE, MZ, NA — David ruled the app's picker canon) and the s4.6 draft-expiry sentence removed (David: drafts do not expire). | [D] | David reviews `EULA_v1.19_DRAFT_country_schedules.docx`; on his yes: edit eula_clean.html, eula_sync.py, bump canon.yml + LEGAL_VERSIONS.md, pointer checks (one EULA-FORK-1 pass). | 2026-09-24 | EULA_v1.19_DRAFT_country_schedules.md |
| L16 | **Landing in TrustSquare from Quick takes 11.8 s to usable on weak 3G** (2.8 s on 4G): the full home page -- ms.js 384 KB compressed, the map library from unpkg, 3.7 MB of home and Wonders photos in the first 4 s -- loads before her draft (SEAM-1 audit, measured 25 Sep). | [C] | Make the ?signin / ?draft / /k/ landing skip the home imagery and defer the map library until a map is opened; re-measure on the same two throttle profiles. **NOT STARTED 2026-09-26 — said rather than carried silently. Nothing blocks it** (no work lock on `ms.js`, `quick.html` or the landing path at 19:1xZ); this run's hands went to the three instrument/routing fixes. Unre-measured, so the 11.8 s figure stands as the 25 Sep measurement, not as today's. | 2026-09-26 | QUICK_TS_SEAM_AUDIT_2026-09-25.html · changelog.d/2026-09-25-seam.md |
| L17 | **Android shell for Quick (phones head to head, offline hand-over)** -- plan written (`genie/ANDROID_SHELL_PLAN.md`); nothing can be published to Play without a developer account in the company name. | [D] | **D-U-N-S requested 25 Sep 2026 ~10:55 SAST** through Apple's free D-U-N-S lookup (TrustSquare (Pty) Ltd was not listed; D&B confirmation goes to dmcontiki2@gmail.com, typically 5 working days, up to 30). When the number arrives: Play Console sign-up as ORGANIZATION (D-U-N-S, trustsquare.co, US$25 card payment and identity checks are David's); Claude then builds steps 2-5 of the plan. | 2026-09-25 | genie/ANDROID_SHELL_PLAN.md |
| L18 | **The QA Bot deploy gate cannot see the app.** In both 25 Sep gate reports every probe was answered 403 before reaching the app (640/640 at 08:07Z, 629/629 at 07:18Z) -- even public routes such as GET /quick/me and POST /listings/quick-publish -- so every route "passes" and the gate can only fail through its database-snapshot diff. | [C] | Find what answers the bot 403 (edge, nginx or portguard for QA_BASE=https://trustsquare.co), point the attack at 127.0.0.1 as its own header comment intends, and add a ledger entry that fails when more than 90 % of probes share one status. **HALF SHIPPED 2026-09-25 20:3xZ — QA-GATE-BLIND-1.** The 90%-check asked for here was built INTO THE BOT rather than into the ledger, deliberately: `scripts/regression_ledger.py` is inside lane `goods-fit-2026-09-25`'s work lock, and teeth that can be locked out of the gate are not teeth. The bot now runs a public-route canary (`/health`) through the same client, vantage and pinning the probes use, plus a >=90%-one-status concentration check; either one makes the run NOT MEASURED. **The damage found while fixing it was worse than the row said:** `judge()` reads 403 as PASS 'refused', so the gate passed AND `accept()` wrote the blind run over `last.json` — and `regressions()` skips any route whose previous verdict was PASS or UNPROVEN, so one accepted blind run disarms the gate for every route. `accept()` now refuses a NOT MEASURED run at the writer, and probe/gate/nightly exit 2, which `server_deploy.sh` already fails CLOSED on. Not weakened: a 300x403+200x401+60x404+40x200 board still grades. **And it does not freeze the pipeline:** an unconditional hard stop would have rolled back every release until someone with server hands fixed the vantage, so the bot now picks a door it can see the app through — the front door first, else the app's own loopback port (which it already trusts for the route list) — and names what that door does not cover ('nginx and the Cloudflare edge'). Only when NO door reaches the app is the run NOT MEASURED. `scripts/test_qa_gate_blind1.py` is red on the pre-fix source and prints the baseline damage verbatim. **WHAT REMAINS AND IS THE WHOLE ROW NOW: why the front door answers the bot 403 at all.** RG-0028's scope text names the likely mechanism — the origin accepts connections only from Cloudflare's published ranges, so a loopback-pinned request carrying no Cloudflare origin-pull credential is refused before nginx reaches the app. Needs a vantage on the box; not guessed at from here. **RE-PROBED 2026-09-26 19:1xZ — the mechanism is now CONFIRMED rather than suspected, and it is NOT the origin-lockdown theory the row inherited from RG-0028's scope text.** One command, from this vantage: `urllib` on its **default** UA → **403 `error code: 1010`, Server: cloudflare**; the identical request carrying a **named** UA → **200**. So the bot is refused by Cloudflare's bad-User-Agent rule at the edge, not by the Hetzner firewall's Cloudflare-ranges rule at the origin — which means it needs a named UA, not server hands and not origin-pull credentials. That narrows the whole remaining row to one line of the bot's HTTP client. Not shipped this run: `qa_bot/qa_bot.py` was not opened, and this is said rather than carried as a silent slip. | 2026-09-26 | /var/lib/trustsquare-qabot/reports/20260925-080733-gate.json · qa_bot/qa_bot.py:52-53 |
| L19 | **25 Sep inspection of both apps: 281 of 287 items fixed and live (six deploys, the last two 26 Sep 13:40 and 13:58 UTC); every item's closure note is on `INSPECTION_2026-09-25_CLOSURES.html`.** David's four answers (26 Sep) carried: one word 'listing' in both apps and the server's messages (RUL-040 amended: AI EXAMPLE GENERATED LISTING); a real banking form on the Billing tab and after publishing, saying the details confirm who she is and are used when she buys Tuppence, never for payouts; the nine Quick pictures kept for later; and qa-11 closed — POST /agencies/wave-prep is admin-only with no loopback pass, CityLauncher 138a607 sends the admin key (probed on the box: 401 without, empty 200 with). Verified live with every write faked; ledger RG-0495..0506 guard the fixes. Kept by design: per-city counts, Quick's 'who am I', 'pass Quick on', the Quick pictures. **Open: langt-01/27 — the Terms v1.19 DRAFT** (`eula_clean_v1.19_DRAFT.html`, 88 corrections, not published; change log `terms_v1.19_changes.json`) waits for David's sign-off and 11 decisions on `TERMS_v1.19_REVIEW.html` (put to him 26 Sep). | [D] | David: the Terms v1.19 sign-off and its 11 decisions; then Claude lands it (decisions into the text, version 1.19 — material or not per his answer — eula_sync.py, LEGAL_VERSIONS.md + canon.yml, one deploy). | 2026-09-26 | INSPECTION_2026-09-25_CLOSURES.html · TERMS_v1.19_REVIEW.html · changelog.d/2026-09-26-listing-banking-terms.md · changelog.d/2026-09-26-wave-prep-admin-only.md |
| L20 | **The fact board is convicting itself, and its loudest verdict went unread for 26 hours.** The whole-board run this stand-up reached (476 entries, stable) prints **2 REGRESSED** and both are the instrument, not the product. **RG-0028** FAILs with *"/health does not answer through Cloudflare"*: reproduced in one command — `urllib` on its default UA gets **403 `error code: 1010`** (Cloudflare's bad-UA refusal), a named UA gets **200**. That is BIT-EDGE-BLIND-1, fixed in `bit/bit_runner.py` on 23 Sep and never carried into `scripts/regression_ledger.py`. **RG-0391** says the Quick manifest moved and *"quick.html no longer links its manifest"*: live `/quick/` carries `rel="manifest" href="/static/brand/quick.webmanifest?v=2"` (count 1) and repo and live manifests are byte-identical — a stale assertion from the `/quick.html` -> `/quick/` door move. **Separately: `host_queue/done/20260924-200620-614_...regression-ledger.result` came back 24 Sep 22:25 carrying `RESULT: 4 previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.` Nothing read it for 26 h, and eleven host actions plus several deploys ran over it.** The result file also cannot say WHICH four: the host agent keeps only an output tail and the per-entry REGRESSION lines fall outside it. | [C] | Three things, none of them David's: (a) carry the named-UA + edge-refusal detector from `bit/bit_runner.py` into the ledger's HTTP client so an edge refusal reads BLIND, never REGRESSED (RG-0401 already rules this — the ledger just never got the fix); (b) re-aim or retire RG-0391's manifest assertion against the `/quick/` door that actually shipped; (c) make a queued board verdict unmissable — have the ledger write its own verdict file into the repo on every run, so the names survive any caller's truncation, and have the stand-up read the newest `host_queue/done/*.result` before reporting. **Not started this run: `scripts/regression_ledger.py` and `quick.html` are both inside lane `goods-fit-2026-09-25`'s work lock (taken 11:21:58Z, live under the 12 h TTL). RUL-140 is a stand-off, not a preference — recorded rather than raced.** **NARROWED 2026-09-26 19:3xZ — (a) SHIPPED, (b) already done by another lane, (c) is the whole row now. And this row's own diagnosis of (a) was WRONG.** It blamed a missing named User-Agent in the ledger's HTTP client. `scripts/regression_ledger.py:84` has carried `TrustSquare-RegressionLedger/1.0` since it was written, and probed 26 Sep that UA gets **200** from `/health` while only the bare urllib UA gets `error code: 1010` — so a missing UA was never the mechanism. The real one: `_get()` has told an edge refusal from an app answer since EDGE-BLIND-1, but **`_status()`, `_post_status()` and `_headers()` never learned it**, so a transient edge refusal mid-board is handed back as the APP's status code. Two-sided: an entry asserting `/health == 200` CONVICTS a healthy site (RG-0028), and an entry asserting a route refuses anonymous callers PASSES without the app being reached — QA-GATE-BLIND-1's hole one layer in. **(a) FIXED as EDGE-STATUS-BLIND-1**, one writer `_edge_refused()` consulted by all four readers (RG-0421's pattern), not weakened: only a refusal Cloudflare SIGNS counts, so an app 401/403 still returns its code and origin 5xx stays in `_get()` per UPSTREAM-BLIND-1; `scripts/test_edge_status_blind1.py` red on the pre-fix source and prints both failure modes verbatim. **(b) was already discharged by the maintenance loop at 05:42Z today** — RG-0391's manifest assertion re-aimed at the `/quick/` door that actually shipped (`changelog.d/2026-09-26-maintenance-loop.md`), so this row asked for work another lane had done. **(c) REMAINS and is the whole row:** the ledger must write its own verdict file into the repo on every run so the per-entry REGRESSION names survive the host agent's output-tail truncation, and the stand-up must read the newest `host_queue/done/*.result` before reporting. This stand-up DID read it (14:15:07Z, rc=0, a docs push — no verdict in it), so the 26-hour unread-alarm failure did not repeat; the durable half is unbuilt. | 2026-09-26 | board run 2026-09-25 20:2xZ (476 entries, 2 REGRESSED) · host_queue/done/20260924-200620-614_...result |
| L22 | **The daily watch is still probing two admin routes anonymously, so it reads blind by design.** SEC-GATE-1 (24 Sep) declared `GET /dashboard/bit`, `GET /dashboard/maint` and `GET /payment/test` **admin** in `route_policy.json`; the watch's checks send no credential and so read `401 {"code":"admin_required"}` and record "STILL BLIND" (DW-158, three days running). **PROBED 2026-09-26 19:1xZ:** all three answer **401** anonymously and **200** with `X-Admin-Key` — the instruments are healthy (`/dashboard/maint` run `20260926T172118Z`, brain GREEN; `/dashboard/bit` 8/8 PASS ran 19:02:29Z); only the watch's door is wrong. The false docstrings that invited an anonymous reader were corrected at source this run (INSTRUMENT-DOOR-1), which stops the NEXT reader going blind but does not re-open the watch's eyes. | [C] | Give the watch's three checks the admin credential the same way `dashboard.server.html`'s fetch wrapper does, then close DW-158 against a dated probe that reads a real verdict. Technical throughout — no part of this is David's. Recorded here and not as a new ledger entry because DW-158 is another lane's board and RUL-140 says a lane records rather than races. | 2026-09-26 | INSTRUMENT-DOOR-1 · DAILY_WATCH/OPEN_ITEMS.md DW-158 · route_policy.json |
| L23 | **The post-deploy BIT run measures nothing and posts an empty board.** MEASURED 2026-09-26: empty POSTs to `/dashboard/bit` at **19:36:04Z** and **19:42:24Z**, each within seconds of an app restart from this run's two deploys, while the 15-minute `trustsquare-bit.timer` posted real 8/8 boards either side (**19:02:29Z** and **19:47:54Z**). So the post-deploy runner races the restart, every check errors, and it posts a board with no results. Until BIT-STORE-FLOOR-1 shipped this run, that **overwrote the real verdict and blanked the dashboard panel after every deploy** until the next timer tick repaired it — a 15-minute blind window, repeated on every release, never caught because it healed itself. | [C] | The store no longer lies (BIT-STORE-FLOOR-1: NOT MEASURED never becomes the record, verified live both ways), so this is no longer damaging — but the runner should WAIT for the app to answer before it grades, and report NOT MEASURED itself rather than posting an empty board. Likely the same stale `ops/bit/bit_runner.py` copy **L13** names (11 Aug, probes `localhost:8000`); fix it there and L13's factoring becomes the natural vehicle. Technical throughout. | 2026-09-26 | BIT-STORE-FLOOR-1 · changelog.d/2026-09-26-standup-instruments-design-route.md · L13 |

## ⚪ DECISIONS AWAITING DAVID / COUNSEL — ranked

| # | Decision | Owner | Single next action | Opened | Source |
|---|----------|-------|--------------------|--------|--------|
| D16 | **The 92-role beta slate (RUL-150) — which roles TrustSquare opens with.** `ROLE_SLATE_REVIEW.md`, created 19 Sep for David's review discussion, is marked up to **61 IN · 19 LATER · 19 OUT** across ~102 role rows, and the roles/employer lane is **held pending his review** (commit `758a9de`). It existed only in a commit message and a working file — not here — which is the failure mode rule 2 of this file exists to stop. | [D] | The rows are largely decided; what is genuinely his are the five OPEN QUESTIONS at the head of that file: split or drop the "Miner"/"Industry worker" sector buckets · where Chef sits · which roles make police clearance effectively mandatory (child contact / home access) · which employers to approach first · the four taps per class. Launch scope, so his. **CORRECTED 2026-09-23 — two things in this row were false.** (i) It says the roles/employer lane is *held pending his review*. It is not: `c30c33d` (20 Sep 02:49Z) shipped QUICK-SVC-DOOR-1 — the seven-category Services door, `roles/role_registry.json` with **99 rows carrying `counts {in:61, later:19, out:19}`**, 61 role pictures and the language preview. The lane shipped the IN rows the day after this row claimed it was frozen. (ii) One of the five open questions — *what are the four taps for each class* — **was already ruled**: RUL-159 (19 Sep, the same day this row was opened) sets Services tap 1 = group, tap 2 = role, then Casuals where/days/rate and Technical qualification/where/call-out, and drops the 'what' tap entirely. **So his queue here is FOUR questions, not five**, and none of them blocks any build. Third consecutive stand-up to find a row in his queue that was already a fact. | 2026-09-19 | ROLE_SLATE_REVIEW.md · QUICK_LISTING_SPEC.md Part II · RUL-150/151/152 |

| D9 | **FLIP-DRILL-1: pick the hour** — runbook ready (`FIRE_DRILL_RUNBOOK.html`). DEFERRED by David 5 Aug 2026 ("needed, just not now") — STANDS OVER till after launch (David, 11 Aug). | [D] | David names a quiet hour when ready; Claude keeps the log. **Note 18 Sep 2026: the condition this was deferred ON — "till after launch" — lapsed at full launch on 1 Sep, 17 days ago. Still genuinely his (naming the hour); no longer waiting on anything.** | 2026-08-03 | this session |
| D10 | **Travelpayouts tours programs — RESUBMITTED 22 Aug 2026 (David's word, per RUL-041).** The 5 Aug decline (*'website under development or not yet ready'*) blocked GYG · Viator · Welcome Pickups · Booking.com and 22 others; 26 programs auto-connect on approval. Submitted with the site answering publicly and the changed face being real (EULA v1.14 live, gate down, honesty labelling in flight) — not a resubmit-unchanged. Aviasales flights Data API unaffected. **TRAVELPAYOUTS_TOKEN is UNROTATABLE** (one permanent token per account, copy-only, verified on the API page 22 Aug) — accepted risk, reasoned and dated in SECRETS_REGISTER.md, policed by RG-0146. | [D] | **OUTCOME READ 24 Aug 2026 — DECLINED AGAIN, same reason.** Probed at app.travelpayouts.com (project Trustsquare, ID 758984): *"20 programs are currently unavailable… Your website is currently under development or not yet ready. Please complete setting up your site and re-submit your Project for review."* Available **26** / blocked **20** — Booking.com, Viator and GetYourGuide all still blocked. The 22 Aug "we've connected you to relevant brands" email is their generic template, NOT an approval (evidence-ladder: email READ said yes, dashboard PROBE said no; the probe wins). Per RUL-041: do NOT resubmit unchanged — the next submit waits until the site's changed face is materially different (soft launch, 29 Aug, is the natural moment, and the timing call is David's). Their dashboard is meanwhile offering **+25% GetYourGuide rewards, expiring 24 Aug, to switch the Drive loader back on** — declined; all five Drive functions stay Off. Safe lane BUILT instead: travelpayouts_partners.py (TP-LINKOUT-1), server-side 302s, host allowlist, dark by flag, RG-0181. Original standing rule unchanged: commercial lane only — server-side or link-out, NEVER a TP script (RG-0025). **CONDITION EXPIRED — corrected 2026-09-19.** This row said the next submit waits for a materially changed face, *"soft launch, 29 Aug, is the natural moment"*. Soft launch happened 29 Aug and FULL LAUNCH happened 1 Sep; the trigger fired 21 days ago and the row went on describing it as future. The row is also mis-tagged **[C]** while its own text says *"the timing call is David's"* — per RUL-041 the resubmit is his word, so the tag is wrong, not the rule. **Single next action, unchanged in substance: David says resubmit (or not).** Nothing technical is waiting. | 2026-08-05 | RUL-041 · scheduled follow-up |
| D11 | **Maroushka's TS-0022 letter drafted** — the retest letter IS the remediation (9 pre-fix covers need her re-upload; class fix RG-0047 live). | [D] | **ACTION CORRECTED 18 Sep 2026 — "retest-send" DOES NOT EXIST.** `grep` finds no `retest-send` route in `bea_main.py`; the only fault-letter endpoints are `/admin/faults/{fid}/close-draft` and `/admin/faults/{fid}/close-send`. **NO-RETEST-1 (David, 11 Aug 2026 — the same day this row was opened) retired the retest lane in his own words: "there are no retests… the retest-wait status is retired", legacy rows migrated by `migrations/012`.** The row therefore asked him for 38 days to fire an endpoint his own ruling had deleted. Live mechanism, unchanged in substance: GET close-draft → David approves → POST close-send, which closes the fault and stamps `verified_at`. Still his: the send. | 2026-08-11 | Records/FAULT_RECONCILE_2026-08-11.md |
| D15 | **Study & Work-Abroad Advisor (Maroushka's idea, 22 Aug — RUL-042).** Positioning RULED: preparation is ours, based on actuals (possible / typically needed / viability, risks, opportunities); partner education & immigration agencies take the Dossier and provide the actual plans and guidance — that handoff IS the introduction. Assessment on disk: ~$0.50–1.00/report vs 5T = $10, existing 5T deep-dive class, no paid feed, ~70% reuse, MVP 3–5 sessions (one corridor first). | [D] | TEASER: DECIDED 22 Aug (David — 'build it now, no risk to baseline') — built as SAW-1 (static page + banner + manifest line, RG-0158 OPEN), rides the next deploy. UPDATE 23 Aug: 5T CONFIRMED + build GREENLIT + work-route example added (RUL-043); videos full-length, SHELVED until spec approved. Remaining to David: ~~deploy timing (rides next TSL)~~ **— DISCHARGED 18 Sep 2026: the teaser is LIVE, probed 200 at `/static/studyabroad_teaser.html`, and has been since before 24 Aug, when RUL-050 deliberately retired its index banner (unlisted, still live). Deploys also stopped being David's at RUL-092 (3 Sep). Two reasons this limb was never his.** · agency outreach approach (education + placement agencies — sending is his) · the video unshelve moment. Plus a business action: recruit 2–3 founding education/immigration agencies (same lane as travel agencies). | 2026-08-22 | RUL-042 · STUDY_WORK_ABROAD_ADVISOR_ASSESSMENT — nice.docx |

## ✅ CLOSED — last 7 days

| # | What | Owner | Disposition | Opened → closed | Source |
|---|------|-------|-------------|------------------|--------|
| L8 | **CLOSED 2026-09-26 19:3xZ — 26 days, and the row's PREMISE was wrong, not just its status.** It said the `design` tier had never been called and prescribed wiring a caller; it was re-probed on 19, 23, 24 and 25 Sep, each time finding `grep -rn 'task="design"' → **0 callers**, each time recording the same zero. **DATED PROBE THAT DISCHARGED IT (26 Sep 19:1xZ):** the tier was wired at the chokepoint the whole time — `bea_main.py:25371` carries `_MAINT_TIER_LADDER = ("design", ...)`, `_MAINT_DEFAULT_MAX_TOKENS["design"]=4000`, and `/admin/maint/brain` accepts `task="design"`. What was missing was DEMAND: `grep -rn DESIGN_BACKLOG scripts/` returned **0 writers**, `GET /admin/faults?limit=500` returns **40 rows, 26 verified / 12 closed / 2 duplicate / 0 unadjudicated** (no design work waiting), and **TS-0027 and TS-0006 were both closed 11 Aug 2026 with "routed to the design backlog" in their fix_note while `DESIGN_BACKLOG.md` holds exactly one dossier — DCB-001 — which is neither of them.** PATH_B's routing was a sentence the report wrote about itself. So the zero-caller count was the SYMPTOM and four stand-ups re-probed the symptom; **LAG: the row misdescribed its own cause for 7 days across four passes.** Fixed at source as **DESIGN-ROUTE-1**: PATH_B files a real dossier in the template `DESIGN_CHANGE_GUIDELINES.md` publishes, asks the **design tier** for the PROPOSED DIRECTION (`task="design"` — RUL-013's allocated lane, its first real caller) and stamps the serving model, reports the dossier id actually written, is idempotent across the loop's three daily runs, and writes the **GATE line EMPTY** because criterion 10 says an absent gate means NOT APPROVED, DO NOT BUILD and binding the designer role is open item 2 and David's. `scripts/test_design_route1.py` red on the pre-fix source, printing the measurement above. **Envelope re-derivation is NOT claimed:** `AI_BASELINE.json tiers/design` still reads *"DECLARED, not measured"* and its own `_doc` says re-derive from real call shapes — the first real call shape now exists to derive from, which is what that gate was waiting for. | [C] | Discharged — the caller exists and the proxy assertion is gone. | 2026-09-19 → closed 2026-09-26 | DESIGN-ROUTE-1 · changelog.d/2026-09-26-standup-instruments-design-route.md · scripts/test_design_route1.py |
| L21 | **CLOSED 2026-09-26 19:1xZ — the stall cleared itself exactly as the row predicted, and the detector that would catch the next one is live.** The row recorded `autodeploy_agent.bat` stopping for 7h31m on 25 Sep with 5 commits stranded off the mirror. **DATED PROBE:** `git fetch origin && git rev-list --count origin/main..HEAD` = **0** — nothing stranded; the queued push `20260925-203849-091_git_push_marketsquare.req` executed as the row said it would, and the host agent completed **three** actions today, the newest `20260926-140213-767_git_push_marketsquare.result` at **14:15:07Z rc=0** (`65170ba..f643535`). The queue is empty now, and per HOSTQUEUE-WATCHDOG-1's own rule quiet is not an alarm — the agent only writes a result when there is work. **LAG: none — opened 25 Sep, discharged 26 Sep.** The residual the row named (*why* the agent stopped) is not carried forward as a loop: the detector now reports a stall with the oldest item named, so the next occurrence arrives as an alarm with evidence rather than as a silence to investigate afterwards. | [C] | Discharged. | 2026-09-25 → closed 2026-09-26 | HOSTQUEUE-WATCHDOG-1 · host_queue/done newest result 14:15:07Z rc=0 |

### Closed 2026-09-24, eighth pass (stand-up, 19:00Z slot, mechanical — SO-3/RUL-037).

- **L12 CLOSED 2026-09-24 — the last ledger row aimed at David is gone, and it was never his.**
  RG-0426 told him to provision an AI vendor key, with the money framed as his call. He already
  owned it. The entry read `/proc/<pid>/environ` alone, citing RG-0147's "check at the point of
  use" — but the point of use is `ai_provider.envkey()`, which by ENVKEY-1's *design* (17 Jul
  2026) falls back to `/var/www/marketsquare/.env` **because the systemd unit does not export
  it**. A .env-sourced lane can never appear in that read, so the check could only ever FAIL
  whatever the box carried. **DISCHARGING PROBE 2026-09-24 20:0xZ:** re-aimed as ENVKEY-BLIND-1
  (**RG-0462**, LOCKED) to the union of both doors — unit-exported names from `/proc` **and** the
  lanes `ai_provider.configured_lanes()` resolves on the box; `scripts/test_envkey_blind1.py` is
  red on the pre-fix source and drives a genuinely one-lane box to prove the teeth survived.
  Shipped in `63839fd`, relayed 20:03Z. Corroboration that needed no credential at all, published
  all along: `/dashboard/maint` reports `brain_lane openai`, `brain_keyed true`,
  `brain_probe {ok:true,status:200}`. **Lag: 4 days as a row pointing at David (opened 20 Sep),
  1 day as an OPEN_LOOPS row.** Nothing was bought and nothing was his.

- **L11 CLOSED 2026-09-24 — the three orphaned instrument fixes now have numbers, proofs and
  fragments.** L11 was opened 23 Sep because LEDGER-VANTAGE-BLIND-1, BIT-EDGE-BLIND-1 and BIT-NS-1
  shipped as code with no ledger entry and no changelog fragment — rule 2's failure mode reached
  honestly, by standing off another lane's work lock rather than by forgetting. **DISCHARGING PROBE
  2026-09-24 19:2xZ:** every path L11 named (`scripts/regression_ledger.py`, `changelog.d/*`,
  `status.d/*`) checked clear of the day's lock, so the work was landed rather than recorded again:
  **RG-0459** (LEDGER-VANTAGE-BLIND-1), **RG-0460** (BIT-EDGE-BLIND-1, carrying the do-not-overwrite
  warning for the ops copy that L13 is about) and **RG-0461** (BIT-NS-1), plus
  `changelog.d/2026-09-24-instrument-blindness.md` and its status fragment. Shipped in `63839fd`.
  **Lag: 1 day, and it was a deliberate hold, not a miss.**

- **The board could not run at all, and that was found only because this pass insisted on a real
  figure.** `--chunk` returned `next=24/449` on three consecutive calls. LEDGER-CHUNK-1 checkpoints
  *after* each entry, so it survives any aggregate weight but not one entry heavier than the whole
  ~180s cap — entry 24 is RG-0025 (eleven live map reads plus a manifest-wide regex scan). Every
  call died inside it, the checkpoint was never reached, and the board had been **permanently
  unrunnable from this stand-up's own vantage, silently**, because a killed command prints nothing.
  Fixed same run as **LEDGER-ENTRY-CEILING-1 (RG-0463)**: each entry gets the room left in the call,
  and a cut raises through a `BaseException` subclass — the first cut of the fix raised
  `ProbeOffline` and RG-0025's own `except Exception` **swallowed it**, leaving the board still
  wedged — landing on RG-0187's blind path: UNVERIFIED, never green. An entry that merely starts
  late is retried with a whole window instead of being blinded for it.
  `scripts/test_ledger_entry_ceiling1.py` pins the half that matters: a cut entry must never read
  HOLDING. Not opened as a loop because it opened and closed inside one run.


### Closed 2026-09-23, seventh pass (stand-up, 19:00Z slot, mechanical — SO-3/RUL-037).

- **L10 CLOSED 2026-09-23 — both instruments it named now report their own blindness instead of convicting
  the app, and a THIRD one was found and fixed the same way.** L10 was opened at 17:0xZ today with two named
  next actions, both deliberately left unwritten because another lane held the files. The tree was quiet on
  those paths this run and both landed.
  **DATED PROBE, 2026-09-23 19:4xZ — the fault first, measured, not recalled:** a full 24-shard board run
  (417 entries) printed **`RESULT: 4 previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.`**
  The four were **RG-0229, RG-0230, RG-0252, RG-0399**, and every one asserts on `../CityLauncher/…` files or
  the Projects-root `CLAUDE.md`. `ls $HOME/mnt/` returns **MarketSquare alone**; the siblings are on David's
  machine and are not mounted on this task. So four fixes were reported as rotted, under a banner that blocks
  deploys, on a tree where nothing was missing.
  **FIX 1 — LEDGER-VANTAGE-BLIND-1.** `sibling_visible()` and `projects_root_visible()` added beside
  `repo_file()`, and applied at the five convicting reads. The test is whether the PROJECT ROOT is mounted, not
  whether the file is there — so on David's PC and on the host agent, the two vantages that run from the real
  Projects folder, a genuinely deleted `ssh_bootstrap.py`, marker or bat still FAILs exactly as before. The
  four now read **UNVERIFIED with a named blind reason** (re-judged individually at 20:0xZ; RG-0425 reads
  HOLDING). `scripts/test_ledger_vantage_blind1.py` pins both halves and, run against the pre-fix file, prints
  the two false convictions verbatim — proven to fail on the old code, not assumed to.
  **FIX 2 — STANDUP-WATCHDOG-1 wired.** `report["standup"] = _standup_lane()` now sits beside the backup lane
  in `scripts/maintenance_agent.py`, so the ~20-minute loop reads the freshness of the stand-up's own output.
  Verified returning `{'ran': True, 'state': 'FRESH', 'age_h': 0.0}`. This is the detector for the two silent
  outages already on the record — 47 unlogged days (2 Aug–18 Sep) and three missed firings (20–22 Sep) — both
  of which were found by a human reading a file weeks later, which is not a detector.
  **FIX 3, NOT IN L10, FOUND BY GOING LOOKING — BIT-EDGE-BLIND-1.** The BIT board printed **7 FAIL including
  an S1 and `Worst severity exit=2`**. Measured in the same minute: `curl https://trustsquare.co/health` →
  **200**, the runner's own urllib client → **403, `Server: cloudflare`, body `error code: 1010`** —
  Cloudflare's bad-User-Agent refusal, which fires on the default `Python-urllib/3.x`. curl, browser and a
  named UA all returned 200; only the default was refused. Every check in the file opens
  `if st != 200: return False`, so one refusal became seven convictions. Fixed with a named UA and an
  edge-refusal detector that exits **3 = NOT MEASURED** rather than convicting — and NOT weakened: the
  signature tested is Cloudflare's own, so a real app-issued 403 still fails its marker, which
  `scripts/test_bit_edge_blind1.py` proves by standing up a server that returns a plain 403. Board re-run after
  the fix: **8/8 PASS, exit 0**. A fourth instrument, `scripts/golden_seam_v2.py`, died on
  `NameError: name 'os'` before reaching its own key check, because today's `bea_main.py` edit gave the lifted
  `_build_vision_prompt` slice an `os.environ` read the hand-kept namespace never carried (BIT-NS-1 — stdlib
  now resolved on demand, and a still-missing name exits saying THE BOARD DID NOT RUN).
  **THE PATTERN, WHICH IS THE POINT OF CLOSING THIS ROW RATHER THAN JUST TICKING IT.** This repo has now
  settled one doctrine — *a probe that cannot reach its target reports that it could not reach it; it does not
  return a verdict* — in **six** separate places: RG-0187, RG-0401/EDGE-BLIND, RG-0420/UPSTREAM-BLIND,
  RG-0423/SELFREAD-DIAG, VANTAGE-BLIND-1, and now LEDGER-VANTAGE-BLIND-1 and BIT-EDGE-BLIND-1. Every instance
  has been fixed one instrument at a time, and each new instrument arrives without the doctrine. **On this one
  day, three separate instruments convicted the app of eleven faults it did not have, two of them carrying
  language that stops a deploy.** The false-red rate of the instruments is now a larger risk to trust than the
  fault rate of the app, and the next structural move is a shared blind-read contract every instrument is built
  on rather than a seventh hand-application of the same lesson. **LAG on L10's own two actions: one run
  (~3h).** The lag that matters is the other one: RG-0229/0230/0252/0399 have been convicting on an unmounted
  sibling since this task's mount was narrowed, and the 16:5x stand-up named five such entries in its pulse
  line and could not act on them — so the board has been carrying a false 'do not deploy' for at least two
  runs.


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
