# Sign-off needed — EULA wording + onboarding AI choice
**For David · 10 June 2026 · nothing deployed; this is for your approval before any live legal change.**

Two parts: **(1)** the exact EULA wording changes (live legal text — your sign-off, and counsel on the flagged items), and **(2)** the precise #5 onboarding change (surface the AI choice) for your OK before I touch the working flow.

---

## PART 1 — EULA markup (file: `eula_clean.html` / `eula_raw.html`, served live)

### A · Charge model → HOLD (CC-001)

**A1 · "Introduction" definition (line 172)**
- *Current:* "A buyer-initiated connection request to a Seller, **charged at 1 Tuppence, which — if accepted —** reveals both parties' contact details to each other."
- *Proposed:* "A buyer-initiated connection request to a Seller. **1 Tuppence is committed (held) when the Buyer makes the request and is burned only when the introduction is delivered** — i.e. when the Seller accepts, revealing both parties' contact details. **If the Seller declines or the request expires, the hold is released in full and no Tuppence is used.**"

**A2 · Tuppence definition (line 176, part i)**
- *Current:* "Introduction Tuppence — the mandatory fee paid by Buyers per Introduction"
- *Proposed:* "Introduction Tuppence — the fee paid by the Buyer for an Introduction, **committed on request and burned only on delivery (Seller acceptance); released if declined or expired**"

**A3 · ECT Act §44 (line 449)** ⚠ COUNSEL
- *Current:* "Once the Seller accepts… that service is complete… **The 1T charged at that moment** is the fee for that completed service and is not subject to reversal…"
- *Proposed:* "The 1 Tuppence is **committed (held) when the Buyer requests** the Introduction and is **burned at the moment the service is delivered** (Seller acceptance). That burned Tuppence is the fee for the completed service and is not subject to reversal under ECT Act §44. **Until delivery the Tuppence is only held, not spent.**"
- *Counsel:* confirm the §44 reasoning still holds under a hold-then-burn model.

**A4 · Withdraw-before-accept (line 451)**
- *Current:* "No Tuppence has been deducted at that point and no charge arises."
- *Proposed:* "**Only a hold was placed; it is released in full and no Tuppence is burned.**"

**A5 · Earned/final (line 454)**
- *Current:* "TrustSquare's Introduction fee is earned and **final on Seller acceptance**."
- *Proposed:* "…earned and **final on delivery (Seller acceptance); the hold is burned at that point. Before delivery it is only held, and is released if declined or expired.**"

**A6 · Fee disclosure 6.1 (line 511)**
- *Current:* "1T (USD $2) per Introduction, **charged to the Buyer's balance only upon Seller acceptance**… No charge arises on submission, decline, or non-response"
- *Proposed:* "1T (USD $2) per Introduction — **committed (held) on the Buyer's balance when the request is made and burned only on Seller acceptance (delivery). The hold is released on decline, expiry or non-response — no Tuppence is burned in those cases.**"

> Note: a §5.7 "Tuppence Holds and Reversals" already exists but is about **fraud/error** holds (operational) — different from the charge-model hold above. Keep both; they're distinct.

### B · AI model → free in-app guidance + per-use, capped 5T (CC-002)

**B1 · Tuppence definition (line 176, part ii)**
- *Current:* "AI Feature Tuppence — an optional, **subscription-gated** fee paid by **Sellers**… cost-recovery for an external AI API."
- *Proposed:* "AI Feature Tuppence — an optional **per-use** fee for advanced AI features. **Everyday in-app AI guidance is free; advanced features are priced per use in Tuppence, capped (Free / 2T / 3T / 5T). Available to Buyers and Sellers.**"

**B2 · AdvertAgent / AI Feature definition (line 180)**
- *Current:* "Seller-facing only. **Accessed via paid subscription.** Charged in AI Feature Tuppence. **Pricing TBD.**"
- *Proposed:* "AI-assisted support for listings, research and reports. **Everyday in-app guidance is free; advanced features are priced per use in Tuppence (Free / 2T / 3T / 5T), shown before you use them. Available to Buyers and Sellers.**"

**B3 · §5.5 table (lines 464–485)**
- *Who it applies to:* "Sellers only" → "**Buyers and Sellers** (some features are buyer-side — area/price research; some seller-side — listing help)."
- *Access model:* "paid Seller subscription tier… quota…" → "**Everyday AI guidance is free. Advanced features are pay-per-use from your Tuppence balance (capped 5T); the price is shown before you confirm. No subscription required.**"
- *Pricing (was TBD):* "**Per use, in Tuppence, capped: Free / 2T / 3T / 5T. Disclosed at the point of use.**"
- *Refunds:* "non-refundable once submitted" → "**A hold is placed when you start a paid AI feature and is burned on delivery; if the run fails, the hold is released and no Tuppence is used. Once a result is delivered, the Tuppence is non-refundable.**" (matches the live AI hold-on-request → burn-on-delivery → release-on-failure behaviour)

**B4 · "Why Tuppence is charged" (line 473) + §5.5 cost-recovery + 6.1/6.2 + line 517** ⚠ DAVID + COUNSEL
- *Current:* "powered by an external AI API (**currently Anthropic Claude**)… **cost-recovery… not platform revenue**."
- *Decision needed:* under the Simpler Model, advanced AI is part of the **revenue** engine, not pure cost-recovery. Do we (a) keep the cost-recovery framing (regulatory comfort) or (b) reframe advanced AI as a priced service? And replace "currently Anthropic Claude" with "**an external AI provider**" (AI-independence)? This changes the regulatory classification paragraph — your + counsel's call.

**B5 · "Pricing TBD" everywhere** → replaced with the capped per-use ladder above. (No more TBD.)

### C · Version
Bump the EULA version (top table) to the new version when landed; record the change in the version history row.

**⚠ Counsel-sensitive (do not finalise without counsel):** A3 (ECT §44 under hold), B4 (AI cost-recovery vs revenue classification), and the existing `[COUNSEL REQUIRED]` Collectors section.

---

## PART 2 — #5 onboarding: surface the AI choice (your OK before I edit the working flow)

**Finding:** the live photo-first "guided" flow (`guided-onboard`, steps b1–b8) already AI-drafts the description at **step b4** — that's why your Kor Haven description was AI-written. The gaps: (i) the AI is **silent** (no clear "this was AI-drafted, free" signal or paid upgrade), and (ii) a **returning seller** tapping Sell gets a sheet that can route past the "Start with a photo" choice.

**Proposed minimal change (non-breaking, flag-gated):**
1. **Step b4 (description draft):** add a clear line — "✦ **AI drafted this for you — free.** Edit anything." — so the free AI is visible, not silent.
2. **Optional paid upgrade at b4 / on the listing:** a subtle link — "Want a deeper paid analysis? **Property Area Dossier · from 3T**" (Cars → Car Dossier) — i.e. surface the **free glimpse / paid deep-dive** (Build B) at the natural point. Hidden unless a dossier exists for that category.
3. **Sell sheet (returning seller):** make "Start with a photo (AI)" the clear primary option so no one bypasses it.

All three are FEA-only, additive, behind a feature check, and don't change the working draft/publish path. I'll show you the rendered change before deploy.

---

## What I need from you
1. **EULA:** approve the A-series + B-series wording (and decide B4 — cost-recovery vs revenue, provider naming). Counsel on A3/B4/Collectors. Then I stage `eula_clean/raw.html` + the in-app EULA box and deploy on your go.
2. **#5:** OK the 3-point onboarding change (or adjust), then I implement + show you, then deploy.
