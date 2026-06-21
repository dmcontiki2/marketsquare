# TrustSquare — Remediation & Prevention Plan
**21 June 2026 · companion to the Documentation Audit of the same date**

Responds to two approved actions: **(1) implement the remediation** (Part A); **(2) prevention actions for review** (Part B).

- **Action 1:** the safe, reversible, agent-owned step (A0) is **DONE** this session. The rest is gated on you + counsel + a money-lane production deploy, so per your "Approvals & blockers" rule it is **parked with owners + exact steps**, not landed unilaterally.
- **Action 2:** Part B is a candidate list — **nothing implemented**, for our review.

## The one move that clears most of the audit
**Land CC-001 → CC-002, then promote Codex v4.8 to canon (A1–A3).** Resolves all of List-2's pricing/HOLD/AI staleness; it's the prerequisite the docs themselves name. Needs your term-map verification + counsel sign-off — which is why it's yours to trigger.

---

## Part A — Remediation Execution Plan

| Step | Action | Owner | Reversibility | Status | Clears |
|------|--------|-------|---------------|--------|--------|
| **A0** | **Refresh the two CLAUDE.md files** — MarketSquare: Codex pointer v4_5→v4_7/v4_8; stale live-state→STATUS/dashboard pointers (F3)+CPX32; premium→pro; dead session path→placeholder. Codices: versioned filenames→canonical (C1), v4_1→current, obsolete status→pointer. | Agent | Reversible (git) | **✅ DONE NOW** | L1-05/06/11/12/13 |
| A1 | **Land CC-001 (Tuppence HOLD)** — (1) you verify term map (Step-2 gate; MATRIX_CC-001.xlsx/AWAITING_DAVID.md); (2) counsel sign-off EULA v1.7 + IP Brief v6 (must land together, Codex §12); (3) deploy staged bea_main.py intro-HOLD from PowerShell; (4) land Codex v4.8 §2/§12. **One-way door.** | David + counsel | IRREVERSIBLE | ⏳ PARKED | L2-12 (intro) |
| A2 | **Land CC-002 (pricing + AI canon)** — after A1 (it sets the charge mechanism CC-002 refers to). Steps in REPORT_CC-002.md. | David | IRREVERSIBLE | ⏳ PARKED | L2-01/02/05 |
| A3 | **Promote Codex v4.8 → canon + refresh stale ops sections** (§1 cities/categories, §4 file-table + Alpha checklist, §5 endpoints + table count, §6 infra/cost, §9 agenda, §10a WH count, §10 history). I can execute on your go (draft → reversible). | Agent (on your go) | Reversible (draft) | ⏳ PARKED | L2-03/04/06/08/09/10/11/13/14 |
| A4 | **Finish CC-003 propagation** — sweep "60 sellers = public launch" from all requirements copies + Codex §1/§2-KPI (exact lines in CHANGE_REGISTER §CC-003). Your ruling already made. I can execute on your go. | Agent (on your go) | Reversible | ⏳ PARKED | L1-10, L2-07 |
| A5 | **Converge requirements to one source + generated mirrors** — after A3: regenerate ONE canonical file from landed canon; replace the 5 copies; delete 2 archived dupes; fix v1.3 internal (footer 1.2→1.3, C5 pointer, briefing cite). | Agent (after A3) | Reversible | ⏳ PARKED | L1-01/02/03/04/14 |
| A6 | **Pin one EULA version + land Session-77 AI-price clause** — resolve v1.1/v1.6/v1.7 spread; land the "[COUNSEL REQUIRED]" clause. | Counsel | Legal | ⏳ PARKED | L1-09 |

**Done this session (A0):** `MarketSquare/CLAUDE.md` + `Codices/CLAUDE.md` refreshed. Reversible via git (commit block below).

---

## Part B — Prevention Actions (for review — nothing implemented)

Root causes: **RC1** CC packages staged-not-landed · **RC2** partial propagation of decisions · **RC3** no enforced single-source/propagation · **RC4** hand-maintained status ages silently.

| ID | Prevention action | Stops recurring (root cause · findings) | Effort | Owner | Rec |
|----|-------------------|------------------------------------------|--------|-------|-----|
| **P1** | **One canonical requirements file + generated mirrors** (copies become build-time generated/symlinked, can't diverge) | RC3 · L1-01/03/04 | Medium | Agent | Adopt |
| **P2** | **Canon-pointer check** (extend `check_pricing_canon.py` → assert every doc's Codex/briefing/tier/threshold pointers match live canon/STATUS; drift fails a check) | RC4 · L1-03/04/05/06, L2-04/08/11 | Medium | Agent | **Adopt — highest leverage** |
| **P3** | **Make the canon diffable** (Codex as Markdown→rendered .docx; key tables in `canon.yml` read by code + docs; binary .docx can't be CI-checked) | RC1/RC4 · L2-01/02/06/09 | Med–Large | Agent + David | Adopt |
| **P4** | **"Rules-changed → canon-updated" DoD gate** (AI-enforced like the demo-mode rule; pricing/tiers/thresholds/intro-model/infra/endpoints/categories change ⇒ canon+requirements updated or CC opened same session) | RC1 · new drift at source | Small | Agent | Adopt |
| **P5** | **Make "land" atomic** (landing a CC = canon updated + ALL mirrors regenerated + pointer-check passes; partial propagation can't be marked done) | RC2 · partial propagation (CC-003) | Small | David + Agent | Adopt |
| **P6** | **Surface CC ageing in the daily brief** (any CC staged > N days appears in morning brief/dashboard; CC-001/002 sat 9–11 days) | RC1/RC2 · indefinite staging | Small | Agent | Adopt |
| **P7** | **Generate status, don't type it** (CLAUDE.md + Codex §4/§6/§9 → generated snippet or pointer; partly applied in A0) | RC4 · L1-06, L2-04/08/09/10 | Small–Med | Agent | Adopt |
| **P8** | **Reference values, don't restate** (docs cite PRICING_CANON/canon.yml; restated values tagged "(derived — see canon)") | RC3/RC4 · L1-07, L2-01/05 | Small | Agent | Adopt |
| **P9** | **Schedule this audit to re-run** (weekly/monthly scheduled task; drift caught in weeks not by hand) — I can wire it on your go | RC4 · residual drift | Small | Agent | Adopt |
| **P10** | **Single legal/version register** (one table: current version + landing status for EULA/IP/WhitePaper/Codex; counsel-gated flags) | RC2 · L1-09 | Small | David + counsel | Adopt |

Grouping — Structural: P1, P3, P8 · Automated checks: P2, P6, P9 · Process gates: P4, P5, P7, P10.

### Suggested minimal first wave
**P2** (canon-pointer check) + **P5 & P4** (atomic landing + rules→canon DoD) + **P9** (scheduled re-audit). Cheap, reversible, and between them they hit all four root causes. The structural items (P1/P3) are higher value but bigger — best done once the CC landing settles the canon.
