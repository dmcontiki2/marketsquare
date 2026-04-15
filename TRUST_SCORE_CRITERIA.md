# MarketSquare — Trust Score Criteria Framework
**Design Specification v1.0 · 15 April 2026**
**Governed by Principle A5 · Council review required to change tier thresholds**

---

## 1 · Framework Overview

The Trust Score (0–100) is the server-side sum of three signal groups. No signal is self-reported without verification. No signal is client-modifiable.

| Group | Description | Max pts |
|---|---|---|
| **Universal** | Identity, profile completeness, referrals — applies to every seller | 30 |
| **Category Credentials** | Qualifications, registrations, and professional standing per category | 40 |
| **Platform Track Record** | Demonstrated performance on MarketSquare | 30 |

**Total maximum: 100 pts**

**Tier thresholds (locked — Principle A5):**

| Score | Tier | Badge |
|---|---|---|
| 0–39 | New | None |
| 40–69 | Established | Blue |
| 70–89 | Trusted | Green |
| 90–100 | Highly Trusted | Gold + featured priority |

**Design intent by milestone:**

| Milestone | Typical score | Notes |
|---|---|---|
| ID verified, no credentials yet | ~20 | Universal partial |
| ID verified + core credentials | ~45–55 | Established tier |
| ID + full credentials + 6 months active | ~70–80 | Trusted tier |
| All of above + strong referrals + sustained record | 90+ | Highly Trusted |

---

## 2 · Group 1 — Universal Signals (all categories, max 30 pts)

### U1 · Identity Verification

| Signal | Pts | Verification |
|---|---|---|
| Government-issued ID verified by MarketSquare | 15 | Manual review — David/ops checks RSA ID or passport against uploaded document |

One-off. Score held if ID is not renewed — only removed on confirmed fraud finding.

### U2 · Profile Completeness

| Signal | Pts | Verification |
|---|---|---|
| Complete profile: bio written, active listing, suburb set, category description | 5 | System-calculated |

### U3 · Verified Referrals

Referrals submitted via a structured platform referral link tied to the seller's profile. MarketSquare validates the referrer is a registered user who completed a real introduction to the seller, or a verified external contact with a confirmed identity.

| Signal | Pts | Notes |
|---|---|---|
| 1st verified referral | 5 | |
| 3rd verified referral | +3 (cumulative 8) | |
| 5th+ verified referral | +2 (cumulative 10) | Capped at 10 pts total |

---

## 3 · Group 2 — Platform Track Record (all categories, max 30 pts)

### T1 · Introduction Performance

| Signal | Pts | Verification |
|---|---|---|
| 1st successful introduction (seller accepted, buyer proceeded) | 5 | BEA system |
| 5+ successful introductions | +5 (cumulative 10) | BEA system |
| 20+ successful introductions | +5 (cumulative 15) | BEA system |

### T2 · Reliability Window

| Signal | Pts | Verification |
|---|---|---|
| Zero ignored introductions in rolling 90-day window | 10 | System — resets on each violation (independent of A3 penalty) |
| Account active 6+ months with at least one live listing | 5 | System |

---

## 4 · Group 3 — Category Credentials (max 40 pts per category)

---

### 4a · PROPERTY

*South African regulatory context: The Property Practitioners Act 22 of 2019 mandates PPRA (Property Practitioners Regulatory Authority, formerly EAAB) registration for all practising agents. NQF qualifications are required for practitioner status. Unregistered Property sellers receive 0 Category Credential points — PPRA registration is a legal prerequisite.*

| Signal | Pts | Verification |
|---|---|---|
| Active PPRA / EAAB Registration Certificate | 15 | Certificate number checked against PPRA public register — must be current and active |
| NQF4 Real Estate qualification (entry-level, intern status) | 6 | Certificate uploaded and reviewed |
| NQF5 Real Estate qualification (candidate for professional status) | +6 (cumulative 12) | Certificate uploaded |
| NQF6+ Real Estate or higher professional designation | +8 (cumulative 20) | Certificate uploaded |
| Professional body membership (IEASA, SAPOA, NAR affiliate) | 5 | Membership card or letter uploaded |
| **Max** | **40** | |

---

### 4b · TUTORS

*South African context: SACE (South African Council for Educators) governs qualified teachers. University qualifications follow SAQA NQF levels. Private tutors without SACE can still earn full Category Credential points via qualifications and experience — SACE is a strong signal but not mandatory.*

| Signal | Pts | Verification |
|---|---|---|
| SACE (South African Council for Educators) registration | 8 | SACE number verified via sace.org.za public register |
| Highest qualification: Certificate or Diploma (NQF5–6) | 6 | Certificate uploaded and reviewed |
| Highest qualification: Bachelor's Degree (NQF7) | 10 | *Replaces Certificate/Diploma pts — not cumulative* |
| Highest qualification: Honours / Postgraduate (NQF8+) | 14 | *Replaces Bachelor's pts — not cumulative* |
| Subject specialisation evidenced (subject-specific cert or transcript) | 5 | Upload reviewed |
| Teaching / tutoring experience: 2–5 years | 5 | CV reviewed by MarketSquare |
| Teaching / tutoring experience: 5+ years | +6 (cumulative 11) | CV reviewed |
| Strong CV: structured, verifiable, employment dates with no unexplained gaps | 2 | Quality assessed at onboarding |
| **Max** | **40** | *Natural cap: SACE + best qualification + experience + specialisation + CV = 40* |

---

### 4c · SERVICES — TECHNICAL

*Covers tradespeople, contractors, and skilled technical service providers: electricians, plumbers, HVAC, solar installers, IT specialists, engineers, financial advisors, legal professionals, landscapers, and similar. South African context: ECSA (Engineering Council SA), PIRB (Plumbing Institute), MERSETA, CETA, City & Guilds, TVET college trade certificates, CoC (Certificate of Compliance).*

| Signal | Pts | Verification |
|---|---|---|
| Formal trade certificate (City & Guilds, TVET/NATED, MERSETA, CETA, Red Seal) | 8 | Certificate uploaded and reviewed |
| Professional / statutory body registration (ECSA, PIRB, NHBRC, FSCA, SAICA, etc.) | 12 | Registration number checked against body's public register — must be active |
| Primary industry ticket or licence (CoC for electrical, gas CoC, PIRB licence, etc.) | 5 | Certificate with expiry date uploaded |
| Additional tickets / specialisations (First Aid, working at heights, confined space, rigging) | +3 per ticket, max 6 | Certificates uploaded — max 2 additional tickets counted |
| Years in trade: 3–7 years | 4 | CV reviewed |
| Years in trade: 7+ years | +4 (cumulative 8) | CV reviewed |
| Strong CV: verifiable work history, references, no unexplained gaps | 2 | Quality assessed |
| **Max** | **40** | |

---

### 4d · SERVICES — CASUALS

*Covers general domestic and personal service providers: cleaning, gardening, childcare, pet care, handyman, delivery, child minding, general labour, and similar. No formal regulatory body — trust built primarily through identity, community vouching, and platform track record. ID verification carries maximum weight in this category.*

| Signal | Pts | Verification |
|---|---|---|
| Any relevant NQF qualification or accredited short-course certificate | 8 | Certificate uploaded (any NQF level accepted) |
| Declared years in service: 2–4 years | 6 | CV or written statement reviewed |
| Declared years in service: 5+ years | +8 (cumulative 14) | CV reviewed |
| Reference letter from a past employer or client (not a platform referral) | 8 | Letter scanned and reviewed — verifiable contact details required |
| Second reference letter | +5 (cumulative 13) | Max 2 reference letters counted |
| Strong profile description: specific services offered, suburb coverage, availability | 5 | Quality assessed at onboarding |
| **Max** | **40** | |

*Note: A Casual with ID (15 Universal) + 2 reference letters (13 Category) + 5+ years (14 Category) = 42 baseline before any track record. Intentional — this is the category where buyers need identity assurance most.*

---

### 4e · ADVENTURES

Adventures has two sub-classes: **Experiences** (guided activities) and **Accommodation** (B&B, guesthouses, boutique hotels). Sub-class is selected at listing creation and drives which credential signals apply.

---

#### Adventures — Experiences

*Covers guided outdoor and experiential activities: hiking, trail running, mountain biking, rock climbing, scuba diving, kayaking, wildlife safaris, cultural tours, skydiving, and similar. South African context: FGASA (Field Guides Association of SA), Mountain Club of SA (MCSA), PADI/NAUI/SSI (diving), SACAA (aviation/skydiving). Safety certifications carry the highest weight.*

| Signal | Pts | Verification |
|---|---|---|
| Activity-specific guide certification (FGASA, MCSA, PADI Divemaster+, SACAA, etc.) | 12 | Certificate number checked against issuing body register — must be current |
| Current First Aid / Emergency Response certificate (valid, not expired) | 6 | Certificate with expiry date uploaded |
| Years of guided experience in declared activity: 3–7 years | 5 | CV reviewed |
| Years of guided experience: 7+ years | +5 (cumulative 10) | CV reviewed |
| Additional safety certification (Wilderness First Responder, swift water rescue, etc.) | 4 | Certificate uploaded |
| Liability / public indemnity insurance for activity (current) | 5 | Policy summary with expiry uploaded |
| Secondary qualification or endorsement in declared activity | 3 | Certificate reviewed |
| **Max** | **40** | |

---

#### Adventures — Accommodation

*Covers B&B, guesthouses, boutique hotels, self-catering units, and similar. South African context: TGCSA (Tourism Grading Council of South Africa) provides the authoritative 1–5 star grading system. TGCSA grading is checked against the public register — expired gradings score 0.*

| Signal | Pts | Verification |
|---|---|---|
| TGCSA 1-star grading (current and active) | 6 | Grading number checked against TGCSA public register |
| TGCSA 2-star grading | 10 | *Replaces 1-star pts* |
| TGCSA 3-star grading | 14 | *Replaces 2-star pts* |
| TGCSA 4-star grading | 18 | *Replaces 3-star pts* |
| TGCSA 5-star grading | 22 | *Replaces 4-star pts — highest single credential on the platform* |
| Municipal / city licence to operate B&B or guesthouse | 6 | Licence document uploaded and reviewed |
| Health & safety compliance certificate | 5 | Certificate uploaded |
| Fire clearance certificate | 4 | Certificate uploaded |
| AA Travel Award, TripAdvisor Travellers Choice, or Booking.com Preferred designation | 3 | Award certificate or screenshot of listing reviewed |
| **Max** | **40** | *5-star TGCSA + licence + H&S + fire + award = exactly 40* |

*Scoring note: A 3-star graded B&B with licence, H&S, and fire cert = 14+6+5+4 = 29 Category pts. With full Universal + partial Track Record, Trusted status (70+) is reachable.*

---

### 4f · COLLECTORS

*Covers vintage, rare, and collectible items: coins, stamps, antiques, memorabilia, art, watches, books, records, trading cards, and similar. Trust in this category is primarily transaction-history based — the collector's platform record IS the credential. External authentication is a strong differentiator for high-value items.*

| Signal | Pts | Verification |
|---|---|---|
| Category specialisation declared (specific collecting domain with written description) | 4 | Profile field reviewed at onboarding |
| Items successfully transacted on MarketSquare: 1–4 | 8 | BEA system |
| Items successfully transacted: 5–14 | +6 (cumulative 14) | BEA system |
| Items successfully transacted: 15+ | +6 (cumulative 20) | BEA system |
| Third-party authentication certificate for a listed item (SANA, PCGS, PSA, CGC, etc.) | 8 | Certificate uploaded per item — counted once per listing, max 1 contribution |
| Professional appraisal or valuation from a recognised appraiser | 5 | Document reviewed |
| Membership of a recognised collector association (SANA, Philatelic Foundation, etc.) | 3 | Membership card or certificate uploaded |
| **Max** | **40** | |

*Design note: Collectors who are new to the platform start low regardless of real-world standing. Score rises primarily through platform transactions. Consistent, honest dealing is the main trust signal.*

---

## 5 · Penalty Framework

### 5a · Complaint Penalties

**Source requirement:** Complaints accepted only from verified buyers who have submitted an introduction to that specific seller. Anonymous or external complaints are not accepted.

**One complaint per pair:** Each buyer may file a maximum of one complaint against any given seller (lifetime).

**Reason required:** Every complaint must include a reason code from: No-show · Misrepresentation · Safety concern · Behaviour or conduct · Item/service not as described · Service not delivered.

**Diminishing scale** (prevents coordinated attacks from eliminating a credentialled seller):

| Complaint number | Points deducted |
|---|---|
| 1st complaint | −8 |
| 2nd complaint | −5 |
| 3rd complaint | −3 |
| 4th complaint | −2 |
| 5th and each subsequent | −1 |
| **Maximum total deduction from complaints** | **−22 pts** |

*Intent: A seller who has legitimately earned Trusted status (75 pts) drops to Established (53 pts) at maximum complaint load — not to New. Genuine credentials cannot be erased by complaints alone.*

### 5b · Complaint Decay

- Each complaint older than 24 months contributes 50% of its original deduction.
- A successfully disputed complaint (David/ops rules in seller's favour) is removed and the deducted points restored.

### 5c · Complaint Escalation Triggers

| Trigger | Action |
|---|---|
| 3+ complaints against one seller within 90 days | Automatic manual review flag — seller notified, David reviews |
| 5+ complaints filed by one buyer against different sellers in 30 days | Buyer's complaints quarantined pending review — possible bad-actor pattern |
| Safety concern complaint (any) | Immediate manual review — listing may be paused pending outcome |

### 5d · Bad Referral Penalties

A referral found on review to be fabricated, from a conflicted party, or contradicted by platform evidence:

| Penalty | Detail |
|---|---|
| Fraudulent referral confirmed | −10 pts + removal of all referral pts the fabrication generated |
| Referral from a buyer with no completed introduction to that seller | Referral invalidated — 0 pts, no penalty unless fraud pattern |

---

## 6 · Anti-Manipulation Principles

These rules are non-negotiable. No exceptions without council review.

1. **No self-reporting without verification.** Every credential signal requires a document upload and manual approval by David/ops. Sellers cannot award themselves points.

2. **Registration numbers are checked live.** PPRA, SACE, PIRB, ECSA, TGCSA, FGASA, and other professional register numbers are verified against the issuing body's public register. Expired or suspended registrations score 0.

3. **Track record is system-calculated only.** Introduction counts, response rates, and account tenure are written by BEA on events — never editable by sellers or admins.

4. **Referrals require a verified origin.** Referrals must come from a registered platform user who completed a real introduction, or from a manually verified external contact. Unverified referrals are held pending review.

5. **Star grading is checked against TGCSA.** An expired TGCSA grading scores 0 pts until renewed and re-verified.

6. **Complaint cap protects genuine sellers.** The −22 cap prevents complaint brigading from destroying a credentialled seller's visibility. Escalation triggers catch coordinated attacks.

7. **Score is server-side only.** Trust Score is computed and stored in BEA. There is no client-side score state. No frontend value is trusted as a score input.

8. **Credential expiry is tracked.** Certificates with expiry dates (First Aid, CoC, insurance, TGCSA) are flagged for re-verification before expiry. Expired credentials score 0 until renewed.

---

## 7 · Verification Workflow

All credential signals follow this pipeline:

1. **Upload** — Seller submits document via admin tool or seller profile (photo upload endpoint: `POST /listings/photo`)
2. **Review queue** — Submission flagged for manual review in admin dashboard
3. **Verification** — David/ops checks document authenticity, checks registration number against public register where applicable, approves or rejects
4. **Score update** — BEA updates `trust_score` on the `users` record on approval
5. **Expiry tracking** — Certificates with expiry dates noted; re-verification reminder generated before expiry

System-calculated signals (intro count, account age, profile completeness, ignored-intro window) update automatically via BEA event logic — no manual step required.

---

## 8 · Score Recalculation

Trust Score is recalculated in full whenever:
- A credential is approved or rejected
- An introduction event is accepted or ignored
- A complaint is filed, resolved, or decayed
- A referral is verified or invalidated
- A listing is published or removed (profile completeness may change)

Score is never cached on the client. Every display reads from BEA.

---

*End of TRUST_SCORE_CRITERIA.md v1.0*
*Changes to tier thresholds require council review (Principle A5). Changes to signal weights require Architect agent sign-off. Append amendments as versioned sections — do not overwrite.*
