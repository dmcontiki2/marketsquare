# MarketSquare · Local Market — Requirements & Architecture
**Version 0.1 · 27 April 2026**
*Draft for review. Not yet approved for implementation.*

---

## 1 · Vision

The Local Market is a completely open-ended peer-to-peer trading category — a digital flea market where absolutely anything can be listed. Unlike the structured categories (Property, Tutors, Services, Adventures, Collectors), the Local Market has no category constraint. A seller may list a vintage lamp, a rare stamp, a second-hand bicycle, a handmade quilt, or a 1965 Ford Mustang — all on equal footing.

The Local Market is fully separated from all other categories. It has its own dedicated page, its own introduction flow, and its own Tuppence mechanic. It never appears in the main category grid and does not mix with structured category listings.

The Wishlist Feed (see `WISHLIST_REQUIREMENTS.md`) matches buyer wishlist signals against Local Market listings and surfaces them in the "For You" feed on the home screen bottom half — this is the primary discovery mechanism for Local Market items.

---

## 2 · Core Principles

| Principle | Rule |
|---|---|
| **Absolute openness** | Any legal item may be listed. No category constraint. The seller describes freely. |
| **Complete separation** | Local Market never appears in the main Browse grid. It has its own page and entry point. |
| **Seller skin in the game** | The seller pays 1T when a buyer submits an introduction request. This self-selects serious sellers and filters window-shopping buyers. |
| **Buyer accountability** | If a seller complains that an accepted buyer did not follow through, Trust Score points are deducted from the buyer. |
| **Credit not refund** | If a buyer ghosts and the seller complains, the seller receives a 1T Tuppence credit — not a cash refund — provided the listing remains active. |
| **Trust-gated discovery** | Buyers filter Local Market listings by minimum seller Trust Score. Higher trust = more serious seller. Sellers are encouraged to build their Trust Score for better visibility. |
| **Privacy is inviolable** | All anonymity rules apply equally to Local Market. Seller identity is never revealed until mutual introduction acceptance. |

---

## 3 · Tuppence Model (Local Market Only)

This is the only category where the **seller pays** on introduction. All other categories have the buyer pay on acceptance.

### Flow

```
Buyer submits introduction request
        │
        ▼
1T deducted from seller's Tuppence balance
(2T if the seller activated the boost option on this listing)
        │
        ▼
Seller notified — 48 hour response window
        │
        ├── Seller ACCEPTS → contact details exchanged
        │       No further Tuppence movement for this introduction
        │
        └── Seller IGNORES / DECLINES → introduction closes
                No refund to seller (seller chose not to engage)
```

### Buyer No-Show (Post-Acceptance)

```
Seller complains buyer did not follow through after acceptance
        │
        ▼
Platform reviews complaint (or auto-processes after threshold)
        │
        ▼
Buyer Trust Score −3 points (window-shopper penalty)
        │
        ▼
Seller receives 1T CREDIT (not cash) to Tuppence balance
        └── Only if listing remains active at time of complaint
```

### Rules

**LM-T1** — The seller pays 1T (or 2T if boosted) exactly once per listing, on the first accepted introduction request. Subsequent introduction requests on the same listing from different buyers do not incur additional Tuppence charges to the seller.

**LM-T2** — If the seller ignores or declines an introduction request, no Tuppence is refunded. The cost is the price of the notification.

**LM-T3** — Tuppence credit (not cash) is issued to the seller only when: (a) the seller files a no-show complaint, (b) the complaint is upheld, and (c) the listing is still active.

**LM-T4** — The buyer's Trust Score is reduced by 3 points per upheld no-show complaint. Repeat offenders will fall below the minimum Trust Score required to access Local Market, providing natural self-regulation.

**LM-T5** — All Tuppence movements are recorded in the existing `transactions` table with type `lm_intro_deduct` (seller) and `lm_credit` (seller credit on no-show) and `lm_boost_deduct` (if boosted).

---

## 4 · Introduction Flow (Local Market)

The Local Market uses the **Commitment model** — one active introduction at a time per listing, same as Property. The listing is not paused during the introduction window (unlike Property) — multiple buyers may queue.

```
COMMITMENT MODEL — LOCAL MARKET

Buyer views listing → submits introduction request
        │
        ▼
Buyer added to seller's introduction queue
        │
        ▼
1T deducted from seller on first queue entry
        │
        ▼
Seller notified (push + in-app) — 48 hour response window
        │
        ├── ACCEPTS within 48hrs → contact details exchanged
        │       Trust Score +3 (seller, for responding within 24hrs)
        │       Trust Score +3 (seller, for responding within 24hrs bonus)
        │
        ├── DECLINES → buyer notified · listing stays live
        │       No Trust Score penalty for decline
        │
        └── IGNORES 48hrs → introduction auto-closes
                Trust Score −1 (seller, for ignoring)
                Buyer notified — may resubmit after 7 days
```

**LM-F1** — Sellers who respond within 24 hours earn +3 Trust Score. This incentivises fast response and rewards active sellers.

**LM-F2** — Sellers who ignore introductions lose −1 Trust Score per ignored request. Accumulated ignores will drop a seller below the visibility threshold for high-trust buyers.

**LM-F3** — A buyer may not submit a second introduction to the same listing within 7 days of a decline or auto-close.

**LM-F4** — There is no limit on the number of buyers who may queue on a single listing simultaneously. The seller works through the queue in order.

---

## 5 · Product Requirements

### 5.1 Dedicated Local Market Page

**LM-01** — The Local Market has its own dedicated page, accessible from a "Local Market" entry on the Browse page and from the main navigation.

**LM-02** — The page displays a grid of Local Market listings, filterable by: city, suburb, price range, and minimum seller Trust Score.

**LM-03** — There is no category filter on the Local Market page. Listings are open-ended. Search is free-text, matched by the Haiko semantic engine (same as Wishlist matching).

**LM-04** — Each listing card shows: item photo(s), title, price, suburb, seller Trust Score badge, time listed, and view count. No seller identity shown.

**LM-05** — Tapping a card opens the Local Market listing detail page — separate from the standard listing detail view used by other categories.

---

### 5.2 Listing Creation (Seller)

**LM-06** — A seller creates a Local Market listing via the admin tool. Required fields: title, description, price (or "Make an offer"), at least one photo, suburb, city.

**LM-07** — No category field. The seller describes the item freely. The AI (Haiko) extracts tags at publish time for matching — these are internal only, never shown to the seller or buyer.

**LM-08** — The seller must have a minimum Trust Score of 30 to publish a Local Market listing. Below this threshold, the app prompts the seller to complete their profile and earn more Trust Score points before listing.

**LM-09** — On publish, the seller is shown: "Your listing is live. You will pay 1 Tuppence when your first buyer expresses interest. Build your Trust Score to attract more serious buyers."

**LM-10** — The seller may activate a 2T boost at listing creation or at any time after. Boost effect: expanded matching tolerance and global reach in the Wishlist Feed (same boost rules as per WISHLIST_REQUIREMENTS.md PR-38 to PR-44).

---

### 5.3 Trust Score Integration

**LM-11** — Buyers may filter Local Market listings by minimum seller Trust Score. Presets: Any (≥0) · Established (≥40) · Trusted (≥70) · Highly Trusted (≥90).

**LM-12** — The Local Market page displays a prominent trust guidance message: *"Filter by Trust Score to find serious sellers. Highly Trusted sellers have verified ID, phone, and a strong track record."*

**LM-13** — When a seller views their Local Market listing in the admin tool, they see: their current Trust Score, their Trust Score tier, and a Haiko-generated tip on the single highest-impact action they can take to increase it.

**LM-14** — Sellers below Trust Score 40 (New tier) are shown a warning on their listing: *"Your listing is visible but buyers filtering for Established sellers or above will not see it. Complete your profile to improve your reach."*

---

### 5.3a Trust Score Enforcement — Bad Actor Suspension

**LM-14a** — If a seller's Trust Score drops below 30 at any time (due to penalties, complaints, or ignored introductions), all their Local Market listings are **automatically suspended** — hidden from all buyers and the wishlist feed immediately. The seller sees their listings in the admin tool marked "Suspended — Trust Score too low."

**LM-14b** — A suspended seller's Tuppence balance is **frozen but not forfeited**. Purchased Tuppence is never confiscated — it was bought with real money. The balance is restored in full when the seller restores their Trust Score above 30.

**LM-14c** — The admin tool shows the suspended seller a clear recovery path: their current score, the minimum required (30), and the exact actions — with point values — that will restore their access. Haiko provides the guidance message.

**LM-14d** — When a seller restores their Trust Score to 30 or above, their suspended listings are **automatically reactivated** with no manual intervention required.

**LM-14e** — **Repeat offender escalation:**
- First suspension: listings suspended until score restored. No time limit.
- Second suspension within 90 days: Local Market access suspended for a mandatory 30-day cooling-off period, regardless of Trust Score recovery during that period.
- Third suspension (any timeframe): **permanent ban from Local Market**. Other categories (Property, Tutors, Services etc.) are unaffected. Tuppence balance remains accessible for use in other categories.

**LM-14f** — The repeat offender rules and Tuppence freeze/restoration policy are disclosed in the EULA at registration and must be re-confirmed when a seller first activates a Local Market listing. See Section 11 (EULA Requirements).

---

### 5.4 Buyer Trust Score & Accountability

**LM-15** — Buyers who submit introduction requests on Local Market listings must have a minimum Trust Score of 20. Below this, they are prompted to verify their email and phone number first.

**LM-16** — A no-show complaint by a seller, once upheld, deducts 3 Trust Score points from the buyer.

**LM-17** — A buyer whose Trust Score falls below 20 as a result of no-show complaints is automatically blocked from submitting Local Market introduction requests until they restore their score.

**LM-18** — Buyers can see their own Local Market introduction history in the Tuppence Wallet / My Activity screen.

---

### 5.5 Home Page & Navigation Changes

**LM-19** — The stats row on the home page (seller count / listings / Tuppence / intros) is **removed permanently** to make space for the "For You" wishlist feed in the bottom half.

**LM-20** — The Browse page includes a "Local Market" banner/button as a distinct entry point — visually separated from the structured category grid. Tapping it navigates to the dedicated Local Market page.

**LM-21** — The "For You" feed on the home page bottom half matches buyer wishlist signals against both structured category listings AND Local Market listings. They are visually distinguished in the feed — Local Market cards carry a "Local Market" badge.

---

### 5.6 Wishlist Integration

**LM-22** — The Wishlist add screen uses free-text input only — no category dropdown. The buyer describes what they want in their own words. Haiko extracts intent and matches against all listing types including Local Market.

**LM-23** — When a wishlist match comes from a Local Market listing, the feed card is badged "Local Market" and tapping it goes to the Local Market listing detail page, not the standard detail view.

**LM-24** — Wishlist matching for Local Market uses the same semantic engine and Trust Score gate as defined in WISHLIST_REQUIREMENTS.md. The buyer's Trust Score filter applies equally to Local Market matches.

---

### 5.7 Tuppence Wallet Updates

**LM-25** — The Tuppence Wallet screen shows Local Market transactions separately, labelled: "Local Market intro fee", "Local Market boost", "Local Market credit (no-show)".

**LM-26** — The wallet summary shows the buyer's current Trust Score and a short status message: "Your Trust Score is 47 — Established. Sellers respond well to buyers at this level."

---

### 5.8 Admin Tool Updates

**LM-27** — "My Listings" in the admin tool shows all categories including Local Market. Local Market listings are displayed in a separate tab or clearly badged section.

**LM-28** — The Local Market listing creation form in the admin tool includes: title, description, price, photo upload (up to 5 photos), suburb, city — and no category selector.

**LM-29** — "Who is the Seller" profile page includes a country selector. Country is required for Local Market listings to support geographic filtering in the wishlist feed.

**LM-30** — The admin tool Local Market section shows the seller's Trust Score prominently with the Haiko improvement tip (see LM-13).

---

## 6 · Data Model

### 6.1 New / Modified Fields

```sql
-- Local Market listings use the existing listings table
-- with category = 'local_market' as the discriminator
-- No other schema changes needed for the listing itself

-- New transaction types for existing transactions table:
-- type = 'lm_intro_deduct'   — seller pays 1T on first intro
-- type = 'lm_boost_deduct'   — seller pays 2T on boosted intro
-- type = 'lm_credit'         — seller credit on upheld no-show complaint

-- New table: Local Market no-show complaints
CREATE TABLE lm_complaints (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id      INTEGER NOT NULL,
    seller_email    TEXT NOT NULL,
    buyer_token     TEXT NOT NULL,
    intro_id        INTEGER NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',  -- 'pending' | 'upheld' | 'dismissed'
    filed_at        TEXT NOT NULL DEFAULT (datetime('now')),
    resolved_at     TEXT,
    credit_issued   INTEGER DEFAULT 0   -- 1 once credit has been applied
);

-- New column on existing introductions table (or equivalent):
-- intro_type TEXT DEFAULT 'standard'  -- 'standard' | 'local_market'
-- This distinguishes Local Market intros (seller pays) from standard intros (buyer pays)
```

---

## 7 · System Flow Summary

```
SELLER CREATES LOCAL MARKET LISTING
        │
        ▼
Trust Score ≥ 30 gate → listing published
Haiko extracts tags (internal) → wishlist matching enabled
        │
        ▼
Listing appears on Local Market page + Wishlist "For You" feed


BUYER FINDS LISTING (browse or wishlist feed)
        │
        ▼
Buyer Trust Score ≥ 20 gate → intro request submitted
        │
        ▼
1T deducted from SELLER (first intro on this listing only)
Seller notified — 48hr window
        │
        ├── ACCEPTS (ideally <24hrs → +3 Trust Score)
        │       Contact exchanged · deal happens offline
        │
        ├── DECLINES → buyer notified · no refund · listing stays live
        │
        └── IGNORES 48hrs → auto-close · seller −1 Trust Score


POST-DEAL: BUYER NO-SHOW
        │
        ▼
Seller files complaint
        │
        ▼
Complaint upheld → buyer −3 Trust Score
Seller receives 1T credit (if listing still active)
```

---

## 8 · Agent Responsibilities

| Component | Agent | Notes |
|---|---|---|
| Local Market page UI | Frontend agent | Dedicated page, separate from main Browse |
| Listing creation form | Admin agent | No category field, photo upload, suburb/city/country |
| Trust Score gate (publish) | BEA / Architect agent | Min score 30 to publish |
| Trust Score gate (intro) | BEA / Architect agent | Min score 20 to submit intro |
| Tuppence deduction (seller) | BEA / Architect agent | 1T on first intro, type=lm_intro_deduct |
| No-show complaint flow | BEA / Architect agent | lm_complaints table, credit on uphold |
| Haiko tag extraction | Haiko agent socket | Internal tags for wishlist matching |
| Wishlist feed integration | Frontend agent | Local Market badge on feed cards |
| Wallet display | Frontend agent | Local Market transactions labelled separately |
| Admin My Listings | Admin agent | All categories + Local Market tab |
| Country selector | Admin agent | Required on seller profile |
| Stats row removal | Frontend agent | Home page — permanent removal |
| Browse entry point | Frontend agent | Local Market banner on Browse page |

---

## 9 · Geo Bug — City Selector Not Propagating

**Separate fix required (not part of Local Market build):**

The city/country selector in the top-right of the buyer app does not correctly propagate the selected city to all API calls and display fields. Some views retain "Pretoria" after switching cities. Root cause: some API calls and display fields read from a hardcoded default or stale variable instead of `activeCity` dynamically.

Fix: audit every reference to city name and city ID in `marketsquare.html` and ensure all consume `activeCity.name` / `activeCity.id` from the live app state. This fix should be delivered as a standalone commit before or alongside the Local Market build.

---

## 10 · Out of Scope (V1)

- Local Market sub-categories or tags visible to buyers (internal only)
- Seller-initiated price reduction notifications to interested buyers
- Group / bulk listings (multiple items in one listing)
- Local Market escrow or payment processing (deal happens offline)
- Automated complaint resolution (V1 = manual review by David)

---

## 11 · EULA Requirements

The following clauses must appear in the MarketSquare End User Licence Agreement and Terms of Service. They must be displayed and explicitly re-confirmed by the seller when they first activate a Local Market listing.

### 11.1 Tuppence as Non-Refundable Platform Currency

Tuppence is a platform introduction currency purchased with real money. Tuppence balances are non-refundable in cash under any circumstances. Tuppence may be suspended (frozen) if a seller's account is suspended due to Trust Score violations, but is never forfeited. Frozen Tuppence is restored automatically when the account is reinstated.

### 11.2 Trust Score Minimum & Listing Suspension

To publish and maintain an active Local Market listing, a seller must maintain a minimum Trust Score of 30. If a seller's Trust Score falls below 30 at any time, all Local Market listings are automatically suspended without notice. Listings are automatically reactivated when the Trust Score is restored to 30 or above.

### 11.3 Repeat Offender Policy

MarketSquare operates a three-strike escalation policy for Trust Score violations in the Local Market:

- **First suspension:** Listings suspended until Trust Score restored. No time limit.
- **Second suspension within 90 days:** Mandatory 30-day cooling-off period. Local Market access remains suspended for the full 30 days regardless of Trust Score recovery.
- **Third suspension:** Permanent ban from the Local Market. Other platform categories remain accessible. Tuppence balance remains accessible for use in other categories.

MarketSquare reserves the right to apply these measures without prior notice where Trust Score thresholds are breached.

### 11.4 Buyer No-Show Accountability

By submitting an introduction request on a Local Market listing, the buyer acknowledges that failing to follow through on an accepted introduction may result in a Trust Score penalty of −3 points per upheld complaint. A Trust Score below 20 will result in suspension from submitting Local Market introduction requests until the score is restored.

### 11.5 Seller Pays on Introduction

In the Local Market category only, the seller's Tuppence balance is debited by 1 Tuppence (or 2 Tuppence if a boost is active) when a buyer submits the first introduction request on a listing. This deduction is non-refundable if the seller declines or ignores the introduction. A 1 Tuppence credit is issued to the seller if a buyer no-show complaint is upheld and the listing remains active at the time of resolution.

### 11.6 EULA Update Process

These terms may be updated by MarketSquare with 14 days notice via in-app notification. Continued use of the Local Market after the notice period constitutes acceptance of the updated terms.

---

## 12 · Out of Scope (V1)

- Local Market sub-categories or tags visible to buyers (internal only)
- Seller-initiated price reduction notifications to interested buyers
- Group / bulk listings (multiple items in one listing)
- Local Market escrow or payment processing (deal happens offline)
- Automated complaint resolution (V1 = manual review by David)

---

*End of LOCAL_MARKET_REQUIREMENTS.md v0.1. Ready for review before implementation.*
