# Session 80 — Opus Task: IP Brief + Patent Strategy Update
**Scheduled: Session 80 (4 sessions from Session 76)**
**Model: Claude Opus (mandatory — deep legal/technical reasoning required)**
**Estimated session length: Full session**

---

## Context — Why This Session Exists

TrustSquare is preparing to submit provisional patent claims to a South African patent attorney. Before that submission, the IP Brief and Patent Strategy documents must be brought fully up to date with all architectural decisions made since they were originally drafted (Sessions ~40–55 with Opus).

Two significant changes have occurred since the last IP document revision:

### Change 1 — Tuppence Model Correction (Session 76)
The original IP Brief and Patent Strategy documents described a penalty mechanism where sellers who ignored or declined introduction requests were charged a **1T resubmission fee**. This was incorrect — it was a legacy AI-suggested clause that contradicted the platform's core architecture.

**The corrected model (now codified as Principle A8):**
- Tuppence is deducted ONLY for voluntary purchases: Introduction fees, AI service fees, Boost fees.
- Negative behaviour is penalised exclusively via **Trust Score reduction** and ultimately **Banishment**.
- No Tuppence deduction is ever involuntary or punitive.

**Why this matters for the patent:**
- The original Claim 2 (distinguishing Tuppence from Bark.com/Thumbtack credit models) rested partly on the resubmission fee as a commitment signal. That argument must be rebuilt around the correct mechanism: **the buyer pays 1T on introduction, which is non-refundable regardless of seller response**. The commitment signal is the buyer's irreversible spend, not a seller penalty.
- The non-refundability of buyer Tuppence on introduction is the load-bearing novelty claim — not a seller fee.
- Tuppence's regulatory character (prepaid service credit, not a deposit under Banks Act s1) is strengthened by the absence of any involuntary deduction. This should be elevated in the IP brief as a deliberate architectural choice with regulatory rationale.

### Change 2 — Tuppence Pricing and Pack Tiers (Session 76)
- **1T = USD $2 fixed** (confirmed, not changed)
- **AI function pricing confirmed uniform:** all AI functions = 1T each, except Batch Cards (2T, vision-justified)
- **Pack tiers updated:** 20T / 50T / 100T / 250T (previously 5T / 10T / 25T)
- **Unified wallet:** AI spend and intro spend draw from the same Tuppence balance. Separate "AI Coach Credits" are legacy and will be deprecated.
- **Introduction model:** Buyer pays 1T on seller acceptance (not on submission). Seller pays nothing on accept/decline.

### Change 3 — Features Added Since Last IP Review
The following features exist in production that may be patentable or should be referenced in claims:
- **AI5 Batch Card Listings** — vision AI identifies collector cards from photos and generates listings in batch (Sonnet Vision, 2T per batch)
- **AI4 Yield Calculator** — AI-generated rental yield analysis for property listings (Haiku, 1T)
- **World Heritage auto-linking** — listings auto-linked to nearby UNESCO World Heritage sites via haversine proximity scoring
- **4-level geo hierarchy** — Country → Region → City → Suburb, with tier-gated buyer reach
- **Commitment model with listing pause** — Property listings pause on introduction, one buyer at a time, 48hr window
- **Trust Score credential declaration system** — sellers declare credentials for 80% points immediately; upload evidence for remaining 20%
- **Anonymous seller CV** — emoji avatar + locked identity until mutual acceptance

---

## Documents to Read First (in this order)

1. `STATUS.md` — current platform state
2. `AGENT_BRIEFING.md` — full platform model, Tuppence, anonymity rules
3. `PRINCIPLE_REQUIREMENTS.md` — all principles including A8 (no punitive Tuppence)
4. `TrustSquare_IP_Brief_v2_May2026.docx` — current IP brief (needs updating)
5. `TrustSquare_IP_Patent_Strategy_v1.docx` — current patent strategy (needs updating)
6. `TrustSquare_WhitePaper_v3_1.docx` — whitepaper (for context)
7. `Tuppence_Refund_Finding_and_Remediation_2026-05-12.docx` — the refund purge audit (critical background)
8. `TrustSquare_Pre-Filing_Patent_Consultation_ERRATUM_2026-05-12.docx` — the corrected Claim 2
9. `CHANGELOG.md` — Session 76 entries for Tuppence correction and A8 codification
10. `MarketSquare_EULA_v1_5_Draft.docx` — updated EULA (accept tracked changes to see clean text)
11. `Solar_Council_Codex_v4_7.docx` — updated Codex (accept tracked changes to see clean text)

---

## Task Instructions for Opus

### Step 1 — Audit
Read all documents above. Produce a gap analysis: what is in the current IP brief / patent strategy that is now incorrect or incomplete, citing specific sections.

### Step 2 — Update IP Brief (new version: v3)
Produce `TrustSquare_IP_Brief_v3_May2026.docx` with the following changes:
- Correct all references to 1T resubmission penalties — replace with Trust Score penalty model
- Elevate Principle A8 (no punitive Tuppence) as a deliberate architectural/regulatory choice
- Update Tuppence pack tiers and pricing
- Add new features (AI5 Batch Cards, AI4 Yield Calc, World Heritage linking, geo hierarchy) as potentially patentable elements or supporting prior art differentiators
- Strengthen the Banks Act / FSCA section: the absence of involuntary deductions is the key argument that Tuppence is a prepaid service credit, not a deposit
- Add a section on the unified wallet (AI + intro from same balance) as an architectural decision

### Step 3 — Update Patent Strategy (new version: v2)
Produce `TrustSquare_IP_Patent_Strategy_v2.docx` with:
- Corrected Claim 2 (remove resubmission fee; rebuild commitment-signal argument around buyer's irreversible 1T spend on acceptance)
- New claim candidate: AI-assisted batch listing generation from visual input (AI5)
- New claim candidate: proximity-based heritage/POI auto-linking for marketplace listings
- Confirm / update the three core novelty claims from v1
- Flag any claims that were weakened by the Tuppence correction and how they are rebuilt

### Step 4 — Produce Lawyer Handoff Summary
Produce `TrustSquare_Patent_LawyerBrief_Session80.docx`:
- 2–3 page executive summary suitable for handing to a South African patent attorney
- Lists all core claims, their novelty argument, and closest prior art
- Notes A8 and its regulatory rationale explicitly
- Flags the [COUNSEL REQUIRED] items from the EULA that overlap with patent territory
- Written in plain English, not technical jargon

### Step 5 — Update CHANGELOG and STATUS
Append Session 80 entry to CHANGELOG.md. Update STATUS.md next session goals.

---

## Definition of Done
- [ ] IP Brief v3 produced and saved to project folder
- [ ] Patent Strategy v2 produced and saved to project folder
- [ ] Lawyer Handoff Summary produced and saved to project folder
- [ ] No document contains any reference to 1T resubmission/penalty fees
- [ ] A8 principle explicitly cited in all three documents
- [ ] CHANGELOG updated
- [ ] STATUS.md updated

---

*Written Session 76 · 23 May 2026 · Scheduled for Session 80*
