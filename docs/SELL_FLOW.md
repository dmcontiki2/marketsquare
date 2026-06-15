# TrustSquare — +Sell Flow Design Spec
**Version 3.0 · 2 May 2026 · AI-guided flow with full Trust Score signal integration**
*Architect agent sign-off required for changes*

---

## Core Principle: 1 · 2 · 3

New sellers go live in three taps. No friction, no Trust Score prompts, no AI guidance on first listing — just live. The full AI-guided experience belongs to the returning seller path. The AI is not an optional extra in the returning path — it is the guide for every step.

---

## Path A — New Seller (First Time, 3 Steps Only)

### Step 1 — Photo
Single photo. Full-screen prompt. Camera or gallery. Skippable with nudge: *"Listings with photos get 3× more intro requests."*

### Step 2 — Category + Headline + Price
- Category tiles: Property · Tutors · Services · Adventures · Collectors · Cars
- Sub-category after main selection (Technical/Casuals under Services; Experiences/Accommodation under Adventures)
- **"What are you offering?"** — short headline
- **Price / rate** — optional
- Commitment model note below the price field: *"Property listings pause when a buyer requests an intro — you respond within 48 hours."*

### Step 3 — Identity + EULA (on first "List now" tap)
- Name · Email · City
- ☑ EULA accepted (required)
- ☑ B5/B6 permanent block acknowledged (required, separate checkbox)
- On submit: POST /users → POST /listings → `listing_status = 'live'` → 3 free AI sessions credited → dashboard

**New seller is live. No AI, no Trust Score, no friction.**

---

## Path B — Returning Seller (Full AI-Guided Flow)

### B1 — Account Picker Sheet
Bottom sheet. "Continue as [name]" → dashboard. "+ Add new listing" → B2. "Use different account" → onboard.

---

### B2 — Category + Agent/Private Gate

Category tiles. For **Property** and **Cars**: immediately ask agent/dealer vs private seller — this gates which Trust Score signals appear later.

> Property: *"Are you a registered estate agent or a private seller?"*
> Cars: *"Are you a registered dealer or selling your own vehicle privately?"*

---

### B3 — Structured Fields (AI note inline)

Category-specific fields. Filled first — they feed the AI description in B4 and define which room photos to request in B5.

**At the bottom of the form, inline AI reacts to what has been entered:**
- Property: *"A 3-bed, 2-bath in Waterkloof — similar listings currently asking R2.1m–R2.8m."*
- Tutors: *"Online Maths Grade 12 tutors in Pretoria are currently charging R200–R350/hour."*
- Services: *"Electricians with a CoC in Pretoria typically charge R650–R950/hour call-out."*

This is a free Haiku call — no session consumed.

**Property fields:** Listing type · Property type · Bedrooms · Bathrooms · Garages · Floor size (m²) · Stand size (m²) · Suburb · Price
**Tutors fields:** Subjects · Level · Format (In-person/Online/Both) · Rate · Suburb
**Services — Technical:** Trade type · CoC held? · Call-out area · Rate
**Services — Casuals:** Type of work · In-home service? (gates clearance prompt in Trust Score) · Availability · Rate
**Adventures — Experiences:** Activity type · Group size · Duration · Location · Rate
**Adventures — Accommodation:** Property type · Rooms/units · Grading (if held) · Nightly rate · Location
**Collectors:** Item category · Condition · Estimated value · Authentication status
**Cars:** Make · Model · Year · Mileage · Colour · Transmission · Engine · Condition · Asking price

---

### B4 — AI Drafts Description

AI generates a 3–5 sentence listing description from the structured inputs. Shown in an editable text box.

*"We wrote this from your details — edit anything that's not right."*

Seller edits directly. Free — no session consumed. CTA: "Looks good →" or "Edit more"

---

### B5 — Photo Gallery (AI-Guided, Room by Room)

The AI guides each photo request. Photos come after structured fields because now the system knows exactly what to ask for. Each request has: Upload · Camera shortcut · "Skip this room" · optional free-text caption field per photo.

**The AI introduces this step:**
*"Now let's add photos for each part of your listing. Buyers scroll through these before deciding to connect — the more you add, the stronger your listing."*

**Property (3-bed house example — built dynamically from B3 fields):**
- AI prompt per room, e.g.:
  - Lounge: *"Add a photo of the lounge — shoot from the corner to show the whole room."*
  - Kitchen: *"Kitchen photos sell houses. Natural light works best."*
  - Main bedroom: *"Show the bed and the window if you can — buyers want to picture themselves here."*
  - Bathroom: *"Clean and tidy before shooting — tile and fixture quality matters to buyers."*
  - Garden/Exterior: *"Step back to get the whole house in frame. Late afternoon light is flattering."*
  - Street view: *"Optional — helps buyers confirm the neighbourhood."*
- Caption field per photo: *"Add a short note about this room (optional) — e.g. 'Renovated kitchen 2024' or 'North-facing garden'"*

**Tutors:**
AI: *"Add a photo that shows you in your element — at a desk, whiteboard, or with learning materials."*
Up to 4 photos. AI prompts each one: workplace photo · qualifications/certificates displayed · study materials. Each skippable with caption option.

**Services — Technical:**
AI: *"Show your work, your tools, or a completed job. Before/after pairs are very effective."*
Up to 4 photos. AI prompts: previous job completed · tools/equipment · certification display. Each skippable.

**Services — Casuals:**
AI: *"A friendly, clear photo of you builds confidence with buyers who will have you in their home."*
Up to 3 photos. AI prompts: professional headshot · reference letter (photographed) · example of work.

**Adventures — Experiences:**
AI: *"Show the experience in action — real guests, real scenery. Action beats studio shots."*
Up to 6 photos. Prompts: activity in progress · location/scenery · group/participants · safety equipment.

**Adventures — Accommodation:**
AI: *"Accommodation listings live or die on photos. Show every space — the room, the bathroom, the view."*
Up to 8 photos. Prompts per room type matching the accommodation type declared in B3.

**Collectors:**
AI: *"Photograph the item from multiple angles. Include any markings, signatures, or wear — buyers respect honesty."*
Up to 6 photos. Prompts: front view · back view · signature/marking detail · box/packaging · certificate of authenticity alongside item.

**Cars:**
AI: *"Car buyers want to see everything. Photograph all four sides, interior, engine bay, and any damage."*
Up to 10 photos. Prompts: front · rear · driver side · passenger side · interior front · interior rear · dashboard · engine bay · boot · any damage (seller self-declares).

---

### B6 — Seller Profile Photo (Selfie)

After the listing gallery. Always after, never before.

*"Add your profile photo — buyers want to see who they're dealing with. You stay anonymous until both of you agree to connect."*

AI note: *"A clear, front-facing photo improves buyer confidence significantly. You can update it any time from your profile."*

Camera (front-facing prompt on mobile) or gallery upload. Always skippable. Writes to POST /users/{email}/photo.

---

### B7 — Trust Score (AI-Guided, Category-Specific)

This is the richest part of the flow. The AI is the guide throughout — it explains every signal, tells the seller exactly what to upload, confirms each upload, and reminds them which signals they skipped.

**Opening:**
*"Your Trust Score determines how visible and credible you are to buyers. You don't need to complete this now — but the higher your score, the more intros you'll receive. Let's go through what applies to you."*

Live score shown at top. Updates in real time as signals are acted on. Tier badge upgrades visibly mid-flow.

**Each signal card shows:**
- Signal name and plain-English explanation of why it matters to buyers
- Points available (declaration pts / evidence pts if declarable)
- Status ring: ○ empty · ◑ declared · ● verified
- Primary CTA: Upload evidence
- Secondary CTA: Declare instead (where declarable — awards 80% of pts immediately)
- Skip link (always available)
- After upload: AI confirmation or flag

**AI confirmation examples:**
- *"This looks like a valid PPRA certificate — expiry detected March 2027. +15 points awarded. You're now Established 🔵."*
- *"This document appears to be a driver's licence, not a PPRA registration. Try uploading your Fidelity Fund Certificate instead."*
- *"SACE registration confirmed — number visible and format correct. +8 points."*
- *"Your trade certificate (City & Guilds, Electrical) has been verified. +8 points."*

**End of Trust Score step — AI reminds about skipped signals:**
*"You skipped [N] signals that could earn you [X] more points. You can add these any time from your profile — I'll remind you when you log in."*

---

## Trust Score Signals — Full List by Category

### All Categories — Universal Signals (auto-calculated, max 30 pts)

| Signal | Pts | How earned |
|--------|-----|-----------|
| Government-issued ID verified | 15 | Upload passport / national ID / driver's licence — AI vision verifies |
| Complete profile | 5 | Auto: bio + suburb + listing + category all filled |
| 1st verified referral | 5 | Auto: buyer confirms intro completed |
| 3rd verified referral | 3 | Auto: cumulative |
| 5th+ verified referral | 2 | Auto: cumulative, cap 10 pts total |

### All Categories — Platform Track Record (auto-calculated, max 30 pts)

| Signal | Pts | How earned |
|--------|-----|-----------|
| 1st successful introduction | 5 | Auto |
| 5+ successful introductions | 5 | Auto: cumulative |
| 20+ successful introductions | 5 | Auto: cumulative |
| Zero ignored intros (rolling 90 days) | 10 | Auto: any ignored intro resets this |
| Account active 6+ months with live listing | 5 | Auto: date-stamped |

---

### Property — Category Credentials (max 40 pts)

**Agent/private gate applies — private sellers see ✳ signals only.**

| Signal ID | Signal | Pts | Evidence | AI coaching script | Seller type |
|-----------|--------|-----|----------|--------------------|-------------|
| property.private_seller | Private seller declaration | 0 | Declare | *"Tell buyers you're a private seller — they need to know this upfront. It takes one tap."* | Private only |
| property.ppra | Active PPRA / EAAB Registration | 15 | Upload + AI verify | *"Your PPRA registration is the most important credential you can show. Upload your PPRA certificate — I'll confirm the number and expiry date."* | Agent only |
| property.ffc | Fidelity Fund Certificate (FFC) | 10 | Upload (annual) | *"The FFC is separate from your PPRA registration and lapses every year. Upload your current FFC — buyers and the law require it."* | Agent only |
| property.mandate | Mandate / instruction letter | 8 | Upload per listing | *"Upload the signed mandate or instruction letter from the property owner. This proves you're authorised to market this specific property."* | Agent only |
| property.nqf4 | NQF4 Real Estate qualification | 6 | Upload | *"Upload your NQF4 certificate. It's the foundation qualification recognised by the PPRA."* | Agent only |
| property.nqf5 | NQF5 Real Estate qualification | 6 | Upload | *"Upload your NQF5 — it stacks on top of your NQF4 and adds 6 more points."* | Agent only |
| property.nqf6_plus | NQF6+ / Professional designation | 8 | Upload | *"An NQF6 or professional designation puts you in the top tier of qualified agents. Upload your certificate."* | Agent only |
| property.body | Professional body membership | 5 | Upload | *"IEASA, SAPOA, or NAR membership signals you take your profession seriously. Upload your membership certificate."* | Agent only |
| property.exp_2_5 | Experience 2–5 years | 4 | Upload/Declare | *"Declare your years of practice — buyers value experience. I'll award 3 points immediately and 1 more when you upload your CV."* | Both ✳ |
| property.exp_10plus | Experience 10+ years | 5 | Upload/Declare | *"10+ years is a strong signal. Add it to your declaration — buyers can see it on your listing."* | Both ✳ |
| property.specialist_services | Specialist services declaration | 3 | Declare | *"Do you offer specialist services like bank valuations, bond origination, or conveyancing referrals? Declare them — buyers filter by this."* | Agent only |

---

### Tutors — Category Credentials (max 40 pts)

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| tutors.clearance | Police clearance / DBS check | 8 | Upload | *"Parents hiring tutors for children expect a criminal clearance check. Upload your SAPS clearance certificate — it's the single most trust-building thing you can do."* |
| tutors.sace | SACE registration | 8 | Upload + verify | *"SACE registration is required for school teachers in SA. Upload your SACE certificate — I'll verify the registration number."* |
| tutors.honours | Honours / Postgraduate (NQF8+) | 14 | Upload | *"Your highest qualification is your most valuable credential. Upload your honours or postgrad degree — it earns the most points in the chain."* |
| tutors.bachelor | Bachelor's Degree (NQF7) | 10 | Upload | *"Upload your degree certificate. If you have an honours degree, upload that instead — it earns more."* |
| tutors.cert_diploma | Certificate or Diploma (NQF5–6) | 6 | Upload | *"Upload your diploma or certificate. A bachelor's degree earns more if you have one."* |
| tutors.specialisation | Subject specialisation certificate | 5 | Upload | *"A subject-specific certificate shows buyers you're not just generally qualified — you specialise. Upload any relevant subject cert or transcript."* |
| tutors.exp_5plus | Teaching experience 5+ years | 6 | Upload/Declare | *"5+ years of teaching experience is a strong differentiator. Declare it now for 5 points, then upload your CV for the final point."* |
| tutors.exp_2_5 | Teaching experience 2–5 years | 5 | Upload/Declare | *"Tell buyers how long you've been teaching. I'll award 4 points on your declaration and 1 more when you upload your CV."* |
| tutors.safeguarding | Safeguarding / child protection cert | 3 | Upload | *"If you work with learners under 18, a safeguarding certificate reassures parents you've been trained in child protection. Upload yours."* |
| tutors.strong_cv | Strong structured CV | 2 | Upload | *"A well-structured CV rounds out your profile. Upload it — I'll check it's complete and confirm your points."* |
| tutors.online_ready | Online platform proficiency | 1 | Declare | *"If you tutor online, tell buyers which platforms you use — Zoom, Google Classroom, Teams. One tap."* |

*Note: Qualification chain — honours (14) replaces bachelor (10) replaces diploma (6). Max from qual chain = 14 pts.*

---

### Services — Technical (max 40 pts)

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| services_tech.body_reg | Professional body registration | 12 | Upload | *"ECSA, PIRB, NHBRC, FSCA, or SAICA registration is your most powerful credential. Upload your registration certificate — I'll verify the body and number."* |
| services_tech.insurance | Public liability insurance | 5 | Upload | *"Clients want to know you're insured before they let you work on their property. Upload your current liability policy — expiry date included."* |
| services_tech.cidb | CIDB grading (construction) | 6 | Upload | *"If you do construction work above R200k in SA, CIDB grading is legally required. Upload your CIDB certificate."* |
| services_tech.trade_cert | Formal trade certificate | 8 | Upload | *"Your trade certificate — City & Guilds, TVET, MERSETA, CETA, or Red Seal — is the foundation credential. Upload it."* |
| services_tech.coc | Primary industry licence / CoC | 5 | Upload | *"Your Certificate of Compliance proves you're legally authorised to do the work. Upload your CoC — buyers look for this before hiring."* |
| services_tech.tickets | Additional tickets (up to 2) | 6 | Upload | *"First Aid, working at heights, confined space — each ticket is worth 3 points. Upload up to 2."* |
| services_tech.exp_7plus | Trade experience 7+ years | 4 | Upload/Declare | *"7+ years in your trade is significant. Declare it now — 3 points immediately, 1 more with your CV."* |
| services_tech.exp_3_7 | Trade experience 3–7 years | 4 | Upload/Declare | *"Declare your years in trade — I'll award 3 points on your declaration and 1 more when your CV is uploaded."* |
| services_tech.strong_cv | Strong verifiable CV | 2 | Upload | *"A CV with references is a strong supporting document. Upload it — references included."* |

---

### Services — Casuals (max 40 pts)

*Note: If seller declared in-home service in B3, clearance is surfaced first and prominently.*

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| services_cas.clearance | Police clearance check | 10 | Upload | *"You declared that you work in clients' homes. A police clearance certificate is the #1 thing clients expect before letting someone into their home. Upload your SAPS clearance — it's worth 10 points and builds immediate trust."* |
| services_cas.ref_1 | Reference letter (1st) | 6 | Upload | *"A reference letter from a previous client is the most powerful thing a casual service worker can show. Upload a scanned letter with the client's contact details."* |
| services_cas.exp_5plus | 5+ years in service | 8 | Upload/Declare | *"5+ years of experience is a strong signal. Declare it now for 6 points, upload your CV for the full 8."* |
| services_cas.exp_2_4 | 2–4 years in service | 6 | Upload/Declare | *"Tell buyers how long you've been doing this work. 4 points on your declaration, 6 with a CV upload."* |
| services_cas.nqf | Any NQF qualification or short course | 8 | Upload | *"Any formal qualification or short course — even a 3-day course from a recognised provider — earns 8 points. Upload your certificate."* |
| services_cas.ref_2 | Second reference letter | 4 | Upload | *"A second reference from a different client adds credibility. Upload it if you have one."* |
| services_cas.in_home_flag | In-home service declaration | 0 | Declare | *"You declared you work in clients' homes — this is already on your listing so buyers know what to expect."* |
| services_cas.profile | Strong profile description | 5 | Auto | *"Your profile description is auto-assessed. The more detail you add to your bio, the higher this score."* |

---

### Adventures — Experiences (max 40 pts)

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| adv_exp.guide_cert | Activity-specific guide certificate | 12 | Upload + verify | *"Your guide certificate is the cornerstone credential. FGASA, PADI, MCSA, SACAA — upload the most relevant one. I'll verify the body and number."* |
| adv_exp.insurance | Liability / indemnity insurance | 5 | Upload | *"For activities involving physical risk, liability insurance is non-negotiable. Upload your current policy — expiry date included."* |
| adv_exp.permit | Operator permit / concession licence | 6 | Upload | *"If you operate in a national park, private reserve, or controlled waterway, upload your permit or concession licence. It proves you're authorised to operate there."* |
| adv_exp.first_aid | Current First Aid / Emergency Response | 6 | Upload | *"First Aid certification with a current expiry date is essential for high-risk activities. Upload yours — I'll check the expiry."* |
| adv_exp.exp_7plus | Guided experience 7+ years | 5 | Upload/Declare | *"7+ years of guiding is a strong credential. Declare it now — I'll award 4 points immediately and 1 more with your CV."* |
| adv_exp.exp_3_7 | Guided experience 3–7 years | 5 | Upload/Declare | *"Declare your years of guiding experience. 4 points on declaration, 5 with CV."* |
| adv_exp.safety_cert | Additional safety certificate | 4 | Upload | *"WFR, swift water rescue, avalanche cert — each additional safety qualification adds to your credibility. Upload one."* |
| adv_exp.secondary_qual | Secondary qualification in activity | 3 | Upload | *"Upload a second qualification related to your activity — up to 3 are counted."* |
| adv_exp.regulator_compliance | Regulatory compliance (SACAA/SAMSA/MCSA) | 5 | Upload | *"Beyond your guide cert, some activities require a separate regulatory compliance certificate — SACAA Part 135 for aviation, SAMSA for maritime. Upload yours if applicable."* |

---

### Adventures — Accommodation (max 40 pts)

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| adv_acc.tgcsa_5 | TGCSA 5-star grading | 22 | Upload | *"A 5-star TGCSA grading is the gold standard. Upload your current grading certificate — I'll check the expiry."* |
| adv_acc.tgcsa_4 | TGCSA 4-star grading | 18 | Upload | *"Upload your TGCSA 4-star certificate — it's the highest earner in this chain if you don't have 5-star."* |
| adv_acc.tgcsa_3 | TGCSA 3-star grading | 14 | Upload | *"Upload your TGCSA 3-star certificate."* |
| adv_acc.tgcsa_2 | TGCSA 2-star grading | 10 | Upload | *"Upload your TGCSA 2-star certificate."* |
| adv_acc.tgcsa_1 | TGCSA 1-star grading | 6 | Upload | *"Even a 1-star TGCSA grading signals you've been assessed. Upload it."* |
| adv_acc.licence | Municipal trading licence | 6 | Upload | *"Your local authority trading licence proves you're operating legally. Upload it."* |
| adv_acc.health_safety | Health & safety compliance | 5 | Upload | *"Upload your health and safety compliance certificate — guests expect accommodation to meet basic safety standards."* |
| adv_acc.tourism_levy | Tourism levy / bed tax registration | 4 | Upload | *"If your accommodation earns above the SARS threshold, upload your tourism levy registration. It signals a legitimate, accountable operation."* |
| adv_acc.fire | Fire clearance certificate | 4 | Upload | *"Upload your fire clearance certificate — it's a legal requirement for accommodation and guests look for it."* |
| adv_acc.hygiene_cert | Hygiene / TGCSA Safe Travels certification | 3 | Upload | *"Upload your TGCSA Safe Travels badge or equivalent hygiene certification — guests value this."* |
| adv_acc.award | AA Travel / TripAdvisor / Booking award | 3 | Upload | *"Upload a screenshot or certificate of any travel award you've received — AA, TripAdvisor, Booking.com. Social proof matters."* |

*Note: TGCSA chain — only the highest star rating earns points (replaces lower stars).*

---

### Collectors — Category Credentials (max 40 pts)

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| collectors.provenance | Item provenance documentation | 8 | Upload | *"Provenance is the chain of custody — where this item came from and who owned it. Upload an auction receipt, gallery invoice, or inheritance document. For high-value items, this is as important as authentication."* |
| collectors.auth_cert | Third-party authentication certificate | 6 | Upload | *"Upload an authentication certificate from a recognised third party — PSA or PCGS for cards and coins, GIA for gems, Beckett for sports memorabilia. I'll confirm the authenticator."* |
| collectors.dealer_reg | Dealer / reseller registration | 6 | Upload | *"Upload your dealer registration or gallery licence. Buyers need to know whether they're dealing with a registered dealer or a private collector — regulatory protections differ."* |
| collectors.tx_15plus | 15+ successful transactions | 6 | Auto | *"You've earned this automatically from your platform history — 6 points."* |
| collectors.tx_5_14 | 5–14 successful transactions | 6 | Auto | *"6 points earned automatically from your transaction history."* |
| collectors.tx_1_4 | 1–4 successful transactions | 8 | Auto | *"8 points earned automatically from your first 4 completed transactions."* |
| collectors.appraisal | Professional appraisal or valuation | 5 | Upload | *"Upload a professional appraisal or valuation document for this item. It gives buyers a price anchor and signals you've had the item independently assessed."* |
| collectors.insured_valuation | Insurance / valuation for high-value items | 4 | Upload | *"For items above a certain value, proof of insurance or a formal valuation adds significant credibility. Upload yours."* |
| collectors.assoc | Collector association membership | 2 | Upload | *"Upload your association membership — SA Numismatic Society, SA Philatelic Society, or any collector's guild. Even soft credentials matter."* |
| collectors.authenticity_guarantee | Authenticity guarantee declaration | 2 | Declare | *"Declare whether you offer a return if the item proves inauthentic. Buyers buying remotely look for this. One tap — it appears prominently on your listing."* |
| collectors.specialisation | Category specialisation declared | 4 | Declare | *"Tell buyers what you specialise in — coins, art, stamps, wine, vintage watches. One tap."* |

---

### Cars — Category Credentials (max 40 pts)

**Dealer/private gate applies — private sellers see ✳ signals only.**

| Signal ID | Signal | Pts | Evidence | AI coaching script | Seller type |
|-----------|--------|-----|----------|--------------------|-------------|
| cars.private_seller | Private seller declaration | 0 | Declare | *"Tell buyers you're a private seller. Consumer protection regulations differ from dealer sales — buyers need to know this upfront."* | Private only |
| cars.ownership | Vehicle ownership (NATIS papers) | 10 | Upload | *"Upload your NATIS registration papers. This proves you own the vehicle you're selling — it's the most important thing a car buyer looks for."* | Both ✳ |
| cars.dealer_reg | Dealer / trader registration | 8 | Upload | *"Upload your MIRA dealer registration or dealer licence. Buyers dealing with a registered dealer have different legal protections."* | Dealer only |
| cars.finance_clear | Finance clearance / no outstanding finance | 4 | Upload | *"Upload a letter from your bank or finance company confirming no outstanding balance on this vehicle. Without this, a buyer could unknowingly take on your debt after purchase."* | Both ✳ |
| cars.rwc | Roadworthy certificate (RWC) | 6 | Upload | *"Upload your roadworthy certificate. It's mandatory for change of ownership in SA — and buyers expect it before they'll consider making an offer."* | Both ✳ |
| cars.inspection | AA / independent vehicle inspection | 5 | Upload | *"Upload an AA or independent inspection report. A third-party inspection is the single most reassuring thing you can show a serious buyer."* | Both ✳ |
| cars.service_history | Service history on file | 4 | Upload | *"Upload your service book or dealer service records. Full service history significantly increases buyer confidence — and the asking price."* | Both ✳ |
| cars.safety_recall_clear | DEKRA / NRCS safety recall check | 3 | Upload | *"Upload a DEKRA or NRCS safety recall clearance. It takes 5 minutes to check — and shows buyers you've done your homework."* | Both ✳ |

---

### Local Market — Category Credentials (base score 40 pts, max category pts 40 pts additional)

*LM sellers start at 40 (Established tier). Every signal above builds further.*

| Signal ID | Signal | Pts | Evidence | AI coaching script |
|-----------|--------|-----|----------|--------------------|
| lm.product_type | Product type declaration | 1 | Declare | *"Tell me what you're selling — honey, beadwork, tutoring, repairs. One tap. It helps me give you more relevant advice."* |
| lm.assoc_role | Named role in association | 15 | Declare+Upload | *"A named role — chair, secretary, committee member — in a recognised association is the highest-value credential available to you here. Declare your role now for 12 points, then upload your appointment letter for the final 3."* |
| lm.prof_body | Association / professional body (1st) | 8 | Upload | *"Upload your membership certificate from SABI, NBA, SATMA, or any recognised guild or industry body."* |
| lm.provincial_role | Official government / regulatory appointment | 10 | Declare+Upload | *"A government or regulatory appointment is a very strong signal. Declare it now for 8 points — upload your appointment letter for the final 2."* |
| lm.prof_body_2 | Second association membership | 6 | Declare+Upload | *"A second professional body membership adds 5 points on declaration and 1 more with your membership card."* |
| lm.formal_cert | Formal qualification / diploma (1st) | 7 | Upload | *"Upload your highest formal qualification — diploma, certificate, or degree from a recognised institution."* |
| lm.food_safety | Food safety / hygiene certificate | 5 | Upload | *"You're selling food products — upload your Department of Health food handler certificate or home kitchen approval. Buyers of food expect this."* |
| lm.formal_cert_2 | Second relevant qualification | 5 | Upload | *"Upload a second qualification — it adds 5 more points."* |
| lm.business_reg | Business registration | 4 | Upload | *"Upload your CIPC registration or tax clearance certificate. It shows buyers you're a registered business, not just a hobbyist — a different level of accountability."* |
| lm.training_course | Formal training course (1st) | 4 | Upload | *"Any formal training course from a recognised provider earns 4 points. Upload your certificate."* |
| lm.formal_cert_3 | Third relevant qualification | 3 | Upload | *"Upload a third qualification — up to 3 are counted."* |
| lm.training_course_2 | Second training course | 3 | Upload | *"A second training course adds 3 more points."* |
| lm.experience_5yr | 5+ years relevant experience | 3 | Declare+Upload | *"Declare 5+ years of experience — 2 points immediately, 1 more with a CV upload."* |
| lm.id_ai_verified | Identity AI-verified | 5 | Auto | *"Your ID was verified automatically — 5 points awarded."* |
| lm.banking_name_match | Bank account holder name verified | 3 | Auto | *"Your bank account name matches your verified ID — 3 points."* |
| lm.cert_name_verified | Certificate name matches ID | 2 | Auto | *"The name on your uploaded certificate matches your verified ID — 2 points."* |
| lm.id_number_valid | ID / passport number validated | 2 | Auto | *"Your ID number has been validated — 2 points."* |
| lm.phone_verified | Phone number verified | 2 | Auto | *"Your phone number is verified via OTP — 2 points."* |
| lm.banking | Banking details on file | 2 | Auto | *"Banking details confirmed — 2 points."* |
| lm.experience_1yr | 1+ year relevant experience | 2 | Upload | *"Upload a document showing 1+ year of experience in what you're selling."* |
| lm.media_feature | Media feature / press coverage | 2 | Upload | *"Been featured in a magazine, newspaper, or online article? Upload it — 2 points."* |
| lm.product_guide | Product guide / recipe authored (1st) | 2 | Upload | *"Have you written a guide, recipe, or care instructions for your product? Upload it."* |
| lm.id_uploaded | Government ID uploaded | 2 | Upload | *"Upload your SA ID, passport, or driver's licence."* |
| lm.product_guide_2 | Second product guide | 1 | Upload | *"Upload a second original guide — up to 3 counted."* |
| lm.product_guide_3 | Third product guide | 1 | Upload | *"Upload a third guide."* |
| lm.social_proof | Active social media presence | 1 | Auto | *"Link your Instagram, Facebook, or website in your profile — 1 point."* |

---

## AI Behaviour Rules in the Trust Score Step

1. **The AI speaks in first person and directly addresses the seller.** Not generic documentation — conversational and specific to their category and sub-type.

2. **The AI surfaces the highest-value skippable signals first.** Within each group, signals are presented in descending point value so the seller sees the biggest gains upfront.

3. **Conditional signals appear dynamically.** food_safety only appears if product_type = food. clearance is surfaced prominently at the top if in_home_flag was declared in B3. PPRA/FFC/mandate only appear for registered agents. CIDB only for Technical services in ZA.

4. **The AI confirms or flags every upload.** Never silent. Always responds within 2 seconds of upload with what it saw and how many points were awarded — or what to try instead.

5. **The AI remembers what was skipped.** At the end of the Trust Score step, it summarises: *"You skipped [N] signals worth [X] points total. You can add these from your profile any time — I'll remind you when you log in."*

6. **Declaration always available as fallback.** For any declarable signal, if the seller doesn't have the document to hand, the declare option awards 80% of points immediately. The AI explains this explicitly: *"Don't have it handy? Declare it now for [X] points — upload the document later for the remaining [Y]."*

7. **Expiry tracking.** For any signal with an expiry date (PPRA, FFC, First Aid, insurance, fire clearance, RWC), the AI reads and stores the expiry. It warns if the document is within 60 days of expiry: *"Your FFC expires in 45 days — you'll need to renew it soon."*

---

## Listing Count Caps

| Tier | Fee | Max live listings | Fade Out |
|------|-----|-------------------|----------|
| Free | $0 | 2 | 30 days |
| Starter | $5/mo | 25 | 60 days |
| Premium | $15/mo | 50 | 120 days |

Batch expansion: +20 listings per 1T, stackable, persists until used.

---

## Open Build Items

- `POST /listings/expand-batch` endpoint — not yet in BEA
- 3 free AI sessions on registration — award in `POST /users`, not via `/dev/credit`
- AI description draft endpoint — needs BEA route or inline Haiku design
- Room-by-room photo prompt list built dynamically from B3 fields
- Conditional signal display in BEA — `product_type`, `in_home_flag`, `agent_type` must be stored on listing/user record to gate signal display
- Cars category — all signals are proposed, none yet in BEA
- Expiry date storage and warning logic for time-limited credentials

---

*Version 3.0 — definitive. Canonical reference for all sell flow, AI coaching, and Trust Score signal implementation. Architect agent sign-off required for any changes.*
