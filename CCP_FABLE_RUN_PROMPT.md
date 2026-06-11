# Fable Run Brief — Execute the Change-Control Protocol on CC-001 + CC-002
**For: an autonomous coding agent.  Author: Claude (Opus 4.8).  10 June 2026.  Project: TrustSquare / MarketSquare.**

You are running **unattended** while David is at work. Do **not** wait for input — start now, drive end-to-end, and finish with a written report. Don't summarise back before starting; begin executing. Where something is genuinely David's call, **stage it** (see HARD STOPS) and keep going on everything else.

David is adding all Project folders to your access: `C:\Users\David\Projects\MarketSquare` (main) and its `Patents\` + `n8n\email_templates\` subfolders, plus `AdvertAgent`, `CityLauncher`, `Codices`.

---

## 0 · Mission (scope is exactly these two changes — nothing else)
Apply the **Change-Control Protocol (CCP)** to the two queued changes — **CC-001 (Tuppence HOLD)** and **CC-002 (Pricing + AI canon)** — doing all the **reversible** work (baseline, evidence-based term maps, traceability matrices, branch edits, tests) and **staging every live/gated cutover for David's approval. Nothing goes live today.** Do CC-001 fully first, then CC-002.

## ⚠ OPERATING MODE — run continuously, NEVER BLOCK (the most important rule in this brief)
- You run for the **FULL session**. **Never pause to ask, never end your turn to wait for David, never write "let me know how you'd like to proceed."** David is unreachable for ~8 hours — a question asked is a question unanswered until tonight.
- **First action:** create `C:\Users\David\Projects\MarketSquare\AWAITING_DAVID.md` and `PROGRESS_LOG.md`.
- The **moment** you hit anything needing his decision, approval, or clarification: append it to `AWAITING_DAVID.md` — the file, the exact question, **your recommended answer**, and what you did in the meantime — then **immediately move to the next item.** Logging the question IS the substitute for asking it. Do not wait for the answer.
- **"Gated" / "staged" does NOT mean stop.** It means: do the work now on the branch and leave only the *go-live* for David. **None of today's work is blocked on his approval** — there is ~8 hours of un-blocked work here; do it.
- On **any error or blocker** on one item: log it, skip to the next item, continue. Never retry the same thing more than twice; never loop on one problem.
- Write a one-line **heartbeat** to `PROGRESS_LOG.md` (timestamp + what you just finished) every few steps, so David can see it ran the whole time.
- If you ever feel "blocked": you are not. Re-read this block, pick the next matrix row or the next artifact class, and continue. Only the HARD STOPS are truly off-limits — and those are **deferred to `AWAITING_DAVID.md`, never waited on.**
- If you somehow exhaust every editable item before the session ends, **keep adding value** (extra straggler greps, deeper verification, tighten the matrices, draft the reports, re-check canon consistency). **Do not finish early and idle.**

## 1 · Read first, in this order — then follow the protocol exactly
1. `C:\Users\David\Projects\MarketSquare\CHANGE_CONTROL_PROTOCOL.md` ← the method; follow its steps 0–8 literally
2. `C:\Users\David\Projects\MarketSquare\CHANGE_REGISTER.md` ← CC-001 + CC-002 + their DRAFT term maps
3. `C:\Users\David\Projects\MarketSquare\TRACEABILITY_MATRIX_TEMPLATE.xlsx` ← copy once per change
4. `C:\Users\David\Projects\MarketSquare\CLAUDE.md` ← build rules (esp. the large-file/HTML write rule, deploy rules, git rules)
5. `C:\Users\David\Projects\MarketSquare\ORCHESTRATION_POLICY.md` ← §5 the two gates, §7.1 change-mode, §12 never-automated
6. `C:\Users\David\Projects\MarketSquare\AGENT_BRIEFING.md` and `STATUS.md`
7. `C:\Users\David\Projects\MarketSquare\Solar_Council_Codex_v4_7.docx` ← **CANON. It overrides everything. Never contradict it.**
8. `C:\Users\David\Projects\AdvertAgent\CLAUDE.md` + `PRINCIPLE_REQUIREMENTS.md` + `AI_FUNCTIONS_SPEC.md`
9. `C:\Users\David\Projects\MarketSquare\Patents\TrustSquare_IP_Brief_v5_Jun2026.docx`

## 2 · HARD STOPS — never cross these, even if it seems helpful
- **No live anything.** No `scp`, `ssh`, `systemctl`, `nginx`, Cloudflare purge, no writes to `178.104.73.239` or `trustsquare.co`, no `.env`/launch-flag changes, no enabling/disabling services or scheduled tasks. **Everything stays local.**
- **No git push and no merge to `main`.** Do the edits on a branch (`ccp/CC-001`, then `ccp/CC-002`). If git is locked/unavailable, instead write the changed files as copies + unified diffs under `C:\Users\David\Projects\MarketSquare\_CCP_STAGED\`. Leave David a paste-ready PowerShell commit block; **never run git commit/push yourself** (sandbox lock risk).
- **No product API / model calls.** This is deterministic dev work — $0 in product terms. Do not call AdvertAgent (service 8002) or CityLauncher AI, do not enable any `ANTHROPIC`/product key.
- **Never edit the published `TrustSquare WhitePaper v2.docx`.** Route any whitepaper change into a new **Addendum** draft instead.
- **Never add, suggest, or implement any Tuppence refund / reversal / release-of-funds-back-to-buyer mechanism.** Non-refundability is load-bearing (Banks Act + patent + CPA). A "hold release on decline" is the *un-spent* hold being freed — not a refund of spent money; keep that distinction exact.
- **Big-file rule (critical).** Do **NOT** use editor/Write tools on `bea_main.py`, `marketsquare.html`, `marketsquare_admin.html`, or `ms.js` — they truncate. Use Python `open().read()` → `str.replace()` → `open().write()`, then **verify**: `ast.parse` for `.py`, `node --check` for `.js`, and `content.rstrip().endswith('</html>')` for the HTML files. If any file ends up truncated, restore from git/server and retry.
- **Don't invent or reinterpret canon.** Where a rule's meaning, a new value, or a phrasing is ambiguous, make your **best-effort DRAFT on the branch**, write the question + your recommendation to `AWAITING_DAVID.md`, and **immediately continue**. Never guess silently and **never halt to wait** — park the decision and keep moving. The Codex decides; if it's silent, the parked question is David's.
- **Treat every pricing / Tuppence / ledger / Codex / IP / EULA edit as GATED — meaning: DO it on the branch and prove it, but leave the go-live staged for David.** "Gated" never means "wait for him"; it means "don't deploy." None of today's work is blocked on his approval.
- **Don't delete.** If you supersede a doc, move the old one to `_ARCHIVE\` (reversible). Never print or stage secrets (`.env`, `ssh_hetzner_key`).

## 3 · The two changes (new values are David-sourced from the register; OLD wording you must discover)
**CC-001 · Tuppence HOLD** — the charge model becomes **commit-on-request → burn-on-delivery → release-on-decline**; the **payer is the service consumer** (the party requesting the introduction). Canonicalise toward **Codex v4.8** and **IP Brief v6**, adding patent claims **C10–C13**. *(Codex/IP/claims edits are staged drafts, not final — David lands canon.)*

**CC-002 · Pricing + AI canon** — retire **"AI uses" / "sessions"**; everyday in-app AI guidance is **FREE**, advanced AI is **priced per use in Tuppence**. Plans = **$0 / $12 / $20 / $40 / $100**; monthly Tuppence = price ÷ 2 = **6 / 10 / 20 / 50T** (anchor **1T = $2**); listing slots (a CAP) = **2 / 10 / 25 / 60 / 500**.

> These term maps are **DRAFT pending David's verification**. You MAY discover exact old wording, build the matrices, and prepare branch diffs — but the whole package is provisional until David verifies the term map and approves. If discovery shows the real old wording differs materially from the draft, **update the term map with file:line evidence and flag it**.

## 4 · Do this per change — CC-001 first, then CC-002 (follow the protocol's steps)
- **Step 0 — Baseline.** Tag `ccp/CC-00X/baseline` (or record the HEAD sha + a snapshot list of the canon/IP/cost files) before touching anything.
- **Step 2 — Evidence the term map.** For every `old` token, grep the **whole tree** (all folders above). Record the **exact current wording** and **every** `file:line` occurrence. Fill the **Term Map** tab of `MATRIX_CC-00X.xlsx` (copy the template). One row per distinct written form (e.g. "AI uses", "AI-uses", "uses of AI" are three rows). Flag any token whose replacement isn't clearly specified.
- **Step 3 — Build the matrix.** Walk **every one of the 12 artifact classes** in the protocol §4 and grep each. Add a **Matrix** row per `(artifact × change-item)` hit, `status=pending`. A class is only clear at **zero hits**. Use the xlsx skill at `C:\Users\David\AppData\Roaming\Claude\...\skills\xlsx` (or openpyxl) and run its `recalc.py` so the Resolved% cell has no formula error.
- **Step 4 — Implement on the branch.** Apply the replacements **matrix cell by cell**, one artifact fully before the next, with the big-file discipline above. For any **new FEA API call**, add the `DEMO_MODE` guard (both branches) per CLAUDE.md; if you touch `LISTINGS`/`SELLERS`, run the demo-data integrity audit. Tick each matrix row `edited` → `verified` as you go.
- **Step 5 — Prove (the verified bar).** Re-grep **all** term-map `search` terms across the tree → must return **ZERO** surviving old tokens (or each survivor logged as legitimate in notes). `ast.parse` / `node --check` clean on changed code. Run `python smoke_test.py` (local, read-only) → must be **green**. Matrix must be **100%** (`verified` or explicit `N-A` with reason).
- **Report — `REPORT_CC-00X.md`.** What changed; matrix coverage %; the surviving-old-token grep result (should be zero); test results; the branch / `_CCP_STAGED` location of the diff; the rollback point (baseline tag); a `Cost model impact:` line if pricing/AI volume/concurrency moved; and the **AWAITING DAVID** list (every gated edit + every ambiguity you stopped on).

## 5 · Output artifacts (save into `C:\Users\David\Projects\MarketSquare\`)
- `MATRIX_CC-001.xlsx`, `MATRIX_CC-002.xlsx` (from the template, fully populated).
- Updated `CHANGE_REGISTER.md` term maps — now **evidence-based** (exact old wording + file:line), with any drift flagged.
- The branch(es) `ccp/CC-001` / `ccp/CC-002` **or** `_CCP_STAGED\` with changed files + unified diffs.
- `REPORT_CC-001.md`, `REPORT_CC-002.md`, and one top-level `CCP_RUN_REPORT_2026-06-10.md`.
- Any Codex/IP/EULA changes as **staged drafts** (e.g. `Solar_Council_Codex_v4_8_DRAFT.docx`, `IP_Brief_v6_DRAFT.docx`) — never overwrite the live canon/published files.

## 6 · Definition of done (today's unattended envelope)
Discovery + both matrices + branch/staged diffs + tests-green-on-branch + the three reports + a single consolidated **AWAITING DAVID** approval list — with **nothing deployed, nothing pushed, nothing merged to main, no live canon/published file overwritten.** End there. David reviews tonight, approves the gated items, and ships via PowerShell.

## 7 · Final report — put this at the top of `CCP_RUN_REPORT_2026-06-10.md`
1. One-paragraph outcome per change.
2. Matrix coverage % and the **zero-surviving-token** proof for each.
3. Test results (smoke + parse/check).
4. Branch / diff location + the baseline rollback tag.
5. **AWAITING DAVID** — numbered list of every gated edit and every ambiguity, each with the file, the proposed change, and why it's staged.
6. The paste-ready PowerShell block for David to review/commit/push (do not run it).
7. `Cost model impact:` line if applicable.

*End of brief. Follow CHANGE_CONTROL_PROTOCOL.md for anything not spelled out here. When in doubt: stage, don't guess; local, never live.*
