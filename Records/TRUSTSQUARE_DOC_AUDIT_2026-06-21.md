# TrustSquare — Documentation Cross-Compliance Audit
**21 June 2026 · FOR REVIEW (findings only — no documents changed)**

- **Baseline (requirements/definition):** `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md` (v1.3 DRAFT, 10 Jun); pricing authority `PRICING_CANON.md` (15 Jun).
- **Codex assessed:** `Solar_Council_Codex_v4_8_DRAFT.docx` (latest) · `v4_7.docx` (controlling canon).
- **Current-truth:** STATUS.md (S139, BEA v1.3.1), AGENT_BRIEFING.md (v1.9), CHANGE_REGISTER.md (CC-001/002/003), CHANGELOG.md.
- **Independently validated by:** Dr. Elena Marsh (lead-auditor persona) — 24/27 confirmed, 0 refuted, 4 corrections applied, +1 finding added.
- Severity = governance/communication risk (agents/counsel acting on a wrong rule), not code defects.

## Headline (L2-12 — most material)
The **in-force Codex (v4.7) does not describe how money actually moves in the live system.** The Tuppence HOLD model, AI per-use pricing, AI-class gating and non-rolling grant are live in code but appear only in the **v4.8 DRAFT (NOT canon)**. v4.8 can't be promoted because **CC-001 + CC-002 are staged-not-landed** and **CC-003 is 0/5 opened**. Your suspicion that the Codex is behind is **confirmed**.

Findings by severity — List 1: 1 Critical · 3 High · 7 Medium · 3 Low/Info. List 2: 1 Critical · 7 High · 4 Medium · 2 Low.

---

## LIST 1 — Documents vs the Requirements baseline

| ID | Sev | Finding | Evidence | Validation |
|----|-----|---------|----------|------------|
| L1-01 | CRITICAL | Requirements doc in 5 divergent live copies (7 on disk) citing 3 different Codex versions | root v1.3→v4_8 · docs/ v1.2→v4_5 · AdvertAgent v1.1→v4_5 · CityLauncher v1.1→v4_4 · Codices v1.0→v4_4 (+_ARCHIVE/duplicates ×2); header says "four" | CONFIRMED |
| L1-02 | MEDIUM | Baseline mis-versioned: 1.3 header / 1.2 footer | line 3 "Version 1.3 — DRAFT" vs line 294 "End of … v1.2", line 296 "v1.2 changes:" | CONFIRMED |
| L1-03 | MEDIUM | Baseline names 3 Codex versions internally | §C5 line 155 = v4_5; header line 4 + QuickRef line 279 = v4_8/v4_7 | CONFIRMED |
| L1-04 | MEDIUM | Baseline cites wrong briefing version | QuickRef line 280 "v1.3 · 11 Apr"; header "v1.8-staged"; actual v1.9 | CONFIRMED |
| L1-05 | HIGH | Project CLAUDE.md names stale canonical Codex | CLAUDE.md line 8 = "v4_5 — canonical" (v4_7 controlling) | CONFIRMED |
| L1-06 | HIGH | CLAUDE.md "Current dev status" stale + self-contradictory | line 159 "BEA v1.2.0 · CPX22" & line 164 "Deploy Session 20" vs line 110 "CPX32" & STATUS "v1.3.1 · S139" | CONFIRMED (table-count not the defect) |
| L1-07 | MEDIUM ↓ | AGENT_BRIEFING still documents RETIRED "AI Coach Credits" packs | briefing line 31 "5T=40 uses…ai_pack_sessions"; retired per requirements A7 line 61 + PRICING_CANON §5; STATUS buy-pack→410 | PARTIALLY-CONFIRMED — citation fixed, HIGH→MEDIUM |
| L1-08 | INFO | "Adventures/Collectors not yet built" vs visible demo content | briefing line 18 vs STATUS demo listings | NEEDS-NUANCE — demo-vs-live, tighten wording |
| L1-09 | MEDIUM | EULA version drifts four ways | briefing v1.1 · Codex §12 "v1.7 must land" · evolution-audit v1.6 · requirements un-landed Session-77 clause (v1.7 DRAFT on disk) | CONFIRMED |
| L1-10 | HIGH | Baseline A6 still states CC-003-superseded 60-seller threshold | v1.3 line 49 & QuickRef 289-290; v1.2 line 49; same in AA + CityLauncher copies; CHANGE_REGISTER CC-003 0/5 | CONFIRMED (blast radius 4-5 files) |
| L1-11 | MEDIUM | Codices/CLAUDE.md uses retired versioned filenames + v4_1 Codex | Codices/CLAUDE.md lines 5-7 | CONFIRMED |
| L1-12 | LOW | CLAUDE.md uses non-existent tier "premium" | line 147 | CONFIRMED |
| L1-13 | LOW | CLAUDE.md hardcodes dead per-session SSH path | line 92 "/sessions/quirky-brave-galileo/…" | CONFIRMED |
| L1-14 | MEDIUM | CODEX_EVOLUTION_AUDIT.md still encodes retired "$40-Business" Founders-Badge terms | :206 vs PRICING_CANON §4 (rev3 Pro-only) vs Codex (rev2) | CONFIRMED (added by validator) |

## LIST 2 — Codex staleness vs the last month

**Top line:** controlling Codex = v4.7 (25 May); v4.8 stays DRAFT (CC-001/CC-002 staged). In-force canon predates the entire June program.

| ID | Sev | Finding | Evidence | Validation |
|----|-----|---------|----------|------------|
| L2-01 | CRITICAL | Codex tier tables carry RETIRED pricing | v4.8 §3/§11 = 5-tier $0/$12/$20/$40/$100 (self-flagged, line 101); v4.7 = older 3-tier $0/$5/$15; canon = Free/Starter$5/Pro$20/Agency. Pro slots Codex 25 vs canon 30 | PARTIALLY-CONFIRMED — re-attributed; kept CRITICAL |
| L2-02 | HIGH | Founders-Badge allocations rev2 (8/12/24/60T) superseded by rev3 (Pro-only) | v4.8 line 108 vs PRICING_CANON §4 | CONFIRMED |
| L2-03 | MEDIUM | §11 [DAVID: confirm] placeholders + retired §11.2 extra-slots | v4.8 lines 346-350 | CONFIRMED |
| L2-04 | HIGH | §5/§6 still describe CPX22 as live; "SSL expires 21 Jun 2026" (=today); CPX32 framed as future | v4.7+v4.8 §5/§6 vs reality CPX32 8GB €15.49/mo | CONFIRMED |
| L2-05 | MEDIUM | §6 breakeven uses retired tier "Premium" + retired pricing | v4.8 lines 193-196 | CONFIRMED |
| L2-06 | HIGH | §1 cities (Berlin, dropped for Sydney) + categories (Help Wanted; omits Adventures/Collectors/Travel/Tour_Guides) | v4.8 lines 22, 24 | CONFIRMED |
| L2-07 | HIGH | §1 "60 total (public launch)" superseded by CC-003 (≡ L1-10) | v4.8 lines 23, 248 (= v4.7) | CONFIRMED |
| L2-08 | HIGH | §4 self-references v4_5 inside v4.8; Alpha Checklist frozen at Session 11 | v4.8 line 115; lines 117-135 | CONFIRMED |
| L2-09 | HIGH | §5 BEA endpoint table April-era; "8 tables" vs 9+ | missing ai-commit/ai-settle/balance, dashboard/summary, PUT listings, listings/mine, versions, users photo, KYC, purge-cache, launch/sync-registry, demo-sellers | CONFIRMED |
| L2-10 | MEDIUM | §9 "Pending Agenda — Session 12" is April work | v4.8 §9 | CONFIRMED |
| L2-11 | LOW | World Heritage "120 sites" vs live 332 | v4.8 line 322 vs STATUS | CONFIRMED |
| L2-12 | HIGH | **Controlling v4.7 omits the entire June money-model program** (HOLD, AI per-use, AI-class gating, non-rolling grant); v4.8 has it but is NOT canon | v4.7 ends §11; v4.8 §12 footer "NOT CANON"; CC-001/002 staged | CONFIRMED (most material) |
| L2-13 | LOW | §10 version-history table ends at v4.6 | v4.8 footers 352/357 | CONFIRMED |
| L2-14 | MEDIUM | §2 Introduction-models omits Help Wanted + new categories | v4.8 line 34 | CONFIRMED |

---

## Validation log — corrections applied after Dr. Marsh's review
1. **L2-01 re-attributed** — retired 5-tier table is in v4.8 DRAFT (not §3 of controlling v4.7); v4.7 carries an older 3-tier $0/$5/$15. v4.8 is stale-but-self-flagged; kept CRITICAL because v4.7 is silently wrong. Pro-slot 25-vs-30 stands.
2. **L1-07 corrected + downgraded HIGH→MEDIUM** — the "AI-uses retired" line lives in requirements A7 / PRICING_CANON §5, not the briefing; the briefing fault is stale retained copy.
3. **L1-06 softened** — "9 tables" is nearer truth than the Codex's "8"; real defects are BEA version, CPX22↔CPX32, "Session 20".
4. **L1-01 / L1-10 blast radius** — 7 copies on disk (5 active + 2 archived); stale 60-seller line also in AdvertAgent + CityLauncher copies.
5. **L1-14 added** — evolution-audit doc still encodes retired "$40-Business" Founders-Badge terms.

Auditor verdict (verbatim): *"The audit is sound and high-confidence … every claimed discrepancy genuinely exists on disk … the canonical-documentation layer has materially decoupled from the running system, and PRICING_CANON.md + STATUS.md + live code — not the Codex — are doing the real source-of-truth work."*

## Root causes
1. CC-001/CC-002 staged-not-landed → v4.8 can't become canon → June pricing/HOLD/AI never propagates.
2. CC-003 only partially propagated (2 hot lines).
3. No enforced "regenerate + copy to all folders" step → 5-7 divergent requirements copies.
4. Hand-maintained narrative status blocks (CLAUDE.md, Codex §4/§6/§9) age silently — contra F3.

## Suggested remediation (for review — nothing changed yet)
1. Land CC-001 → CC-002, then promote Codex v4.8 to canon (clears most of List 2).
2. Finish CC-003 propagation (clears L1-10 / L2-07).
3. Collapse the requirements doc to one canonical copy + generated mirrors (clears L1-01/02/03/04/14).
4. Refresh CLAUDE.md status + Codex §4/§6/§9, or point them at /dashboard/summary.
5. Pin one current EULA version + land the Session-77 counsel clause (clears L1-09).
6. Optional: extend check_pricing_canon.py to assert doc↔canon version pointers so drift fails a check.

## Appendix — requirements-copy divergence
| Copy | Version | Source Codex cited | Briefing cited |
|------|---------|--------------------|----------------|
| MarketSquare/PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md | v1.3 DRAFT (10 Jun) | v4_8_DRAFT | v1.8-staged |
| MarketSquare/docs/PRINCIPLE_REQUIREMENTS.md | v1.2 (17 May) | v4_5 | v1.7 |
| AdvertAgent/PRINCIPLE_REQUIREMENTS.md | v1.1 (12 Apr) | v4_5 | v1.3 |
| CityLauncher/PRINCIPLE_REQUIREMENTS.md | v1.1 (12 Apr) | v4_4 | v1.3 |
| Codices/PRINCIPLE_REQUIREMENTS.md | v1.0 (11 Apr) | v4_4 | v1.3 |
| Codices/_ARCHIVE/duplicates/_1.md, _2.md | v1.0 (archived) | v4_4 | v1.3 |

## CC-package status (why canon is behind)
- **CC-001 (Tuppence HOLD):** 4/5 STAGED — nothing live; awaiting David term-map verify → land (Codex v4.8 / IP v6 / EULA v1.7).
- **CC-002 (Pricing + AI canon):** 4/5 STAGED — nothing live.
- **CC-003 (Launch-threshold correction):** 0/5 OPENED — only AGENT_BRIEFING:14 + CLAUDE.md:139 fixed.
