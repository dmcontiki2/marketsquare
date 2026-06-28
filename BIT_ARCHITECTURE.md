# TrustSquare BIT (Built-In Test) Architecture

**Status:** design + first working slice (this session, 27 Jun 2026)
**Author of record:** David + Claude. Supersedes the shelved ChatGPT-era BIT notes — clean slate, baselined against the live app.
**Why now:** the heartbeat monitor checks only *did a scheduled task fire*. It cannot see a feature that fires and returns an error. Yesterday's "Feature examples broken" (the `See an example (free)` buttons) is invisible to it. BIT closes that gap.

---

## 0. Vocabulary (so PASS/FAIL never lie to us)

A BIT is a single assertion about the *running* system that returns one of four states. The two failure-shaped traps are first-class, not afterthoughts:

| State | Meaning | What it must trigger |
|---|---|---|
| **PASS** | Marker healthy. | Nothing (quiet-when-healthy). |
| **FAIL** | Marker broken. | Severity ladder (§4). |
| **FALSE-POSITIVE PASS** | BIT said PASS but the thing is actually broken. The dangerous one — a blind spot we trust. | Negative BITs (§2) + canary expectations + coverage audit. |
| **FALSE-NEGATIVE FAIL** | BIT said FAIL but the thing is actually fine (flaky network, cold cache, rate-limit jitter). | Confirm-before-alert: N-of-M re-runs, grace windows, dependency suppression (§3). A monitor that cries wolf gets ignored — which re-creates the blind spot. |

**Functional BIT** — asserts a *positive* contract: "this should work, prove it does." (`/health` returns ok; `/ai/example/<id>` returns a sample report.)

**Negative BIT** — asserts a *failure* contract: "this should be rejected/blocked/absent, prove it is." Negative BITs are how we catch false-positive PASSes, because they fail loudly when a safety boundary silently dissolves. (Bad API key must 401 — if it 200s, auth is open. Demo listings must NOT appear in live grids — if they do, demo-bleed is back. An unfunded paid op must be refused, not delivered for free.)

The design principle: **functional BITs prove features work; negative BITs prove the guardrails that make a PASS trustworthy are still standing.** You need both or your green board is a lie.

---

## 0.5 The BIT-budget constraint — the agent is a SEPARATE, minimal article (David, 27 Jun 2026)

**Hardware BIT rule carried over:** in a circuit-board design the self-test circuitry must not exceed ~5% of the total BOM component count (or the customer-set figure). Past that, the *added* parts raise the board's own failure rate — the test hardware degrades the MTBF/MTTF of the very article it certifies. The monitor must never become a material contributor to the failure rate of the monitored.

**Software equivalent, made a hard requirement:**
1. **Out-of-process & out-of-repo-runtime.** The BIT Agent is a **separate, minimalist article**, NOT code inside `bea_main.py`. It must not share the BEA's process, deploy, DB connection, dependency tree, or fate. A bug in the BIT can then never crash, corrupt, or block TrustSquare — it can only mis-report, which the §3 false-negative discipline already contains.
2. **Independence (the watcher must outlive the watched).** A monitor that dies *with* the system cannot tell you the system died. The BIT runs on its own footing and reaches TrustSquare only over the network (read-only HTTP), so BEA-down is observable, not co-fatal. Ideally it runs on a *different* host/process than the BEA so a box-level fault is still reported.
3. **Minimal footprint, measured like a BOM budget.** The BIT's own complexity is bounded and tracked:
   - **Size budget: BIT LOC <= 5% of TrustSquare core LOC** (`bea_main.py` + `ms.js`). Tracked each session.
   - **Dependency budget: zero third-party libraries** — Python stdlib only. Every dependency the BIT adds is new failure surface that counts against it. (The slice meets this.)
   - **Coupling budget: read-only network calls only.** The BIT imports no TrustSquare code and never writes to its DB. Acting on failures is done via the existing Detect→Triage channel and reversible flag-flips, not by reaching into the BEA.
4. **Current measurement (27 Jun 2026):** BIT = **185 LOC = 0.73%** of the 25,177-LOC core, **0 third-party deps**, coupling = 7 read-only GET paths. **Well inside the 5% budget.** If the BIT ever approaches the budget, that is a signal to prune BITs or split tiers — not to grow it inside TrustSquare.

**Consequence for placement (revises §7):** the continuous BIT Agent does NOT live inside the BEA. It is its own article — `bit/` here for source, deployed as an independent `systemd` unit (own venv-free Python, own user) ideally on a separate host or at minimum a separate process. The only piece allowed to touch TrustSquare's own runtime is the **deploy-gate BIT**, which runs as an external pre/post-deploy step in `deploy_marketsquare.bat` (a script that already exists and already runs outside the BEA), never as imported BEA code.

---

## 1. Baseline — what TrustSquare actually is (the surface under test)

Captured live, 27 Jun 2026, from `bea_main.py` (~9,970 lines, ~130 endpoints), `ms.js`, the SQLite schema, and the complaints subsystem.

### 1.1 FEA (Front-End App) — `marketsquare.html` + `ms.css` + `ms.js`
- Static shell (~325 KB) served by the BEA; logic in external `ms.js`, data via `/demo-listings`, `/wonders`, `/listings`.
- **AI feature panel** (`AI_FNS`, `AI_SEL`): each feature has `id`, `name`, `price_t` (Tuppence), `params`, `accepts_photos`, a free **dry-run preview**, and a **free worked example** button (`aiExample()` → `GET /ai/example/<id>`).
- Demo-bleed guards live in JS (`!DEMO_MODE && id.startsWith('demo_')`).

### 1.2 BEA (Back-End App) — Flask, ~130 routes. The high-value clusters:
- **Core data:** `/health`, `/listings`, `/demo-listings`, `/demo-sellers`, `/wonders`, geo (`/countries`,`/regions`,`/cities`,`/suburbs`).
- **AI ops (paid, Tuppence-metered, deliver-then-charge):** `/vision-draft`, `/ai-rewrite`, `/ai-audit`, `/value-tiers`, `/price-check`, `/yield-calc`, `/batch-cards`, `/coach`, `/market-note`, `/draft-from-photos`. **The free `/ai/example/<id>` previews — CURRENTLY MISSING/ERRORING (see §6).**
- **Money path:** `/buy-pack`, `/balance`, `/ai-commit` → `/ai-settle` (hold-then-settle), `/buyer-token`, Paystack `/initialize`/`/verify`/`/webhook`.
- **Trust + safety:** `/trust`, `/complaint`, `/complaints` (two systems: `lm_complaints` = buyer no-shows; `seller_complaints` = diminishing-scale seller penalties), `/credential`, `/verify-identity`, `/declare`, EULA `/accept`.
- **Ops/admin:** `/dashboard/summary`, `/admin/email-triage`, `/flags`, `/ai-spend`, `/cost`, `/scan`, `/grading-review`.
- **Email triage:** `/email/inbound` → Haiku classify → draft/auto-send gate.

### 1.3 dBase (SQLite, WAL): 23 tables.
Trust-critical: `lm_complaints`, `seller_complaints`, `lm_suspensions`, `buyer_trust`, `user_credentials`, `user_declarations`, `seller_documents`. Money/AI: `ai_spend_log`, `ai_spend_config`, `email_triage`. Catalog: `listing_versions`, `listing_cities`, geo_*, `wonders` (via JSON+endpoint), wishlist_*.

### 1.4 Customer complaints (an input channel, not just a table)
- Inbound mail → `/email/inbound` → classified (support/billing/legal/compliance/spam). **A spike in a complaint category is itself a BIT signal** — the customer is the test oracle of last resort.
- On-platform: `/complaint` (buyer no-show), seller complaints feeding trust-score penalties.

---

## 2. The BIT catalogue (baseline set — versioned in `bit_registry.json`)

Each BIT = `{id, layer, type, severity, assert, expect, confirm, mitigation, owner}`. Starter set grounded in the baseline:

### FEA / contract BITs
- **B-FEA-EXAMPLE** (functional, S2): every advertised AI feature id resolves `/ai/example/<id>` to a non-error sample. *This is yesterday's failure.*
- **B-FEA-SHELL** (functional, S2): HTML shell 100–600 KB, ends `</html>`, links external ms.js/ms.css with immutable cache.
- **B-FEA-CONTRACT** (negative, S2): every feature id the FEA advertises has a live BEA route. A UI button with no backend = contract breach.

### BEA / functional BITs
- **B-BEA-HEALTH** (functional, S1): `/health` → `{status:"ok"}`.
- **B-BEA-DATA** (functional, S2): `/demo-listings` ≥200, `/wonders` ≥100 sites, `/listings` live count ≥1.
- **B-BEA-AI-DRY** (functional, S2): each AI op dry-run/preview returns a shaped sample at $0 (no token burn).

### BEA / negative BITs (guard the PASS)
- **B-NEG-AUTH** (negative, S1): bad/empty API key → 401, never 200. Admin routes refuse unauth.
- **B-NEG-DEMOBLEED** (negative, S2): `/listings` live set contains zero `demo_*` ids.
- **B-NEG-DELIVER-CHARGE** (negative, S1): an AI op with no verified result must NOT deduct Tuppence (deliver-then-charge integrity). A `cannot_verify` path returns free.
- **B-NEG-COST-CEILING** (negative, S1): a request over the per-user/platform token ceiling is *refused*, not just logged.

### dBase BITs
- **B-DB-WAL** (functional, S2): WAL + synchronous=NORMAL on; DB writable on a probe row (rolled back).
- **B-DB-COMPLAINT-INTEGRITY** (negative, S2): a seller below the trust floor with **zero** complaints is NOT auto-suspended (the LM-14a bootstrap rule) — proves the penalty engine isn't over-firing.

### Complaint-channel BITs (oracle of last resort)
- **B-CC-SPIKE** (functional/anomaly, S3→S2 on threshold): rate of `support`/`billing`/`legal` complaints over a rolling window vs baseline; a spike escalates severity.
- **B-CC-SLA** (functional, S3): no complaint sits unactioned past its SLA window.

> The catalogue is *append-only and versioned*. Every real incident should add at least one new BIT (preferably a negative one) so the same failure can never return silently — this is the "prevent" step of §4 made concrete.

---

## 3. False-negative discipline (don't cry wolf)

A FAIL is **provisional** until confirmed. Before any FAIL escalates:
1. **N-of-M confirm:** re-run the BIT (e.g. 2 of 3 within 90s) — flaky network/cold cache clears.
2. **Grace window:** transient-class BITs get a hold-down (mirrors the heartbeat's 90-min cron grace).
3. **Dependency suppression:** if `/health` (S1) is down, suppress the 40 downstream BITs that depend on it — report the *root*, not 40 symptoms. (Borrowed from the strategist's checkpoint model.)
4. **Canary expectations:** negative BITs carry a known-bad input whose FAIL is *expected*; if that canary ever PASSes, the BIT itself is broken (catches false-positive PASS in the harness).

Only a *confirmed* FAIL enters the severity ladder.

---

## 4. Severity ladder + the four-phase recovery process

Each BIT carries a severity. Severity decides *who hears about it, how fast, and whether auto-fix is allowed.*

| Sev | Definition | Example BIT | Auto-fix? | Human report |
|---|---|---|---|---|
| **S1 — Critical** | Money, auth, or whole-site down. Users harmed or exposed *now*. | B-BEA-HEALTH, B-NEG-AUTH, B-NEG-DELIVER-CHARGE, B-NEG-COST-CEILING | **No auto-fix.** Auto-*mitigate* only (flag-flip to safe state). Immediate human page. | Instant email + dashboard red + (future) push. |
| **S2 — Major** | A feature is broken or a guardrail is down, but money/auth intact. | B-FEA-EXAMPLE, B-FEA-CONTRACT, B-NEG-DEMOBLEED | **Conditional** (see §5). | Email within the cycle; dashboard amber. |
| **S3 — Minor** | Degraded/slow/anomaly; not user-blocking yet. | B-CC-SPIKE, B-CC-SLA, latency drift | Auto-fix allowed if reversible. | Rolled into the daily brief; dashboard yellow. |
| **S4 — Info** | Cosmetic/observational; trend only. | coverage gaps, drift counters | Auto-fix freely. | Weekly digest only. |

**The four-phase process every confirmed FAIL runs (concurrent, not sequential where possible):**

1. **REPORT** — emit a Detect-schema finding (so it feeds the existing Triage→Fix loop via `prevent.py`) + notify per severity. Reporting happens first and always, even when an auto-fix is about to run, so a human is never surprised.
2. **MITIGATE (short-term, fast)** — bring the system to a *safe* state without fixing root cause. Always a flag-flip or graceful-degrade, never a code change: turn the broken feature off (hide the button / return an honest "temporarily unavailable"), fail closed on auth, freeze the metering path. Mitigation must be reversible and must itself be BIT-checked.
3. **RESOLVE (root cause)** — for S3/S4 and *conditionally* S2 (§5), the agent applies a real fix following David's mount/verify discipline (bash-python str-replace + py_compile + smoke), then re-runs the BIT to confirm green. S1 resolution is human-led; the agent prepares the diff but does not ship.
4. **PREVENT** — add/strengthen a BIT (preferably negative) that would have caught this earlier, record it in the registry + CHANGELOG, and — if the failure was a contract gap — add the missing contract test to the deploy gate so it can't reship.

---

## 5. Auto-fix gating — when is the agent allowed to change code itself?

Auto-fix is powerful and dangerous; it is gated by a **hard allow-list**, not a judgement call:

**Auto-fix ALLOWED (agent ships the fix, then re-BITs) only if ALL hold:**
- Severity ≤ S2 **and** the fix is on the pre-declared reversible allow-list: flag flips, cache purge, asset re-deploy of byte-identical content, restart of a wedged service, re-seeding demo data, re-pointing a known-good config.
- A backup exists (`cp f f.bak-<ts>`) and the change passes `py_compile`/smoke **before** it goes live.
- The post-fix BIT re-run is GREEN and no *other* BIT regressed.

**Auto-MITIGATE-only (no code change, agent flips to safe state, human resolves):**
- Anything S1 (money/auth/site-down).
- Any fix touching `bea_main.py` business logic, the metering/Tuppence path, auth, or the DB schema.
- Any fix not on the allow-list.

**Human-only, agent prepares but does not act:**
- Deploys of new logic, spend, deletes, sending mail on David's behalf, the live cron `--live` flips.

> Rule of thumb, straight from CLAUDE.md: reversible → the agent just does it; irreversible/consequential → mitigate + report + hand David the prepared diff. Cheap-wrong beats expensive-vague, but never on the money or auth path.

---

## 6. First true positive (proof the design earns its keep)

Baseline run found the live failure unaided: **the FEA advertises `/ai/example/<id>` for every AI feature, but the BEA has no `/ai/example/` route** (every other AI op — `/ai-rewrite`, `/price-check`, `/value-tiers`, `/yield-calc` … — is a real route; the example endpoint is absent). So `aiExample()`'s `fetch` is not `r.ok` → the catch fires → "No example available." That is a **contract breach** caught by **B-FEA-CONTRACT** (negative) and **B-FEA-EXAMPLE** (functional) simultaneously — exactly the class the heartbeat is blind to. Today's fix (implement/mount the route) becomes the **PREVENT** step: B-FEA-CONTRACT goes into the deploy gate so a UI-button-without-a-route can never reship.

---

## 6.5 The FIX process — what happens when a BIT fails (four actors, three already built)

The schema must not just *detect*; it must *act*. The best solution is NOT a new monolithic fix-bot — it is a pipeline of four roles separated by capability, so the tiny read-only watcher never holds deploy power. Three of the four already exist in `orchestration_v2/`.

**Actor 1 — BIT Agent (detect + confirm).** On a confirmed FAIL it writes a Detect-schema finding (`findings_bit.json`, identical shape to `prevent.py`'s `findings_prevent.json`) and stops. It never fixes. (`bit_runner.py` + `emit_findings_file()`.)

**Actor 2 — Mitigator (fast, reversible, automatic) — the one genuinely new piece.** The existing Fix loop is *daily* — far too slow for an S1 erroring at users right now. The Mitigator runs in seconds and does **no code change ever**: it only flips pre-declared flags to a safe state (hide the broken feature / honest "temporarily unavailable", fail-closed auth, freeze the Tuppence burn, purge stale cache). Allow-list only; anything not on it escalates to a human. Every action is reversible (prior value recorded). This is the "speedy recovery + short-term mitigation" requirement. (`bit_mitigator.py`.)

**Actor 3 — Fix Orchestrator (resolve, gated) — already built.** `detect_verify.py → triage.py → fix.py → orchestrator_v2.py`. Triage lanes every finding **green / amber / red**. `fix.py` ships **only green** under verify-or-revert; **amber stays staged, red is never auto-consumed.** That IS the "auto-fix if possible, human if not" rule, already enforced in code. The real edit is a Sonnet checkpoint applied with David's bash-python str-replace + ast + smoke discipline. The `/fix` skill (`autofix:fix`) is the heavier interactive resolver for a recurring fault.

**Actor 4 — Preventer (close the loop) — already built (`prevent.py`).** After resolution, add a regression guard so the defect re-flags instantly if it returns, and push the contract test into the deploy gate.

**Auto-fix decision (the crux), already gated by severity + allow-list — never judgement:**
- Reversible flag/asset fix, severity ≤ S2 → Mitigator may flip immediately; Fix loop ships the green resolution then re-BITs.
- Touches money / auth / DB schema / BEA logic → amber or red → mitigate + prepare the diff + hand to David. 
- S1 → Mitigator buys time; resolution is human-led.

**End-to-end on yesterday's failure:** BIT confirms `/ai/example` 404 (S2) → Mitigator flips `ai_example_enabled:=false` so the button shows "temporarily unavailable" instead of erroring (seconds, reversible) → finding lands in Triage as amber (it needs a real new route, not a flag) → David/Fix loop implements the route under verify-or-revert → Preventer adds B-FEA-CONTRACT to the deploy gate so a UI-button-without-a-route can never reship. Report happens first and throughout.

## 7. How it runs — the concurrent BIT Agent (recommendation)

David asked which way is best. Recommended shape — **three tiers, one registry, increasing cost/coverage:**

1. **Deploy-gate BIT (synchronous, blocking):** the functional + negative BITs that are cheap and contract-shaped run inside `smoke_test.py`'s successor at every deploy. A broken example/contract **blocks the deploy**. Zero new infrastructure — extends what exists.
2. **Continuous BIT Agent (the concurrent cycler David specified):** a long-lived loop on the Hetzner box (a `systemd` service beside the BEA, mirroring `citylauncher-strategist.service`) that cycles the registry on a cadence per severity — S1 markers every ~60s, S2 every ~5 min, S3/S4 every cycle of minutes/hourly. It is **observe-and-act, never spend**: pure-Python fast path for routine ticks, severity-gated auto-mitigate/auto-fix per §5, emits Detect findings into the existing Triage→Fix loop, writes state to a `bit_state` table, and pushes status to the **+1 Dashboard Page 1 "Live Health"** (LAUNCH-CONTROL-1, already specced). Quiet-when-healthy; emails David only on confirmed S1/S2.
3. **Daily brief:** one consolidated health line in the morning brief (S3/S4 rollup + overnight S1/S2 history), so even a perfectly quiet night leaves a visible "all green" trail.

This reuses four things you already have — `smoke_test.py` (gate), `prevent.py`/Detect-schema (loop intake), the strategist `systemd` pattern (the concurrent service), and the +1 Dashboard (human surface) — so the only genuinely new artifact is the registry + runner, which is the working slice built this session.

---

## 8. Build status (this session)
- ✅ Baseline captured from the live app (this doc, §1).
- ✅ `bit_runner.py` + `bit_registry.json` — working harness, functional + negative BITs, severity-tagged, quiet-when-healthy, N-of-M confirm. Catches the `/ai/example` failure as a true-positive S2.
- ▢ Deploy-gate merge into the smoke test — next.
- ▢ `systemd` BIT Agent service + `bit_state` table + dashboard panel — next, after David okays the shape in §7.
- ▢ Fix the actual `/ai/example` route (the feature fix) — David flagged this as today's work; BIT now makes its done-ness checkable.
