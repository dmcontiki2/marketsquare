# Patent + Whitepaper Convergence Loop — Audit Trail

**Run date:** 2026-06-23
**Documents:** `patent.md` (provisional spec) · `whitepaper.md` (technical whitepaper, = patent's Detailed Description by reference)
**Inputs:** patent v6.0, whitepaper v3.5 (extracted from the frozen counsel-gated .docx originals)
**Current working state:** patent **v6.5**, whitepaper **v3.10**
**Loops executed:** 6 (loop 1 inspected separately; loops 2–6 = the second batch)
**Outcome:** Effective convergence on auto-fixable items at loop 3, held stable through loops 4–6. Δ on auto-fixable defects = 0. Major baseline (v7.0 / v4.0) NOT yet applied — awaiting David's post-inspection decision.

## Convergence rule in force
Counsel-gated items (`unresolved_for_human`) do NOT block convergence (David, 2026-06-23). The loop converges once every auto-fixable defect is resolved and only counsel calls remain.

## Audit method note
Loops 1–2 used a fresh adversarial **sub-agent** auditor (clean-room context). Loop 2's sub-agent read through the sandbox FUSE mount and reported a **phantom "Abstract truncated" blocker** (AUD-2-001) that did not exist on the authoritative Windows file — the documented MOUNT-READ / false-RED fault. Per David's instruction, loops 3–6 used an **inline mount-safe audit** via the authoritative file tool, eliminating phantom-truncation findings while preserving the adversarial checklist.

## Jurisdictions checked (SA-first, then secondary)
South Africa (CIPC, CPA 68/2008 s63 & s63(3), POPIA s69 & s71, Banks Act 94/1990, SARB Draft Payment Activities Exemption Notice 14 Nov 2025) · WIPO/PCT · US (USPTO §112, §101 Alice + Recentive Apr 2025) · EU (EPO T 0641/00 COMVIK, EU AI Act Art. 50 / limited-risk) · APAC (CNIPA — no new prior art).

## Loop-by-loop summary
| Loop | Versions | Search focus (rotated, no reuse) | Auto-fixable defects resolved | Counsel items parked |
|---|---|---|---|---|
| 1 | 6.0→6.1 / 3.5→3.6 | SA + US prior art; CPA s63; CIPC novelty | Composite→signal-points (Summary/Abstract); prior-art design-arounds (3 refs); Pingsby narrowed | CPA claim-text; applicant id; Pingsby/C3; Banks Act; novelty search |
| 2 | 6.1→6.2 / 3.6→3.7 | POPIA; EPO COMVIK | Revenue table reconciled; "all implemented" scoped; verified-delivery defined; Summary vi narrowed; Banks Act hedged; projections labelled; masthead; 5-tier→tier-agnostic | (same, carried) + applicant-id footer flagged |
| 3 | 6.2→6.3 / 3.7→3.8 | Escrow prior art; Alice §101 | Annex version pointer; escrow design-around; §101/COMVIK framing note | + escrow refs to novelty search; §101 framing |
| 4 | 6.3→6.4 / 3.8→3.9 | CNIPA/WIPO; SARB; EU AI Act | EU AI Act Art.50 transparency line (additive) | (no new) — SARB + AI Act corroborate existing hedges |
| 5 | 6.4→6.5 / 3.9→3.10 | Matching-method prior art; POPIA s71 | **US 8,095,377 closest-prior-art design-around** (additive) | + POPIA s71; US8095377 as primary ref to distinguish |
| 6 | 6.5 / 3.10 (no change) | Confirm US8095377; no new prior art | **none — Δ=0 on auto items** | (stable) |

## All search queries executed
See `search_history.log` (16 queries across 6 loops; no string reused between consecutive loops).

## Counsel hand-off checklist (the parked items — these are the real next actions)
1. **CPA s63 / s63(3) — claim text.** Reconcile "non-refundable under any circumstance" / "no restitution logic" in independent Claim B against the consumer's statutory property right in the un-burned float. Distinguish burned (service-rendered, non-refundable) from un-burned (reclaimable). Move EULA dormancy to ≥36 months; fix EULA §5.3 vs §6.3.
2. **Applicant identity.** Patent filed natural-person; whitepaper footer/§9 say corporate. Fix the inconsistency and document the inventor→applicant assignment/licence chain; confirm PCT/USPTO small-entity basis.
3. **C3 / Pingsby.** C3 still CONDITIONAL. Pingsby is a dating-intro service (different field of use) — narrows but does not clear. Clear, narrow, or drop C3.
4. **Banks Act / SARB.** Confirm Tuppence's non-financial-product, closed-loop classification under the SARB Draft Payment Activities Exemption Notice (14 Nov 2025; comment period closed 5 Dec 2025). Do NOT add MiCA/crypto scaffolding — Tuppence is non-transferable credit.
5. **POPIA s71.** Confirm the trust score never operates as a solely-automated consequential decision without human involvement / an explanation path.
6. **Professional novelty search.** Independently confirm every cited reference (US20120030054A1, US20090076967A1, US 11,107,154, US 6,865,559, US20060253339A1, **US 8,095,377**, US 8,494,867) recites what the Background attributes. **US 8,095,377 is the closest reference** and must be distinguished in the complete specification.
7. **§101 / COMVIK framing.** At complete-spec / PCT drafting, frame the claims as a specific technical improvement (typed hold state machine; indexed existence gate; daily cost-ceiling pre-flight), not an abstract business method — per Alice/Recentive (US) and COMVIK (EPO).

## Provenance / safety
- The counsel-gated **.docx originals were never opened or edited.** All work was on `.md` working copies.
- No prior-art number or citation was invented; every reference came from a live web-search result this run and every one is flagged for independent professional confirmation before filing.
- Per-version snapshots are in `archive/` (patent v6.0–v6.5, whitepaper v3.5–v3.10).
