# TrustSquare Change-Control Protocol (CCP)
**v1.0 · 10 June 2026 · David-approved** *(reusable — run every big cross-cutting change through it)*

The single source of truth for committing a **large change that ripples across many artifacts** — a
Codex rule, a pricing model, a business-process redefinition, a renamed concept. Its one job is to
make **"we forgot to update X somewhere"** impossible. It does this by replacing human recall with a
machine-checkable artifact: a **term map** that a grep drives to zero.

> **The guarantee, in one line:** we never ask *"did we remember every document?"* — we ask
> *"does the old wording still appear anywhere?"*, and that is a question a script answers to **zero**.

---

## 0 · Why this exists — the dropped-item problem
A big change fails not in the hard parts but in the *boring* parts: a stray old number in an email
template, an obsolete sentence in IP Brief v4, a tier name that survived in `ms.js` but nowhere else.
These are **recall failures**, and recall is exactly what humans (and unaided AI) are worst at across
60+ files in five repos plus a live server.

The fix is to make steps 2 and 3 **mechanical, not remembered**:
- **Step 2 produces a term map** — every old token → its replacement. This becomes the search key.
- **Step 3 greps that key across the entire tree** and emits a **traceability matrix** (change × artifact).
- **Step 5's Sensor re-runs the same grep** until it returns zero. A surviving old token is a tracked
  *finding*, not something a person has to notice.

Diligence is not the control. The **term map + grep-to-zero loop** is the control.

---

## 1 · When to invoke (materiality test)
Run the full CCP when a change is **YES to any** of:
- It changes a **word, rule, number, or name** that appears in more than ~3 artifacts, **or**
- It touches **canon** (Codex / PRINCIPLE_REQUIREMENTS / Addendum), **IP/patent lineage**, **pricing /
  Tuppence / tiers**, or a **legally-worded surface** (EULA / Privacy / public mechanism copy), **or**
- It redefines a **business process** (how a thing works), not just fixes a bug.

A one-file bug fix uses the normal session flow, **not** the CCP. (When unsure, run it — the cost is one
term map.)

---

## 2 · The nine steps (0 → 8)
Each step has an **output** and, where relevant, a **gate**. One step fully complete before the next.

| # | Step | Output (the artifact) | Gate |
|---|------|------------------------|------|
| **0** | **Freeze a baseline** | Git tag + a recorded snapshot of current versions of every canon/IP/cost file, so every later diff has an anchor and rollback is one command. One **CHANGE-ID** opened in `CHANGE_REGISTER.md` = the single source of truth for this change. | — |
| **1** | **Plan** | A short brief: the change in one paragraph, **definition-of-done**, and an explicit **abort/rollback criterion**. | David approves the brief |
| **2** | **List the changes → TERM MAP** | The old→new table: every word, rule, number, name, formula, endpoint, file-served-name that changes. This is the mechanical key for everything downstream. | David verifies the term map is complete & correct (he owns canon meaning) |
| **3** | **List affected artifacts → MATRIX** | Grep the term map across the **whole tree** + walk the **artifact-class checklist (§4)** → a **traceability matrix (§5)**: every change-item × every artifact that carries it. | — |
| **4** | **Implement** | The edits, worked **matrix cell by cell** — one artifact fully before the next. Big files (`bea_main.py`, the two HTMLs, `ms.js`) edited via the Python string-replace + verify discipline, **never** the Edit/Write tool. | Gate 1 / Gate 2 items **stage** for David (§7) |
| **5** | **AI dry-run test/fix loop** | The Sensor → Fixer → Orchestrator harness (§6) runs until **verified**. | "Verified" defined in §6 |
| **6** | **Human testing** | David tests the live/staging surfaces the matrix flagged (apps, emails, public pages, billing copy). | David sign-off |
| **7** | **Claude/David review + report** | A one-page closeout: what changed, **matrix coverage %**, residual risk, **cost-model impact**, the rollback point. | — |
| **8** | **Folder clean-up** | Superseded docs archived to `_ARCHIVE` (reversible); MEMORY + CHANGELOG/STATUS/BACKLOG/AUDIT_PROGRESS updated; one `scp` of the four parsed docs; **one** git push. | Session-end checklist (CLAUDE.md) |

---

## 3 · The term map — the mechanical key
Built in step 2, stored per change in `CHANGE_REGISTER.md` and the matrix's **Term Map** tab.

| Column | Meaning |
|---|---|
| `old` | The exact old token / phrase / number / formula (one row per distinct form, incl. variants & abbreviations) |
| `new` | Its replacement (or `DELETE` / `N/A`) |
| `kind` | word · rule · number · name · formula · endpoint · served-filename · concept |
| `search` | The literal/regex the Sensor greps for (e.g. `AI uses`, `\bsession(s)?\b` near "AI", `R?\s?12\b`) |
| `notes` | Disambiguation — false-positive traps, files where the old token legitimately survives (e.g. a published doc) |

**Rule:** if a token can appear in more than one written form (e.g. "AI uses", "AI-uses", "uses of AI"),
**every** form gets its own row. The grep is only as complete as the map.

---

## 4 · Artifact-class checklist (the anti-drop registry)
Step 3 does **not** list artifacts from memory. It walks **every class below** and greps each. A class is
only "clear" when grep returns zero (or the surviving hits are logged as legitimate in `notes`).

1. **Canon & governance** — `Solar_Council_Codex_v4_7.docx` (canonical) · `Canon_Addendum_*` · `PRINCIPLE_REQUIREMENTS.md` · the four `AGENT_BRIEFING.md` · `ORCHESTRATION_POLICY.md` · `AUTONOMY_LADDER.docx` · **all five `CLAUDE.md`** (root, MarketSquare, AdvertAgent, CityLauncher, Codices).
2. **IP / patent lineage** (`\Patents`) — `TrustSquare_IP_Brief_v5` (→ v6 if open) · `Patent_Strategy_v4` · `WhitePaper_v3_4` · Pre-Filing Consultation set · Claim Visuals. ⚠️ **`TrustSquare WhitePaper v2.docx` is PUBLISHED defensive disclosure — NEVER silently edit; supersede via Addendum** (see [[project_pricing_ai_canon]]).
3. **BEA code** — `bea_main.py` · `ai_service_tiers.py` · `payments.py` · `tier_resolvers.py` · `value_resolvers` · `auth.py` · `database.py` · `storage.py` · `feature_flags.py` · `launch_redemption.py` · `smoke_test.py` + the `test_*.py`.
4. **FEA / apps** — `marketsquare.html` (→ index.html) · `marketsquare_admin.html` (→ admin.html) · `ms.js` · `ms.css`.
5. **AdvertAgent** — `AI_FUNCTIONS_SPEC.md` · `AdvertAgent_AI_Functions_Spec_v1_1.docx` · `AdvertAgent_Pricing_Model.xlsx` · `AdvertAgent_AI_CostModel.xlsx` · `AdvertAgent_AI_Cost_Brief.docx` · `AdvertAgent_AI_Value_Benchmark.docx` · `AdvertAgent_HMI_Spec` · `service/`.
6. **Cost models (.xlsx)** — `Cost_Breakdown_GlobalLaunch.xlsx` (MarketSquare **and** the Codices copy) · the AdvertAgent xlsx pair · Codices cost variants. (Edited via openpyxl; remind David of the git commit per CLAUDE.md xlsx rule.)
7. **Email templates** — all 16 in `\n8n\email_templates` + the CityLauncher `emailer/templates/*.html` + n8n synced copies.
8. **Dashboards / ops pages** — `dashboard.html` · `orchestrator.html` · `citylauncher_ops.html` · `LAUNCH_READINESS_PLAN.html` · plus the server's `/dashboard/summary` parse of STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS.
9. **Session docs** — `STATUS.md` · `CHANGELOG.md` · `BACKLOG.md` · `AUDIT_PROGRESS.md` (per project).
10. **Server-deployed copies** — `/var/www/marketsquare/` (index/admin/main/static + the four parsed docs) · `marketsquare.service.d/launch.conf` · CityLauncher `.env`. **The server is its own artifact** — a change isn't done until the deployed copy matches.
11. **Memory** — the space `MEMORY.md` index + every relevant `project_*` / `feedback_*` file.
12. **Public-facing copy** — `trustsquare.co` homepage (Tuppence Wallet wording) + `/support` FAQ (mechanism + refund disclosure). These are externally visible and must not lag canon.

> Adding a class is cheap and permanent. If a change reveals a missed class, **add it here** so the next
> change inherits the fix.

---

## 5 · The traceability matrix — the 100% rule
One matrix per change (`TRACEABILITY_MATRIX_TEMPLATE.xlsx` → `MATRIX_<CHANGE-ID>.xlsx`).

Grid = **rows: every artifact** that grep/checklist flagged × **columns: every change-item** from the term
map, plus: `status` (pending / edited / verified / N/A), `owner`, `verified_by`, `verify_method`
(grep-zero / smoke / visual / David), `date`.

**The 100% rule:** the change is **not done** until **every cell is `verified` or an explicit `N/A` with a
reason.** A blank cell is a dropped item by definition. The matrix coverage % is reported in step 7.

---

## 6 · The AI dry-run harness (step 5) — Sensor → Fixer → Orchestrator
This **reuses the orchestration roles** ([[project_orchestration_v2]]) but in **ATTENDED change-mode**, not
the nightly hygiene loop. (The nightly loop, by ORCHESTRATION_POLICY §7, never touches canon/design — a
canon change is exactly what it must *not* auto-run; so here the same roles operate under full human gating.)

- **5a · Sensor (read-only, zero-token).** Re-greps **every term-map `search` across the whole tree** and
  cross-checks the matrix. Output: a findings list = (any surviving old token) + (any matrix cell not
  `verified`) + (`smoke_test.py` result) + (a Codex/served-copy drift check). Pure mechanical — no model.
- **5b · Fixer (attended).** Clears **one finding at a time**, surgically, with the big-file string-replace
  discipline + `ast.parse` / `node --check`. Because the targets are canon/pricing/IP, **every Fixer edit is
  treated as gated** (§7) — staged for David, never auto-shipped.
- **5c · Orchestrator (decides + reports).** Re-runs the Sensor; if any finding remains, re-queues the
  Fixer; loops. Writes the run report.

**Repeat 5a→5c until VERIFIED**, where **verified ≡ all three true at once:**
1. Sensor grep returns **zero** surviving old tokens (or all survivors logged legitimate),
2. matrix is **100%** (`verified` / explicit `N/A`),
3. `smoke_test.py` is **green** and the served copies match HEAD.

Only then does the Orchestrator declare **"fully implemented and verified"** and hand to step 6.

---

## 7 · Gates, rollback, and what stays human
The CCP **inherits** ORCHESTRATION_POLICY's two gates and never widens them:
- **Gate 1 — Regulatory:** EULA/Terms/Privacy/consent, company reg, **non-refundable / Tuppence validity**,
  KYC/anonymity-reveal. → **stage**.
- **Gate 2 — Financial:** `payments.py`, Paystack, the **Tuppence ledger**, **pricing/tiers/slots**, any
  release-of-funds path. → **stage**.
- **Never automated (POLICY §12), always David:** Codex amendments · WhitePaper lineage (supersede via
  Addendum, never edit) · pricing/tiers/Tuppence allocations · legal filings (CIPC, Paystack live, patents)
  · secrets/permissions.

Because most big changes are *made of* exactly these, the practical rule is: **the CCP is an attended track.
The AI harness finds and proves; David approves every canon/money/IP edit.**

**Rollback:** any step may abort to the step-0 tag with one command. An aborted change is a success of the
gate, not a failure.

---

## 8 · Definition of done + clean-up (step 8)
Done = **matrix 100% + Sensor zero + smoke green + David sign-off + report filed**, then:
- Archive superseded docs to `_ARCHIVE` (reversible; [[feedback_codices_retention]]).
- Update **MEMORY** (the change, and any new artifact class).
- Append to **CHANGELOG / STATUS / BACKLOG / AUDIT_PROGRESS** (with `Cost model impact:` if pricing/AI
  volume/concurrency moved).
- **One** `scp` of the four parsed docs (refreshes the live dashboard) + **one** git push (Orchestrator-owned).
- Close the CHANGE-ID in `CHANGE_REGISTER.md`.

---

## 9 · Roles
- **David** — owns the term map's meaning, approves the brief, signs off gates and human test. The only one
  who edits canon/money/IP (via Claude's hands, on his approval).
- **Claude (attended session)** — builds the term map draft, the matrix, does the implementation, runs the
  harness, writes the report.
- **The loop roles (Sensor/Fixer/Orchestrator)** — the *mechanical* engine of step 5; here they run attended
  and fully gated, never as the nightly auto-ship loop.

---

## Appendix · Per-change file set
For `CHANGE-ID = CC-NNN`:
- `CHANGE_REGISTER.md` → the ticket + term map (lives in MarketSquare).
- `MATRIX_CC-NNN.xlsx` → the traceability matrix (from the template).
- `REPORT_CC-NNN.md` / `.docx` → the step-7 closeout.
- Git tag `ccp/CC-NNN/baseline` at step 0.

*End of CCP v1.0. Amend here only for structural changes to the protocol; log routine use in
`CHANGE_REGISTER.md` and CHANGELOG.*
