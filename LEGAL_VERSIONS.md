# LEGAL & CANON VERSION REGISTER
**Single source for "what version are we on, and has it landed?"** (P10 prevention measure.)
Version *values* are mirrored in `canon.yml`; `scripts/check_canon_pointers.py` asserts the two agree.
If a document version changes, update this table **and** `canon.yml`, then run the checker.

_Updated: 23 July 2026 · Owner: David._

| Document | Current version | Status | Counsel-gated | Notes |
|---|---|---|---|---|
| **Codex** | `Solar_Council_Codex_v4_8.docx` | **CANON** (adopted 21 Jun 2026) | No | Supersedes v4.7. CC-002 pricing parked → §3/§11 defer to PRICING_CANON. |
| **PRINCIPLE_REQUIREMENTS** | v1.5 | **CURRENT** (18 Jul 2026) | No | One canonical copy + 4 md5-identical mirrors. v1.5 adds PART H — The Third Pillar (AI sovereignty/access equity, H1–H6). |
| **AGENT_BRIEFING** | v1.9 | CURRENT (18 Jun 2026) | No | Single source for the three agents. |
| **PRICING_CANON** | pinned 15 Jun 2026 | **AUTHORITY** | No | The one place pricing is defined; code is the final word. |
| **EULA** | **v1.9** | **PUBLISHED 23 Jul 2026** (David's explicit instruction, pre-counsel — A6 counsel review remains OPEN) | **Yes** | v1.9 = live web fork (v1.3 lineage, which had drifted ahead of the docx: FICA deferred-KYC, Tuppence expiry, Casuals roles, AI 2T/3T/5T) + new: §2.6 not-a-referral, §8.10 Reference Library, §13.5 local-laws, §13.6 Country Schedules UK/US/AU. Shipped: terms.html + embedded copy in marketsquare.html gate. NOTE: docx lineage (v1.7→v1.8→v1.9 drafts in repo) and web fork MUST be consolidated by counsel — two forks exist. Last fully-Final = v1.4. |
| **IP Brief** | v6 | DRAFT | **Yes** | Recites Tuppence-HOLD claims C10–C13; counsel pending (A1). |
| **WhitePaper** | v3.11 | DRAFT (converged 23 Jun; alignment-corrected 29 Jun) | No (v2 is the published prior-art defensive publication — never edited) | v3.11 = current working/publication candidate. Frozen filing baseline: Patents/patent-loop/FILING_BASELINE_2026-06-29.md (docx pinned by sha256). |

## Landing dependencies (what must move together)
- **CC-001 (Tuppence HOLD):** Codex v4.8 §2/§12 (✅ landed) + IP Brief v6 + EULA v1.7 → **counsel** finalizes the legal pair.
- **CC-002 (pricing/AI canon):** parked — when landed, inline the current tiers into Codex §3/§11 (today they point to PRICING_CANON) + sync EULA pricing.
- **CC-003 (launch threshold):** ✅ landed (wave-trigger wording swept everywhere 21 Jun 2026).

## Counsel-gated items still open (external action)
1. EULA v1.9 counsel review + docx/web fork consolidation (A6) — v1.9 is LIVE pre-counsel per David, 23 Jul 2026.
2. IP Brief v6 finalization (A1) — must land with the EULA.
