# Build Brief — Build the Simpler Model (the new design)
**For: the build agent (David's chosen model).  Author: Claude.  Draft for David's review — do NOT run until he approves.**

You are **building the new product design** David, Maroushka & Dave Junior agreed on — not sweeping documents, not adjusting wording. Build the working app to match the **Simpler Model**.

---

## 0 · THE SPEC IS THE DOC — read these first, and they win over everything
The authoritative spec is in `C:\Users\David\Projects\MarketSquare\`:
1. **`MarketSquare_Simpler_Model_Options.docx` — build OPTION A** (the recommended model + the "five moves"). This is the spec.
2. `MarketSquare_Revenue_Bridge.docx` — the costing that backs Option A (why it works).
3. `Agency_Model_Deliberation.docx` — why agencies are free + the quality-gate guardrails.

**Rule: if ANY memory, note, `CHANGE_REGISTER.md`, the live code, or the Codex contradicts these docs on the pricing/AI/onboarding design, the docs win.** Do **not** trust any pre-9-June pricing (the old five-tier $0/12/20/40/100 model is the thing we are REPLACING). Read all three docs before writing code.

Also read for build rules: `CLAUDE.md` (large-file/HTML rule, deploy rules, git, DEMO_MODE rule), `ORCHESTRATION_POLICY.md` §5 gates + §12, `STATUS.md`, `AGENT_BRIEFING.md`.

---

## 1 · The agreed design (explicit, so there is no drift)
**Subscriptions — three individual tiers + free agency:**

| Tier | Price/mo | Listings (cap) | Monthly Tuppence | Who |
|---|---|---|---|---|
| Free | $0 | **2** | pay-as-you-go | one-item seller |
| Starter | $5 (~R85) | **10** | 2T | regular individual |
| Pro | $20 (~R330) | **30** | 10T | power seller |
| Agency | **Free** | **Trust-graduated** (▼ see below) | buys Tuppence + AI | EVERY category's aggregator (see below) |

- **Listings are the only upgrade lever** (no feature-gating). 1T = $2 (Pro 10T = $20÷2; Starter 2T ≈ $5÷2).
- **Agencies free**, gated by **quality not price**: verification + Trust Score + the free-listing cap (per the Agency doc). Monetised on transactions, not access.
- **Agency listing cap = trust-graduated** (throttle the new, free the proven) — a large *verified* agency must not be inhibited, while a small/unproven one must not run away. **Default ladder (tunable — David to confirm the numbers):** unverified / new = **10** · verified (identity + credentials) = **100** · verified + established Trust Score = **500**, raised further on review. The cap rises **automatically** as verification completes and Trust Score climbs — the cap *is* the throttle, and it's never a paywall.
- **"Agency" spans EVERY category** (not property-only) — the credentialed professional aggregator for each vertical, all on the one free + trust-graduated Agency tier: **Property** = estate agencies · **Cars** = dealerships (WeBuyCars-type) · **Services** = trade / service companies · **Tutors** = educational institutions (universities / schools / technikons, or similar user-groups) · **Travel / Adventures** = travel agencies, tour operators & accommodation groups (covering both **Experiences** and **Stays**) · **Collectors** = dealer shops & collector groups. Each verifies against **its own vertical's credentials** (the quality gate); the Agency account type must be **category-aware**, not a single property-shaped form.
- **Launch special (+20% Tuppence-for-life + Ruby Spark badge) — a SEPARATE gated build, NOT this run; design now DECIDED.** Window = **per-city: each city declares a launch-month start + a definitive end date**; earned by **any paid plan (Starter/Pro) or a verified agency** within that city's window; **closes hard at the city's end** (each new city gets its own founding window). This replaces the old global launch-month + $40/$100 gate (both invalid now). For THIS build: just leave a **clean hook** — do NOT hardcode any launch-month/tier rule. The launch infra (`launch_codes.py` / `launch_redemption.py` / `launch.conf`) moves from one global `LAUNCH_SPECIAL_DEADLINE` to per-city {start, end} as its own gated task.
- Slots = capacity CAP (meter UI) vs Tuppence = currency (wallet UI) — never shown as bare equal numbers.

**AI features — free glimpse + paid deep-dive, capped 5T:**
- Every research feature splits into a **free Level-1 glimpse** + a **paid Level-2 deep dive**.
- Price ladder **Free / 2T / 3T / 5T** — the old 2/3/5/8/10T spread and the 8T & 10T tiers are **retired**.
- Build the **Property Area Dossier split first** (free **Area Snapshot** / paid **Investor Dossier ~3T**), then the **Car Purchase Dossier** split.
- "AI uses" / "AI sessions" / coaching-uses mechanic is **dead** — must not exist in code or copy.

**Listing/onboarding — one photo + one sentence:**
- Seller adds **one photo + one line of intent** ("selling my 2019 MacBook, lightly used, hoping ~R15k"). The system **drafts** the title, description, category, a **condition read from the photo**, and a **suggested price** — the seller fine-tunes and publishes.
- Built **$0-first**: a cheap vision pass on the photo, templates to shape the listing, public signals for the price range; heavier model only where it genuinely helps.

**Charge wording** follows the **Tuppence HOLD** model (separate change CC-001, concurrent): committed on request → burned on delivery → released on decline/expiry. Any new copy you write must be HOLD-consistent; do not write "charged on acceptance" or any refund/deposit language.

---

## 2 · OPERATING MODE — run continuously, never block
- Run the **full session**; never pause to ask, never end your turn to wait for David (he's at work ~8h).
- **First action:** create `AWAITING_DAVID.md` and `PROGRESS_LOG.md`.
- Anything needing his decision/approval → append to `AWAITING_DAVID.md` (the question, your recommended answer, what you did meanwhile), then **continue**. Logging the question replaces asking it.
- Any error/blocker on one item → log it, skip to the next, continue. Never retry >2× or loop.
- Heartbeat one line to `PROGRESS_LOG.md` every few steps.
- If you exhaust the work, deepen tests / polish the preview / draft the report. Don't idle.

---

## 3 · HARD STOPS (never cross)
- **NOTHING GOES LIVE.** No deploy / scp / ssh / systemctl / nginx / Cloudflare purge; no writes to `178.104.73.239` or `trustsquare.co`; no `.env` / launch-flag changes; no DB migration run against the live server. Build **local + staged only.**
- **No git push, no merge to main.** Work on branch `build/simpler-model` (or stage under `_BUILD_STAGED\` with diffs if git is locked). Leave David a paste-ready PowerShell commit block; never commit/push yourself.
- **$0 in product terms — no live paid AI calls.** Build the AI features ($0-first) against **DEMO_MODE mocks / dry-run** by default. If a real model call is needed to validate, **do not spend** — log it to `AWAITING_DAVID.md` with the estimated cost. (David's rule: one real run per milestone, only after he okays the cost.)
- **Gated = build it on the branch, prove it, leave go-live to David.** Everything here is Gate 1 (EULA) and Gate 2 (pricing / tiers / Tuppence / ledger / payments) + §12 (Codex / pricing). Staged, never live. Gated does NOT mean stop.
- **Big-file rule:** never use editor/Write tools on `bea_main.py`, `marketsquare.html`, `marketsquare_admin.html`, `ms.js` — Python open/read → str.replace → write, then verify (`ast.parse` / `node --check` / HTML ends with `</html>`). Restore from git if truncated.
- **Never add any refund / reversal mechanism** (non-refundable is load-bearing). A HOLD "release on decline" frees an un-spent hold — not a refund.
- **Never edit the published `TrustSquare WhitePaper v2.docx`** — Addendum only.
- **Don't invent canon.** Where the doc leaves a dial open (see §6), implement a sensible default, log it in `AWAITING_DAVID.md`, and continue — never guess silently, never halt.
- **No secrets** printed or staged. **Don't delete** — supersede to `_ARCHIVE\`.

---

## 4 · What to build (each with acceptance criteria)
Work in this order; one piece fully (build + test + preview) before the next.

**A · Subscriptions: migrate 5-tier → 3-tier + free agency.**
- FEA PLANS page (`marketsquare.html` / `ms.js`) rebuilt to **Free / Starter / Pro / Agency** with the §1 numbers; slots-vs-Tuppence clarity (meter vs wallet); DEMO_MODE branch shows it without the live BEA.
- BEA (`bea_main.py`) tier config: names, slot caps 2/10/30, `TIER_TUPPENCE_MONTHLY` (Free PAYG / Starter 2T / Pro 10T), the **free verified Agency** tier (trust-graduated cap per §1), plan activation. (Leave a clean hook for the launch special, but do NOT hardcode a launch-month/tier rule — open decision, §1.) Staged DB migration mapping old tiers → new (don't run live; keep the 4 family superusers; set agencies free).
- Admin tier picker updated to the new tiers.
- *Done when:* the PLANS page renders the 4 rows correctly in a local DEMO_MODE preview; BEA unit logic for caps/allocations passes; migration script written + dry-run output shown (not executed live).

**B · AI features: free L1 glimpse + paid L2, capped 5T.**
- Implement the **Property Area Dossier** split (free Area Snapshot $0-first / paid Investor Dossier ~3T) end to end; then the **Car Dossier** split.
- Price ladder Free/2T/3T/5T across the AI entry points; remove 8T/10T and any "AI uses/sessions" remnants in code + copy.
- *Done when:* a buyer can see the free L1 glimpse and a 5T-capped paid L2 path in a DEMO_MODE preview (mocked outputs); no "uses/sessions" string remains; no live paid call was made.

**C · One-photo-one-sentence listing (the flagship — built in this run, not deferred).**
- New listing/onboarding flow: one photo + one sentence → drafted title/description/category/condition/suggested-price → seller fine-tunes → publish. $0-first pipeline; **DEMO_MODE mock** so the whole flow is previewable without live AI.
- *Done when:* David can walk the new flow locally end-to-end on mock data and see a drafted listing from one photo + one sentence.

**D · Canon / doc alignment (supporting — staged, not the main event).**
- Stage the Simpler-Model numbers into Codex v4.8 §11, the PLANS/EULA tier copy, support FAQ, AGENT_BRIEFINGs, `AdvertAgent_Pricing_Model.xlsx`, and pricing mentions in the email templates — as DRAFTs / staged edits, for David to land. (This is where a term-map sweep is a *tool*, not the goal.)

---

## 5 · MAKE IT VISIBLE (this is the point — David must SEE the rebuild)
Produce a **reviewable local preview** so David opens it and sees the new design without anything going live:
- The buyer app in **DEMO_MODE** showing the new PLANS page (4 tiers), the AI free/paid chips, and the one-photo onboarding flow.
- **Screenshots** of each in the build report (PLANS, an AI L1 glimpse + L2 paywall, the one-photo flow start→drafted listing).
- A one-paragraph "how to open the preview locally" note (which file to open / how to run in demo mode).

A staged build David can't see has failed the brief. The preview is the deliverable.

---

## 6 · Open design dials — implement a sensible default + log (don't block)
The Simpler Model doc lists these as still-to-define. Pick a sensible default, build it, and log the choice + your reasoning in `AWAITING_DAVID.md`:
1. **Free-L1 vs paid-L2 scope** per feature (what exactly the free glimpse shows vs the paid dossier).
2. **$0-first listing architecture** — which steps use the cheap vision pass / templates / public data vs a heavier model.
3. **Existing-user migration** mapping (old Standard/Pro/Business/Elite → new Free/Starter/Pro; agencies → free) — propose the mapping, stage it, don't run it live.

---

## 7 · Test + output
- `node --check` (JS) and `ast.parse` (Python) clean on every changed file; existing `smoke_test.py` logic not broken (run locally only — it's SSH-bound, so where it needs the server, note it, don't hit live).
- **Outputs (into `C:\Users\David\Projects\MarketSquare\`):** branch `build/simpler-model` or `_BUILD_STAGED\` with diffs · the DEMO_MODE preview + screenshots · staged canon/doc DRAFTs · `BUILD_REPORT_SIMPLER_MODEL.md` · `AWAITING_DAVID.md` · `PROGRESS_LOG.md`.
- **Build report (top):** what's built & previewable (with screenshots), what's staged for David's go-live, the open-dial decisions you made, test results, the branch/rollback point, the paste-ready PowerShell block (do NOT run), and a `Cost model impact:` line.

---

## 8 · Definition of done (today's envelope)
A · B · C built and **previewable in DEMO_MODE with screenshots**, D staged, tests clean, report written, decisions logged — **nothing deployed, pushed, merged, or charged.** David reviews the preview, lands canon/pricing, and ships.

*The spec is `MarketSquare_Simpler_Model_Options.docx` (Option A). When in doubt: the doc wins; build local, never live; make it visible.*
