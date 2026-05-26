# MarketSquare · Wishlist Feed — Requirements & Architecture
**Version 0.2 · 26 April 2026**
*Open questions resolved. Ready for implementation review.*

---

## 1 · Vision

Transform MarketSquare from a **pull marketplace** (buyer goes looking) into a **push marketplace** (platform hunts on the buyer's behalf).

A buyer's search history and browsing behaviour passively builds a personal wishlist. The moment a matching listing appears anywhere on the platform, it surfaces in a **live scroll feed** on the bottom half of the MarketSquare home screen — and pings the buyer's connected wearable device.

The feature requires zero extra setup from the buyer. Their intent is already captured in how they use the app.

### First Impression — Empty State Showcase
When a visitor opens the app for the first time with no wishlist signals yet, the bottom half does not show a blank screen or a prompt. It runs a curated **showcase scroll** of the most aspirational listings on the platform — gold coins, Rolex watches, rare and expensive collectors cards, high-value Adventures experiences. This is the wow factor. It tells a first-time visitor immediately: *this is where serious items live.* The showcase is editorially curated and updated manually by David. It transitions seamlessly to the personalised wishlist feed once the buyer has 3+ signals.

---

## 2 · Core Principles

| Principle | Rule |
|---|---|
| **Privacy is inviolable** | User search history and wishlist data is never sold, shared, or used for advertising. It exists solely to serve that user. |
| **No data leaves the vault** | Matching runs server-side anonymously. Sellers and third parties never see who matched their listing or why. |
| **Zero friction onboarding** | Browsing automatically builds the wishlist. No manual "save this search" required. |
| **One ping per item** | A wearable notification fires once per matched listing, not once per category match. Prevents notification fatigue. |
| **Tuppence-aligned** | Boost mechanics use Tuppence, not advertising spend. Intent stays clean. |
| **Trust-gated matching** | Buyers may filter their wishlist feed by seller Trust Score. High-trust filtering is a first-class feature, not a hidden setting. |

---

## 3 · Product Requirements

### 3.1 Wishlist Engine

**PR-01** — The system must capture and store each buyer's search terms, category filters, suburb filters, and listing views as implicit wishlist signals.

**PR-02** — A buyer may also add explicit wishlist items: a free-text description of what they are looking for, with optional category, suburb, price range, and minimum seller Trust Score.

**PR-03** — Implicit signals (browsing) and explicit signals (saved searches) are weighted separately. Explicit intent carries higher matching weight (weight=2.0 vs 1.0).

**PR-04** — Wishlist data is stored against an anonymous buyer identifier. It is never linked to name, email, or phone in any external-facing query.

**PR-05** — A buyer can view, edit, and delete their own wishlist items at any time. Deletion is permanent and immediate.

**PR-06** — Wishlist data is retained for 90 days of inactivity, then purged automatically.

---

### 3.2 Trust Score Filter

**PR-07** — Every wishlist signal (explicit and implicit) may carry a minimum Trust Score threshold. The buyer sets this as a slider or preset:
- **Any seller** — no Trust Score filter (default)
- **Established +** — Trust Score ≥ 40 (blue badge)
- **Trusted +** — Trust Score ≥ 70 (green badge)
- **Highly Trusted** — Trust Score ≥ 90 (gold badge) — *recommended for high-value items*

**PR-08** — The matching engine excludes listings from sellers who do not meet the buyer's Trust Score threshold for that wishlist signal. A listing that matches on category and keywords but fails the Trust Score gate does not appear in the feed.

**PR-09** — Trust Score filtering applies to both the personalised wishlist feed and to wearable pings. A buyer who sets ≥ 90 will only be pinged for gold-badge sellers. This is the primary safety and assurance mechanism.

**PR-10** — The Trust Score threshold is displayed on each wishlist signal card in the buyer's settings: "Showing sellers rated Highly Trusted (90+) only."

---

### 3.3 Matching Engine

**PR-11** — When a new listing is published, the matching engine runs within 60 seconds and identifies all buyers with a wishlist signal that matches the listing.

**PR-12** — Matching is semantic, not keyword-only. "Red bicycle" must match "crimson bike, 21-speed." The Haiko agent socket handles intent extraction and fuzzy matching. Fallback when Haiko is unavailable: keyword overlap scoring (exact and stemmed token match, scored 0–100).

**PR-13** — Match confidence is scored 0–100. Only matches scoring ≥ 60 surface in the feed. Only matches scoring ≥ 80 trigger a wearable ping.

**PR-14** — The matching engine runs as a background job. It must not block listing publish or degrade API response time.

**PR-15** — Match results are stored per buyer as a queue. The queue is consumed by the scroll feed in reverse-chronological order (newest match first).

---

### 3.4 Subscription Tiers & Geographic Reach

**PR-16** — The wishlist feed is available to all registered users (free sign-on required — see PR-28). Geographic reach of matching is gated by subscription tier:

| Tier | Price | Wishlist Feed Reach |
|---|---|---|
| **Free** | $0 | National — matches listings within the buyer's country only |
| **Global** | $5/month | Global — matches listings across all cities and countries on the platform |

**PR-17** — Free tier buyers see a subtle prompt at the top of their feed when a match exists outside their country: *"There are matching listings in [Country] — upgrade to Global to see them."* This is the primary upgrade incentive for this feature.

**PR-18** — Global tier ($5/month) is a standalone wishlist subscription, separate from the existing Starter/Premium listing tiers. A buyer may hold both a Global wishlist subscription and a listing-access subscription independently.

**PR-19** — Tuppence boost (PR-34) benefits from Global tier: a seller who boosts reaches matched buyers globally, not just nationally. This makes the boost significantly more valuable and justifies the 2T price point.

*Cost model impact: Global tier at $5/month adds a new revenue stream. Impact to be quantified in Cost_Breakdown_GlobalLaunch.xlsx when subscription is activated.*

---

### 3.5 Free Sign-On & Trust Score Onboarding

**PR-20** — Access to the wishlist feed requires a free account registration. Unauthenticated visitors see the showcase scroll (Section 1) only.

**PR-21** — On registration, the buyer is assigned a buyer_token and their Trust Score journey begins immediately. The AI onboarding coach (Haiko) guides the new user through trust-building steps in order of impact:

| Step | Trust Score Bonus | Required for |
|---|---|---|
| Verify email address | +5 pts | Account activation |
| Add phone number | +8 pts | Optional — bonus only |
| Upload ID document | +12 pts | Optional — bonus, stored encrypted |
| Add banking details | +5 pts | Optional — required later for payments; adds bonus now |
| Complete profile (photo, bio) | +5 pts | Optional — bonus only |

**PR-22** — Banking details are collected for future payment flows (Paystack) but are never required at registration. Collecting early earns bonus Trust Score points as an incentive. The UI is explicit: *"Adding your banking details now earns you 5 trust points and means you're ready to transact when the moment comes."*

**PR-23** — The AI coach (Haiko) provides personalised advice on maximising Trust Score: *"You're at 18 points. Adding your phone number and ID would take you to Established tier — sellers will respond faster to buyers with verified identities."*

**PR-24** — Trust Score progress for buyers is displayed as a simple progress bar in their profile. The four tier thresholds are shown (New / Established / Trusted / Highly Trusted) so the buyer always knows their next milestone.

**PR-25** — A buyer's Trust Score is visible to sellers at the moment of an introduction request. A Highly Trusted buyer is a stronger signal of serious intent — sellers may prioritise these introductions. This creates a natural flywheel: buyers who invest in their Trust Score get better seller response rates.

---

### 3.6 Scroll Feed (Bottom Half — Home Screen)

**PR-26** — The bottom half of the MarketSquare home screen is reserved for the wishlist scroll feed. It renders as a continuous horizontal scroll of matched listing cards (visual, image-forward).

**PR-27** — **Empty state (new visitor / no signals):** Runs a curated showcase scroll of the most aspirational listings on the platform — gold coins, Rolex watches, rare collectors cards, high-value Adventures. Editorially curated by David. Purpose: wow factor and first impression. Transitions automatically to personalised feed once buyer has 3+ wishlist signals.

**PR-28** — **Empty state (registered buyer / < 3 signals):** Shows the showcase scroll with a subtle overlay prompt: *"Browse above to personalise this feed."*

**PR-29** — Each personalised feed card shows: listing thumbnail, category badge, suburb/city, Trust Score badge of the seller, time since listing appeared, and a view count. No seller identity shown — anonymity rules apply.

**PR-30** — Cards display a subtle **age + demand signal**: time since listed + view count. Factual information only — not manufactured urgency.

**PR-31** — The feed refreshes in real time (WebSocket or polling every 60s). New matches appear at the top with a soft animation.

**PR-32** — Tapping a feed card opens the standard listing detail view and initiates the normal introduction flow.

---

### 3.7 Wearable Notifications

**PR-33** — Buyers may connect a wearable device (smartwatch, smart ring) via buyer app settings. Android wearables and most smartwatches: Web Push API. Apple Watch: requires iOS companion app — in scope for V1, delivered via standard iOS Push Notification Service (APNs) through a PWA or future native app wrapper.

**PR-34** — A ping fires when a new listing scores ≥ 80 match confidence AND meets the buyer's Trust Score threshold for that signal.

**PR-35** — Ping payload: category + suburb/city + one-line description only. No seller identity, price, or listing ID in the notification payload.

**PR-36** — Ping rate-limited to maximum 3 pings per buyer per hour.

**PR-37** — Buyers can disable pings per wishlist item, per category, or globally from settings.

---

### 3.8 Tuppence Boost (Seller-Side)

**PR-38** — A seller may spend **2 Tuppence** to boost a listing into matched wishlist feeds.

**PR-39** — Boost effect: expanded match tolerance (looser semantic threshold, score ≥ 45 instead of ≥ 60), expanded geographic radius (national for free-tier sellers, global for Global-tier sellers and boosted listings), and priority placement (top of feed, labelled "Featured").

**PR-40** — A free-tier seller who boosts becomes globally visible for that listing to matched buyers worldwide for the duration of the boost. This is a meaningful upgrade incentive for sellers.

**PR-41** — Boost duration: 7 days or until the listing is sold/removed, whichever comes first.

**PR-42** — Boost targeting is anonymous: the seller sees "your listing was shown to N matched buyers." No buyer identities or signals are ever exposed.

**PR-43** — Boosting never places a listing in a feed where the buyer's Trust Score filter would exclude it. Trust Score gating is absolute — it cannot be bought around.

**PR-44** — Boosted listings are labelled "Featured" in the feed. No deception.

*Cost model impact: 2T boost = USD $4 per boost per listing per 7 days. Projected volume to be added to Cost_Breakdown_GlobalLaunch.xlsx at activation.*

---

## 4 · Data Model

### 4.1 New Tables (BEA SQLite)

```sql
-- Buyer wishlist signals (implicit + explicit)
CREATE TABLE wishlist_signals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_token     TEXT NOT NULL,          -- anonymous buyer identifier, not email
    signal_type     TEXT NOT NULL,          -- 'browse_search' | 'browse_view' | 'explicit'
    raw_text        TEXT,                   -- search term or free-text description
    category        TEXT,                   -- optional category filter
    suburb_id       INTEGER,                -- optional suburb filter
    price_min       REAL,
    price_max       REAL,
    min_trust_score INTEGER DEFAULT 0,      -- 0=any, 40=Established+, 70=Trusted+, 90=Highly Trusted
    weight          REAL NOT NULL DEFAULT 1.0,  -- explicit=2.0, browse=1.0
    created_at      TEXT NOT NULL,
    expires_at      TEXT NOT NULL           -- 90 days from last activity
);

-- Matched listing queue per buyer
CREATE TABLE wishlist_matches (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_token     TEXT NOT NULL,
    listing_id      INTEGER NOT NULL,
    match_score     REAL NOT NULL,          -- 0–100
    seller_trust    INTEGER NOT NULL,       -- trust score at time of match
    matched_at      TEXT NOT NULL,
    seen            INTEGER DEFAULT 0,      -- 0=unseen, 1=seen in feed
    pinged          INTEGER DEFAULT 0,      -- 0=not pinged, 1=wearable ping sent
    boost_rank      INTEGER DEFAULT 0       -- 0=organic, >0=boosted position
);

-- Wearable device registrations
CREATE TABLE wearable_devices (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_token     TEXT NOT NULL,
    push_endpoint   TEXT NOT NULL,          -- Web Push or APNs endpoint
    push_keys       TEXT NOT NULL,          -- JSON: {p256dh, auth} or APNs token
    platform        TEXT NOT NULL,          -- 'android' | 'ios' | 'web'
    device_label    TEXT,                   -- 'Watch', 'Ring', 'Phone', etc.
    enabled         INTEGER DEFAULT 1,
    created_at      TEXT NOT NULL,
    last_ping_at    TEXT
);

-- Showcase listings (editorially curated — empty state feed)
CREATE TABLE wishlist_showcase (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id      INTEGER NOT NULL,
    sort_order      INTEGER NOT NULL DEFAULT 0,
    added_at        TEXT NOT NULL,
    added_by        TEXT NOT NULL DEFAULT 'admin'
);

-- Buyer subscriptions (wishlist global tier)
CREATE TABLE wishlist_subscriptions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer_token     TEXT NOT NULL UNIQUE,
    tier            TEXT NOT NULL DEFAULT 'free',   -- 'free' | 'global'
    activated_at    TEXT,
    expires_at      TEXT,
    paystack_ref    TEXT
);
```

### 4.2 Modified Tables

- `listings` — add `published_at` timestamp if not already present
- `users` — add `buyer_token` UUID column (generated on first login/registration)

---

## 5 · System Flow

```
NEW VISITOR
        │
        ▼
Bottom half → Showcase scroll (gold coins, Rolex, rare cards)
        │
        ▼
Visitor registers (free) → buyer_token assigned
        │
        ▼
Haiko onboarding coach → guides Trust Score completion
(email +5, phone +8, ID +12, banking +5, profile +5)


REGISTERED BUYER BROWSES / SEARCHES
        │
        ▼
Signal captured → wishlist_signals
(buyer_token, signal_type, raw_text, category, suburb, min_trust_score)
        │
        │ (3+ signals → feed transitions from showcase to personalised)
        │

SELLER PUBLISHES LISTING
        │
        ▼
Matching job triggered (async, within 60s)
        │
        ├── Extract listing intent (Haiko: category, keywords, suburb, price)
        │   └── Fallback if Haiko unavailable: keyword overlap scoring
        │
        ├── Query wishlist_signals for candidate buyers
        │
        ├── Score each candidate (0–100 semantic match)
        │
        ├── Apply Trust Score gate: exclude if seller_trust < signal.min_trust_score
        │
        ├── Apply geographic gate: free buyer = national only | global buyer = all
        │
        ├── score ≥ 60 (or ≥ 45 if boosted) → INSERT wishlist_matches
        │
        └── score ≥ 80 + trust gate passes → trigger wearable ping
                │
                ▼
        Push to wearable_devices (Web Push / APNs)
        payload: {category, suburb, description_excerpt}


BUYER OPENS APP
        │
        ▼
Bottom half loads wishlist_matches WHERE buyer_token=X AND seen=0
ORDER BY boost_rank DESC, matched_at DESC
        │
        ▼
Cards: thumbnail · category · Trust Score badge · suburb · age · view count
        │
        ▼
Buyer taps card → listing detail → standard introduction flow


SELLER BOOSTS (2 Tuppence)
        │
        ▼
Boost record created · boost_rank set · geographic gate expanded
Seller sees: "shown to N matched buyers" — no buyer identity
```

---

## 6 · Agent Responsibilities

| Component | Agent | Notes |
|---|---|---|
| `wishlist_signals` capture | Frontend agent | Fires on every search, filter change, and listing view |
| Trust Score filter UI | Frontend agent | Slider/preset on wishlist settings screen |
| Matching job | BEA / Architect agent | Background worker, async — does not block publish |
| Intent extraction | Haiko agent socket | Hot-swappable — Haiko 4.5 primary, keyword fallback |
| Scroll feed UI | Frontend agent | Bottom half of `marketsquare.html` |
| Showcase curation | David (manual) | Admin tool to add/reorder showcase listings |
| Wearable push | BEA / Architect agent | Web Push (Android) + APNs (iOS) |
| Boost mechanics | BEA / Architect agent | 2T deduction, expanded tolerance + radius |
| Onboarding coach | Haiko agent socket | Trust Score guidance for new registrants |
| Settings UI | Frontend agent | Ping controls, Trust Score filter, wishlist view/edit/delete |
| Global subscription | BEA / Architect agent | Paystack $5/month flow |

---

## 7 · Privacy Architecture

- **buyer_token** is a server-assigned UUID, never the buyer's email or name
- The mapping `buyer_token → email` exists only in the `users` table, server-side, never returned in any wishlist-related API response
- Matching queries never return buyer identity to any external caller
- Seller boost reporting returns only aggregate counts ("shown to N buyers") — never token, email, or any identifier
- Trust Score filtering runs server-side; sellers never learn which Trust Score threshold a buyer applied
- Banking details collected at onboarding are stored encrypted and used only for Paystack payment flows — never shared, never used for profiling
- Wishlist data is excluded from all analytics, data exports, and third-party integrations
- POPIA compliance: data minimisation, purpose limitation, deletion-on-request (expires_at + manual delete)
- Principle: *"Your wishlist never leaves MarketSquare."* This statement must appear in the onboarding flow and settings screen.

---

## 8 · Out of Scope (V1)

- Cross-city wishlist matching beyond geographic tier (handled by subscription gate)
- Wishlist sharing between buyers
- Group wishlists
- Seller-initiated "I have this item" push to wishlist holders
- Price drop alerts (separate feature, different signal type)
- Offline wearable sync

---

*End of WISHLIST_REQUIREMENTS.md v0.2. Open questions resolved. Ready for implementation planning.*
