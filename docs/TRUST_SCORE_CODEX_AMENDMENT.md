# Trust Score Criteria — Codex Amendment
**For insertion into Solar_Council_Codex_v4_4.docx**
**Prepared: 15 April 2026 · Version 1.0**

---

## How to apply this amendment

1. Open `Solar_Council_Codex_v4_4.docx` in Claude Chat (upload the file)
2. Ask Claude Chat to insert the section below into the Codex as a new chapter, after the existing Trust Score section (A5)
3. Increment the Codex version to v4.5
4. Download the updated .docx and replace `Solar_Council_Codex_v4_4.docx` in this folder
5. Update `CLAUDE.md`, `STATUS.md`, `AGENT_BRIEFING.md` (both projects), and `PRINCIPLE_REQUIREMENTS.md` references from v4_4 to v4_5

---

## Content to insert

---

### A5a · Trust Score Criteria — Category-Specific Signal Framework

*This section expands Principle A5. The tier thresholds (0–39 New / 40–69 Established / 70–89 Trusted / 90–100 Highly Trusted) remain locked under A5. This section governs how the score is earned.*

The Trust Score is the server-side sum of three groups. Full specification in `TRUST_SCORE_CRITERIA.md`.

**Group 1 — Universal (max 30 pts, all categories)**

- Government ID verified by MarketSquare: 15 pts
- Complete seller profile (bio, suburb, active listing, description): 5 pts
- Verified referrals: 1st = 5 pts · 3rd = cumulative 8 pts · 5th+ = cumulative 10 pts (capped)

**Group 2 — Platform Track Record (max 30 pts, all categories)**

- 1st successful introduction: 5 pts · 5+ intros: 10 pts · 20+ intros: 15 pts
- Zero ignored intros in rolling 90-day window: 10 pts
- Account active 6+ months with live listing: 5 pts

**Group 3 — Category Credentials (max 40 pts per category)**

| Category | Highest-weight credential | Key additional signals |
|---|---|---|
| Property | PPRA/EAAB Registration: 15 pts | NQF4–NQF6+ (up to 20 pts cumulative) · Prof body: 5 pts |
| Tutors | SACE registration: 8 pts | Best qualification NQF5–NQF8+ (6–14 pts) · Experience · CV |
| Services — Technical | Prof body registration: 12 pts | Trade cert: 8 pts · Primary ticket: 5 pts · Experience · CV |
| Services — Casuals | Reference letters: up to 13 pts | NQF qualification: 8 pts · Years in service (up to 14 pts) |
| Adventures — Experiences | Guide certification: 12 pts | First Aid: 6 pts · Insurance: 5 pts · Experience · Safety certs |
| Adventures — Accommodation | TGCSA 5-star grading: 22 pts | Municipal licence: 6 pts · H&S cert: 5 pts · Fire clearance: 4 pts |
| Collectors | Platform transactions: up to 20 pts | Authentication cert: 8 pts · Appraisal: 5 pts · Association: 3 pts |

**Adventures category split (effective from this amendment):**
Adventures has two sub-classes — **Experiences** (guided activities) and **Accommodation** (B&B, guesthouses, boutique hotels). Sub-class is declared at listing creation. Credential signals differ per sub-class as detailed in TRUST_SCORE_CRITERIA.md §4e.

---

### A5b · Trust Score Penalty Framework

**Complaint penalties (diminishing scale, capped at −22 pts total):**

1st complaint: −8 · 2nd: −5 · 3rd: −3 · 4th: −2 · 5th+: −1 each · Max total: −22

- Complaints accepted only from verified buyers who submitted an introduction to that seller
- One complaint per buyer-seller pair (lifetime)
- Complaints older than 24 months: 50% weight decay
- Successfully disputed complaint: removed, points restored
- 3+ complaints against one seller in 90 days → manual review flag
- Safety concern complaint → immediate manual review, listing may pause

**Bad referral penalty:**
- Fabricated referral confirmed: −10 pts + reversal of all referral pts generated

---

### A5c · Anti-Manipulation Rules (locked)

1. All credential signals require document upload and manual approval — no self-reporting
2. Registration numbers verified against public registers (PPRA, SACE, TGCSA, etc.) — must be active
3. Track record signals are BEA system-calculated only — not editable
4. Referrals require a verified platform origin (completed introduction or manually verified contact)
5. Star grading verified against TGCSA register — expired = 0 pts
6. Trust Score computed server-side only — no client-side score state
7. Certificates with expiry dates tracked — expired credentials score 0 until renewed

---

*End of Codex amendment. Source document: TRUST_SCORE_CRITERIA.md v1.0 · 15 April 2026*
