# Golden Listing Tier — Future Design Specification

**Status:** 🔵 **PLANNED FUTURE DESIGN — NOT SCHEDULED.** No build date. Touches nothing live. To be reviewed after launch.
**Type:** Post-launch monetisation / premium production tier
**Owner:** David
**Drafted:** 26 July 2026 (David + Claude)
**Related:** `LAUNCH_HARDENING_DECISION_2026-07-25.md` · `ROADMAP_MASTER.md`

---

## 1. One-line summary

A premium, **opt-in** upgrade at listing creation that buys an operator a more beautifully produced listing — richer copy, cinematic motion from their **own** photos, and the interactive route map — at a cost above the base 5T, **without ever touching Trust Score, Listing Quality, or Ranking.**

## 2. The Bright Line (non-negotiable)

> **Money buys production quality. Money never buys trust — not the Trust Score, not Listing Quality, not Ranking, and not the *appearance* of trust.**

Every decision in this spec serves that line. If a proposed feature would let a paying operator appear more trustworthy, or rank higher, than an honest non-paying one, it is out — no exceptions.

## 3. Why (problem / opportunity)

- TrustSquare already lets operators spend **5T** to generate a listing. Serious operators (higher-value tours, property, premium adventures) will want a listing that looks like a real agency made it.
- A premium **production** tier funds the platform and the trust infrastructure **without** compromising the trust signal — provided the bright line holds.
- The interactive **route map** (already built) is a genuinely differentiated hook nobody else offers.

## 4. Goals

- Let operators make a **materially better-produced** listing from their **own real assets**.
- Create an **honest revenue stream** that covers premium generation + motion costs and contributes margin.
- Do it so it **reinforces** trust (real operators showcasing real assets well) rather than eroding it.
- Keep the surface **clean** — no new badges, no clutter.

## 5. Non-Goals

- **Not** a visibility or ranking product. Golden buys nothing in search, placement, or trust.
- **Not** a verification tier. It says nothing about who the operator is or whether they are trustworthy.
- **Not** an AI-imagery product for real listings (AI imagery stays demo-only — see §8).
- **Not** a badge or label on the public listing.
- **Not** time-scheduled. This is design intent, not a committed build.

## 6. The Three Locks (product decisions — final)

1. **Trust untouched.** Golden never touches or depreciates Trust Score, Listing Quality, or the Ranking List. A phone-photo listing with a higher score always out-ranks a Golden listing with a lower one.
2. **No badge.** Nothing on the live listing announces Golden. Quality speaks for itself. *(Badges breed clutter/kitsch, and a "premium" mark is precisely how money would leak into the perception of trust.)*
3. **Sold as features-with-a-cost; never "AI".** Marketed as "a richer listing with more features, at a cost." Never name AI models; never use the word "AI" in the pitch. The customer buys the **outcome**, not the plumbing.

## 7. Surface / UX model

- Golden is an **opt-in choice in the create flow** (the 5T step): the operator chooses **Standard** or **Golden** and pays above the base.
- It is **seller-visible** (the person deciding) and **buyer-invisible** (the person judging). The buyer simply sees a better listing — never a label explaining why.
- This is the no-badge principle expressed end to end.

## 8. Honesty constraints (critical — as binding as the Bright Line)

- **Real listings use the operator's own real photos only.** AI-generated imagery remains **demo-only** and is always marked **"demo advert."**
- **Single-image 360 / orbit fabricates the unseen sides — even of a real property.** On real listings, motion is restricted to **non-fabricating moves**: cinematic push-in, parallax drift, pan across what is genuinely in frame.
- **A true 360 of a real place requires the operator's multiple real photos or a real walk-around video** — never a single-image AI orbit.
- **Real heritage / public sites** (e.g. Stonehenge) use **real footage or a real 3D scan**, never AI-invented views.

## 9. What Golden includes (feature set)

**P0 — defines the tier:**
- Higher-quality generated **copy** (best available generation; unnamed).
- **Cinematic motion from the operator's own real photos**, within the honesty constraints (§8).
- The **interactive journey / route map.**

**P1 — nice-to-have:**
- Extra photo slots / richer detail-page layout.
- A short produced "hero" clip assembled from their real media.

**P2 — future / architectural insurance:**
- True multi-photo 360 of the operator's real place.
- Real-footage / 3D-scan integration for heritage tours.

**Acceptance criteria (illustrative):**
- *Given* an operator at the create step, *when* they select Golden and pay, *then* the listing is produced with the Golden feature set and **no change occurs to its Trust Score, Listing Quality, or Ranking.**
- *Given* a Golden listing on the public feed, *when* a buyer views it, *then* **no badge, label, or trust-implying mark** distinguishes it from a Standard listing.
- *Given* a real listing, *when* motion is applied, *then* only non-fabricating moves are used and **no AI-invented imagery** appears (AI imagery only ever on demo listings, marked "demo advert").

## 10. Out of scope / must-nevers

- Never sell Trust Score, Listing Quality, ranking, placement, verification, or the appearance of any of them.
- Never put a Golden badge/label on a live listing.
- Never name an AI model or use "AI" in the customer-facing pitch.
- Never apply AI-generated imagery to a real (non-demo) listing.
- Never use a single-image 360 / orbit on a real property.

## 11. Success signals (if / when built)

**Leading:** Golden **attach rate** at the create step · operator satisfaction with produced listings.
**Lagging:** incremental revenue / margin from the tier · retention of Golden operators.

**🛡️ Guard metric (must-hold):** **Trust/ranking fairness does NOT move.** Non-paying listings with higher trust continue to out-rank Golden listings with lower trust, measured directly. If Golden ever correlates with a ranking advantage, the tier is considered broken and pauses until fixed.

## 12. Prioritisation & phasing

- **Now (architecture-aware, no monetisation):** the maps + motion capability already exist; keep building so they *could* support Golden without rework.
- **Post-launch (monetise):** only after the base free/5T experience is proven to convert and engage. Charging a premium before the base works is solving the wrong problem first.
- **Not time-scheduled.** This document is design intent; it acquires a date only when explicitly promoted onto the roadmap.

## 13. Cheapest validation (before building any billing)

- Give **2–3 founding operators the full Golden treatment for free** — polished copy + real-photo motion + route map — placed beside their Standard listing.
- Ask those operators, and a handful of buyers, **what it is worth.**
- This surfaces the riskiest assumption before a line of billing code is written.

## 14. Riskiest assumption

Not "will it look good" (it will). It is: **will operators pay a meaningful premium for production quality, versus just uploading their own decent photos?** §13 is the test.

## 15. Open questions

- **Pricing:** flat add-on above 5T, or tiered by feature? *(David)*
- **Lifecycle:** one-time at creation, or does Golden expire / need refreshing? *(David / eng)*
- **Motion safelist:** which real-media motions are safe-by-default vs need review? *(design + trust)*
- **Pipeline & cost:** where does produced motion live technically, and what is the cost per listing? *(eng)*
- **Consent:** do founding-operator free showcases need recorded consent / usage terms? *(David)*

---

*This is a planned future design. It changes nothing live and carries no build commitment until explicitly promoted onto the roadmap with a date.*
