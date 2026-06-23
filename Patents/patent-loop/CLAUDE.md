# CLAUDE.md — Self-Improving Patent + Whitepaper Convergence Loop

> **Scope:** This file governs ONLY the `Patents/patent-loop/` workspace. It does
> not override the MarketSquare project CLAUDE.md. When run, the agent operates
> exclusively inside `patent-loop/` and treats everything outside it as read-only
> reference.

## Mission
Run a continuous, multi-agent optimisation loop over two working documents —
`working/patent.md` (TrustSquare provisional specification) and
`working/whitepaper.md` (TrustSquare technical whitepaper) — to **maximise legal
defensibility, technical accuracy, and cross-document alignment** while
**minimising prior-art, compliance, and litigation risk**. Iterate until the loop
produces no change (Δ = 0), then promote both documents to a major-revision
baseline.

## Non-negotiable safety rails (read first — these override the loop)
1. **The `.docx` originals are FROZEN.** Never open, edit, or write
   `TrustSquare_Provisional_Specification_*.docx` or `TrustSquare_WhitePaper_*.docx`.
   The loop lives entirely on the `.md` working copies. Those docs are
   counsel-gated per `../../LEGAL_VERSIONS.md`.
2. **Never invent a citation.** Every prior-art reference, regulation, statute, or
   case must come from an actual web-search result the agent retrieved this run.
   No source → no claim. If a search returns nothing usable, record that and move
   on; do not fabricate a patent number, a case, or a section reference.
3. **Legal posture, not legal advice.** The agent improves drafting and flags risk.
   It is NOT counsel. Anything it cannot resolve from sources goes to the human as
   a flagged item, never silently "fixed" with a guess.
4. **This is a real SA/CIPC provisional, not a token/crypto project.** Tuppence is a
   **non-transferable platform credit (1T = USD $2)**, not a tradeable crypto
   asset. Apply securities/crypto checklists (Howey, MiCA) as *de-risking screens*
   to keep the language utility-only — NOT as an assumption that this is a
   crypto-asset offering. Over-correcting the docs into "crypto compliance"
   language is itself a defect; flag, don't impose.
5. **Whitepaper = the patent's Detailed Description by reference.** The spec's
   "Detailed Description" section explicitly incorporates Whitepaper v3.5. This
   makes the cross-document alignment check (Phase 2 §4) **existential**: a
   whitepaper claim the spec contradicts, or a spec claim the whitepaper doesn't
   enable, is a filing-killing defect, not a style nit.
6. **Edit `.md` via the file tools (Read→Edit/Write); never bash-write a large
   `.md`.** Per the parent project's mount rule, bash Python writes of large files
   on this mount can truncate. After every write, verify the file still ends on its
   real final line.

---

## Versioning model (matches the real docs)
The working copies carry a `version:` field in their YAML front-matter:
- `patent.md` starts at **6.0** (it is IP-Brief-v6-aligned spec).
- `whitepaper.md` starts at **3.5**.

- **Minor bump per loop iteration:** `6.0 → 6.1 → 6.2 …` and `3.5 → 3.6 …`.
  Both docs bump together each iteration, even if only one changed (keeps them
  lockstep, mirroring how they ship as a pair).
- **Major bump on convergence:** when the loop terminates at Δ = 0, promote to the
  next major: `patent 6.x → 7.0`, `whitepaper 3.x → 4.0`.
- Every save also appends a one-line entry to the doc's own revision-history table
  and writes a snapshot into `archive/<doc>.v<version>.md`.

---

## Phase 0 — Pre-flight (every run, before any iteration)
1. Confirm `working/patent.md` and `working/whitepaper.md` exist and end on their
   real final lines (tail check). If either looks truncated, STOP and report —
   do not proceed on a torn copy.
2. Read both fully into context. Build a **claim/assertion inventory**: list every
   independent + dependent claim in the patent, and every capability/metric/promise
   in the whitepaper. This inventory is the spine of the alignment check.
3. Initialise (or read) `audit/search_history.log` and
   `audit/loop_counter.txt`. The loop counter is N (start at 1).

---

## Phase 1 — Global Evidence Gathering & Maker Improvement (agent: MAKER)
The Maker runs **web searches**, synthesises findings, and revises both docs.

### 1A. Jurisdiction priority (TrustSquare-specific — NOT generic)
Primary filing jurisdiction is **South Africa / CIPC**. Search emphasis per
iteration, in this order of weight:
1. **South Africa** — CIPC provisional/complete practice; SA Patents Act 57 of
   1978; **CPA (Consumer Protection Act)** for the credit-expiry / dormancy /
   refund clauses; **POPIA** for data protection; **FAIS/NCA** only insofar as the
   Tuppence credit could be miscast as a financial product (screen, don't assume).
2. **WIPO / PCT** — because a PCT route off the SA provisional is the likely path;
   absolute-novelty exposure for the published Whitepaper v2 prior-art disclosure.
3. **US / USPTO + SEC** — §112 enablement/definiteness as a *drafting-quality*
   lens; Howey only as an anti-"investment-language" screen.
4. **EU / EPO + MiCA + EU AI Act** — EPO absolute-novelty; MiCA only as an
   anti-investment-language screen; AI Act tiering for the AI-triage / vision
   features (likely limited/GPAI, not high-risk — verify, don't assume).
5. **APAC — CNIPA / JPO** — secondary prior-art net only.

### 1B. Prior-Art Search Matrix (three classes, every iteration)
Extract the actual structural nouns, methods, and formulas from the current
`patent.md` / `whitepaper.md` to populate `[bracketed]` slots — never run generic
strings. Core TrustSquare nouns to draw from: *unified single-table participation
model; role-as-derived-state; commitment-gated / HOLD-settled introduction;
Tuppence value-unit metering; anonymous bilateral identity disclosure;
evidence-based trust signal-points; dual-use (human + AI) metering; existence-gate
on metered AI invocation; reverse-auction/lead framing (C10).*

**Class 1 — Patent-office syntax probes** (Google Patents, USPTO, EPO, WIPO):
- Structural-combination: `("commitment" OR "escrow" OR "hold") NEAR/5 ("introduction" OR "contact disclosure") AND marketplace`
- Functional-equivalence: `("anonymous seller" OR "identity reveal") AND ("system for" OR "method") AND NOT TrustSquare`
- Classification-boundary: query the relevant **CPC/IPC** classes
  (e.g. `G06Q 30/* ` commerce, `G06Q 50/*`, `H04L` for the disclosure-exchange) AND
  `[novel step]`.

**Class 2 — Academic / grey-literature crawls** (Google Scholar, arXiv, SSRN):
- Algorithmic-inversion: search the literal mechanism — `"role derived from listing count" OR "implicit role marketplace"`.
- Prior-art-by-another-name: translate legal → engineering — "commitment unit" →
  `"prepaid intro credit"`, "value-unit metering" → `"usage-metered platform credit"`.
- Dissertation/thesis probe for the trust-scoring and metering mechanisms.

**Class 3 — Adversarial open-source / market discovery** (GitHub, HN, forums):
- Repo code-hunt for the exact mechanisms (single-table role derivation,
  hold-settled credit ledger).
- "Failed attempt" forensic search — competitors who tried anonymous-intro
  marketplaces (e.g. Bark, Thumbtack, Pingsby) and the limitations they hit.
- Watch specifically for **Pingsby** (referenced in the spec's C3 as
  conditional/clearance-pending) — actively hunt its public disclosures.

### 1C. Maker revision rules
- Revise `patent.md` and `whitepaper.md` to (a) design around any real prior art
  found, (b) tighten enablement so every claim term is supported by whitepaper
  structure, (c) strip over-promises / investment-flavoured language, (d) fix any
  contradiction surfaced against sources.
- **Inline audit trail:** annotate every evidence-driven change with a hidden
  markdown comment naming the source, e.g.
  `<!-- prior-art design-around: see US20XX/XXXXXX (Google Patents, retrieved 2026-06-23) -->`.
- **Save to `staging/`** (not `working/`) — staging is what the Auditor sees.

### 1D. Anti-duplication gate
- Log every executed query to `audit/search_history.log` with the loop number.
- In loop N+1, **no query string from loop N may be reused** — rotate keywords,
  synonyms, or jurisdiction. If you've exhausted a jurisdiction's obvious angles,
  pivot to the next in the 1A priority list.

---

## Phase 2 — Doctorate Auditing Persona (agent: AUDITOR — adversarial, clean context)
Fork a **fresh sub-agent** that sees ONLY the raw text of `staging/patent.md` and
`staging/whitepaper.md` — no Phase-1 chain-of-thought, no search logs. Persona: a
ruthless senior IP attorney + technical examiner whose job is to **invalidate**.
It tries to kill the patent using the whitepaper, and discredit the whitepaper
using the patent.

Run the full checklist; output `audit/audit_feedback.json` (schema below).

### 1. Patentability & Prior-Art Cleansing (SA Act 57/1978, WIPO/PCT, USPTO, EPO)
- **Whitepaper-induced self-anticipation:** the published **Whitepaper v2** is an
  intentional prior-art defensive publication. Verify nothing in the current
  whitepaper/patent newly anticipates a claim in a way that breaks **absolute
  novelty** for the PCT/EPO route. SA/US grace periods do NOT save an EPO/PCT
  filing — flag any claim whose enabling disclosure predates the provisional.
- **Enablement & definiteness:** every patent claim term must be enabled by
  whitepaper engineering description. Flag vague adjectives, functional language
  with no structural backing, hand-wavy math. (Lens: SA sufficiency + US §112.)
- **Inventive step / non-obviousness:** hunt "combination of references." Force the
  docs to articulate the **non-obvious technical synergy** of the unified-model +
  hold-settled-metering + trust-points combination.

### 2. Consumer, Data & Financial Compliance (SA-first)
- **CPA (SA) — credit expiry/refund:** the spec already flags an internal
  inconsistency (EULA §5.3 "no expiry" vs §6.3 "24 months") and a staged CPA-s63
  extension to ≥36 months. Verify the docs describe Tuppence credit validity and
  **non-refundability** in a CPA-survivable way. This is the single most concrete
  live legal risk — audit it hard.
- **POPIA / GDPR (Privacy-by-Design):** anonymous-introduction means PII handling
  is core. Verify both docs state where data lives, how bilateral disclosure is
  consented/logged, and that no un-minimised PII is exposed pre-commitment.
- **Investment-language screen (Howey / MiCA) — de-risk only:** flag any "yield,"
  "returns," "profit," "appreciation," "burn-to-drive-value" phrasing and force it
  to utility language ("platform credit consumed for a service rendered"). Do NOT
  add crypto-asset disclosures — Tuppence is non-transferable credit. Over-adding
  MiCA scaffolding is itself a flaggable defect.

### 3. AI / Automated-Systems (EU AI Act + general)
- The platform uses AI inbound-triage and batched vision. Verify the docs describe
  human-oversight / guardrail loops and the existence-gate on metered AI. Classify
  tier (likely limited-risk / GPAI) **from the text** and flag if the docs
  over- or under-state capability.

### 4. Cross-Document Divergence — THE ALIGNMENT TEST (existential here)
Because the whitepaper IS the patent's incorporated Detailed Description:
- **"Lying to the patent office" trap:** no patent claim may assert a capability the
  whitepaper contradicts, marks "future work," or admits is unbuilt. Check each
  claim in the Phase-0 inventory against whitepaper status language
  (e.g. C3 Pingsby "CONDITIONAL," HOLD-model "spec-staged" vs "live").
- **"Overselling to investors" trap:** no whitepaper metric/feature may exceed what
  the patent's independent claims actually support or what production code delivers
  (the docs themselves cite "BEA v1.3.x production" and a ground-truth audit —
  honour that).
- **Live-vs-staged consistency:** the docs distinguish *implemented* (AI metering,
  trust signal-points) from *spec-staged* (Tuppence HOLD intro side, C10–C13).
  Flag any place that blurs the two.

### Auditor output — `audit/audit_feedback.json`
```json
{
  "loop": <N>,
  "verdict": "CHANGES_REQUIRED | CLEAN",
  "violations": [
    {
      "id": "AUD-<N>-001",
      "category": "prior-art | enablement | inventive-step | CPA | POPIA | investment-language | AI-Act | alignment",
      "severity": "blocker | major | minor",
      "doc": "patent | whitepaper | both",
      "location": "<section / claim id>",
      "finding": "<what is wrong>",
      "corrective_action": "<explicit, do-this instruction for the Maker>",
      "source": "<URL/citation if the finding rests on external evidence, else 'internal-consistency'>"
    }
  ],
  "alignment_conflicts": [ "<claim X vs whitepaper §Y>" ],
  "unresolved_for_human": [ "<items the agent must NOT auto-fix — counsel calls>" ]
}
```
The Auditor must list every actionable defect. An empty `violations` array AND an
empty `alignment_conflicts` array is the only "CLEAN" verdict.

---

## Phase 3 — Version Control & Gatekeeper (agent: GATEKEEPER)
### 3A. Apply feedback (Maker)
- Read `audit/audit_feedback.json`. Implement **every** `corrective_action` whose
  severity is `blocker` or `major`, and every `minor` that doesn't require a human
  call. Items in `unresolved_for_human` are NOT auto-applied — they are collected
  for the final report and the loop continues without them.
- Bump both docs **one minor** version; append a revision-history line to each;
  write `working/` copies (promote staging → working) and snapshot to `archive/`.

### 3B. Convergence Gatekeeper criteria
Compute Δ between the new `working/` docs and the previous iteration's `archive/`
snapshot.
- **Δ is NON-ZERO (→ loop again, return to Phase 1)** if ANY of:
  - the Auditor verdict was `CHANGES_REQUIRED` (any blocker/major/minor remained),
  - applying fixes changed claim text, technical spec, or a material metric,
  - Phase-1 search surfaced new conflicting evidence this round.
  - On re-loop, the Maker MUST use fresh search criteria (Phase 1D) and SHOULD
    rotate to the next jurisdiction in the 1A priority list.
- **Δ = ZERO (→ terminate)** only when a *complete* cycle yields: Auditor verdict
  `CLEAN`, no text changes applied, and no new conflicting evidence. (Items parked
  in `unresolved_for_human` do not block termination — they are reported, not
  auto-resolved.)
- **Safety stop:** if the loop reaches **8 iterations** without Δ = 0, halt and
  report non-convergence with the outstanding `violations` — do not spin forever.

---

## Phase 4 — Finalisation & Major Baseline
When Δ = 0:
1. Promote `working/patent.md` → major **7.0**; `working/whitepaper.md` → major
   **4.0**. Update front-matter `version:` and append a "MAJOR BASELINE" line to
   each revision-history table.
2. Snapshot both to `archive/patent.v7.0.md` and `archive/whitepaper.v4.0.md`.
3. Write `audit/audit_trail.md`: jurisdictions checked, total loops, every search
   query (from `search_history.log`), count of violations fixed per category, and
   the full `unresolved_for_human` list as a **counsel hand-off checklist**.
4. Regenerate clean `.docx` deliverables from the v7.0 / v4.0 markdown into
   `staging/` (using the project's docx skill), named
   `TrustSquare_Provisional_Specification_v7.0_AUTO.docx` and
   `TrustSquare_WhitePaper_v4.0_AUTO.docx`. **Stamp each first page:
   "AUTO-CONVERGED DRAFT — NOT COUNSEL-APPROVED. The frozen counsel-gated .docx
   remains authoritative until counsel sign-off."** (Honours LEGAL_VERSIONS.md —
   the loop produces a candidate, counsel still gates the real filing.)
5. Emit the terminal notice:
   `[SYSTEM STATUS: CONVERGED. MAJOR BASELINE patent v7.0 / whitepaper v4.0 SAVED — AUTO, PENDING COUNSEL.]`

---

## Operating principles (inherited + loop-specific)
- **No floating "later"s.** Every unresolved-for-human item lands in
  `audit/audit_trail.md` as a dated checklist line — nowhere else.
- **Source grounding is mandatory** (rail #2). An un-sourced "fix" is a defect.
- **Flat status only:** report done / not done / looped N times / converged /
  non-converged. No optimistic "it's now bulletproof" spin — these are legal drafts
  pending counsel.
- **One change class per Maker pass** where practical; never sweep-rewrite a whole
  doc when a targeted fix answers the finding.
