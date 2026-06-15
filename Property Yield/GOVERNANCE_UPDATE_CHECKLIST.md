# Yield Estimation System — Governance Documents Update Checklist
**Version:** 0.1 (Initial draft)  
**Date:** 19 May 2026  
**Owner:** David Conradie  
**Status:** Pre-execution — design phase complete, awaiting Solar Council review

This checklist is the single reference for which governance documents require updates as the Yield Estimation System progresses through its build sequence. For each document it records the current version, the version target at each key milestone, and the trigger event that drives the update. All updates are mandatory unless marked optional.

---

## Key Milestones

| ID | Milestone | Description |
|----|-----------|-------------|
| M0 | Governance checklist approved | This document accepted by David — activates tracking |
| M1 | Solar Council review complete | ChatGPT + Grok review done; both source docs updated to v0.2 |
| M2 | Phase 1 complete | Schema and reference data live on server |
| M3 | Phase 3 complete | Calculation pipeline and snapshots live; first yield figures computable |
| M4 | Phase 6 complete | Admin-gated user surface live; internal validation period begins |
| M5 | Patent filing complete | SA provisional patent application lodged |
| M6 | Public launch | Feature flag `yield_estimates_public = true` set on production |

---

## Document Register

### 1. YIELD_SYSTEM_TECHNICAL_DISCLOSURE.txt
**Location:** `C:\Users\David\Projects\MarketSquare\Property Yield\`  
**Current version:** 0.1  
**Classification:** Pre-filing confidential — patent material

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M1 | 0.2 | Solar Council review complete — incorporate accepted comments |
| M2 | 0.3 | Phase 1 complete — add implementation evidence for schema (Steps 1.1–1.5) |
| M3 | 0.4 | Phase 3 complete — add calculation pipeline implementation evidence |
| M4 | 0.5 | Phase 6 complete — add admin surface and feature flag implementation evidence |
| M5 | 1.0 | Patent filing — finalise as filing-ready disclosure document |
| M6 | 1.1 (if needed) | Public launch — update status fields; no substantive changes post-filing |

**Rule:** After each build step is completed, the corresponding section of this document is updated with implementation evidence. This is part of the step, not optional (per Build Sequence governance notes).

---

### 2. YIELD_SYSTEM_BUILD_SEQUENCE.txt
**Location:** `C:\Users\David\Projects\MarketSquare\Property Yield\`  
**Current version:** 0.1  
**Classification:** Pre-filing confidential

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M1 | 0.2 | Solar Council review — incorporate architectural or sequencing feedback |
| M2 | 0.3 | Phase 1 complete — update step statuses to Completed |
| M3 | 0.4 | Phase 3 complete — update step statuses; note any sequencing changes |
| M4 | 0.5 | Phase 6 complete — update step statuses |
| M5 | 0.6 | Patent filing — mark Phase 8 steps In Progress |
| M6 | 1.0 | Public launch — mark all steps Completed; archive |

---

### 3. GOVERNANCE_UPDATE_CHECKLIST.md (this document)
**Location:** `C:\Users\David\Projects\MarketSquare\Property Yield\`  
**Current version:** 0.1

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M0 | 0.1 | David approves this draft |
| M1 | 0.2 | Solar Council review — update milestone dates if adjusted |
| Any | Patch | New document added to the register, or trigger event changes |

---

### 4. Solar_Council_Codex_v4_5.docx
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** 4.5

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M1 | — | **Review only** — confirm yield system design does not conflict with existing Codex rules |
| M3 | 4.6 (if needed) | If calculation pipeline introduces a new product rule not covered in Codex — escalate to David for Codex amendment |
| M6 | 4.6 | Public launch — add Yield Badge and Self-funding Filter to product feature register in Codex |

**Rule:** No Codex update without David's explicit approval. Conflicts are escalated, not resolved unilaterally.

---

### 5. PRINCIPLE_REQUIREMENTS.md
**Location:** `C:\Users\David\Projects\AdvertAgent\`  
**Current version:** Not versioned (confirm and add version tag at M1)

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M1 | Confirm current + add version tag | Solar Council review — verify Parts A–F and new Part G (G1–G4) remain consistent with yield system design |
| M3 | Patch if needed | Calculation pipeline — if Fisher equation or confidence scoring introduces a new sovereignty or data principle |
| M6 | Patch | Public launch — confirm all user-facing yield disclosures comply with existing principles |

---

### 6. AGENT_BRIEFING.md
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** Check and record at M0

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M2 | Patch | Phase 1 complete — add yield system schema tables to BEA table inventory |
| M3 | Patch | Phase 3 complete — add `/yield/estimate` BEA endpoint to API surface listing |
| M4 | Patch | Phase 6 complete — add admin yield surface to admin app section |
| M6 | Patch | Public launch — add yield badge to FEA listing card description |

---

### 7. CLAUDE.md (TrustSquare)
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** Not versioned

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M2 | Patch | Phase 1 complete — add note: `listing_yield_snapshots` and `feature_flags` tables added to SQLite; Rule B7 applies to all yield data sources |
| M6 | Patch | Public launch — update Current Development Status section; remove yield admin-gated note |

**Rule:** CLAUDE.md is updated for major structural changes only — not routine build steps (per existing rule).

---

### 8. STATUS.md
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** Session 64 state (live)

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| Each session | Current session | End-of-session checklist (existing rule) — reference yield system progress in Open Actions until Phase 1 begins |
| M2 | Session N | Phase 1 complete — add "Yield System Phase 1 complete" to Last Completed |
| M6 | Session N | Public launch — move yield system to Live State section |

---

### 9. CHANGELOG.md (TrustSquare)
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** Append-only log

| Milestone | Trigger Event |
|-----------|---------------|
| M2 | Phase 1 complete — append session entry noting schema migration steps completed |
| M3 | Phase 3 complete — append session entry noting calculation pipeline live |
| M4 | Phase 6 complete — append session entry noting admin yield surface live |
| M6 | Public launch — append session entry: yield feature public, feature flag set |

---

### 10. TrustSquare_IP_Brief_v2_May2026.docx
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** v2 (May 2026)

| Milestone | Target Version | Trigger Event |
|-----------|---------------|---------------|
| M1 | v3 | Solar Council review — if yield system IP (self-funding filter / yield badge) is added as a formal claim. Currently referenced in Section 5 questions for counsel. |
| M5 | v3 or v4 | Patent filing — update to reflect final claim set as filed |

**Note:** Claim 3 (self-funding filter) is already referenced in v2. After Solar Council review, confirm whether BACKLOG items H7 and F8 are elevated to formal patent claims requiring counsel brief update.

---

### 11. BACKLOG.md
**Location:** `C:\Users\David\Projects\MarketSquare\`  
**Current version:** Not versioned

| Milestone | Trigger Event |
|-----------|---------------|
| M3 | Phase 3 complete — mark H7 (Rental yield badge) and F8 (Self-funding property filter) as In Progress or move to active sprint |
| M6 | Public launch — mark H7 and F8 as Completed |

---

## Open Actions Outside Build Sequence

These items appear in the Build Sequence governance notes and are tracked here for completeness. They are not build steps but must be completed before or alongside specific milestones.

| Action | Owner | Target Milestone | Notes |
|--------|-------|-----------------|-------|
| Select SA patent attorney | David | Before M5 | Required before provisional patent application can be lodged |
| EULA revision for yield disclaimer | David + Counsel | Before M6 | Per-jurisdiction disclaimer language; cannot launch publicly without this |
| Per-jurisdiction regulatory review | David + Counsel | Before M6 | Confirm yield display does not constitute regulated financial advice in ZA, UK, USA |
| CIPC registration complete | David | Before M6 | Required for Paystack live mode; also relevant to FSCA status |
| Confirm FSCA position on yield badge | Counsel | Before M6 | Section 5 question 4 from IP Brief v2 |

---

## Version Discipline Rules (for this document)

All updates to this checklist must be recorded in the change log below. Version increments follow: major version (x.0) for milestone-level additions; minor version (x.y) for document additions or trigger event changes; no patches without a log entry.

---

## Document Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1 | 2026-05-19 | Claude (Cowork) | Initial draft — full document register, 11 documents, 6 milestones, open actions table |
