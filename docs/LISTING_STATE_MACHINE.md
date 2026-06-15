# TrustSquare — Listing State Machine
**Version 1.2 · 25 May 2026 · Locked design — do not change without Architect agent sign-off**

---

## Overview

Every listing on TrustSquare exists in exactly one of seven states at any point in time.
State transitions are either seller-initiated, system-triggered, or admin/legal-initiated.
Buyers only ever interact with listings in the **LIVE** state.

---

## The Seven States

### 1. DRAFT
- Filled in by the seller but not yet published
- Invisible to all buyers — never appears in browse, search, or intro flows
- Does not consume a commitment-model slot
- Fully editable by the seller
- **Auto-expires after 30 days** — nudge email at day 20, auto-archived at day 30
- Reached via "Save as draft" on the publish screen, or "Reactivate" from WITHDRAWN

### 2. LIVE
- Visible in buyer browse and search
- Accepting intro requests
- The only state buyers ever interact with
- Commitment model listings auto-pause when an intro request arrives
- Duration before Fade Out is gated by seller subscription tier (see Fade Out section)
- **Listing count limits by tier:** Free = 2 simultaneous live listings · Starter ($5/mo) = 25 listings · Premium ($15/mo) = 50 listings
- **Batch expansion:** Starter and Premium sellers may purchase additional listing capacity at 2T per batch of 20 extra listings. Free tier sellers must upgrade to Starter before purchasing extra slots.

### 3. PAUSED
- Was LIVE, now temporarily off
- Two causes:
  - **(A) Auto-pause** — commitment model listing receives an intro request
  - **(B) Manual pause** — seller pauses deliberately (e.g. holiday, not ready)
- Hidden from buyers. No new intros accepted. Existing pending intros remain active
- One tap to resume → returns to LIVE
- **Fade Out clock continues ticking while PAUSED** — a listing paused and abandoned
  will fade exactly as a live abandoned listing would

### 4. FADE OUT
- System-triggered when a listing has been LIVE or PAUSED with no intro requests
  received AND no seller login within the tier's inactivity window
- Removed from buyer browse silently — no buyer-facing notice
- Seller receives nudge email: *"Your listing is fading — tap to keep it live"*
- Seller has **14 days from nudge** to respond
  - Tap "Keep live" → returns to LIVE immediately
  - No response within 14 days → auto-moves to ARCHIVED

**Inactivity windows by subscription tier:**

| Tier        | Inactivity window | Nudge sent | Auto-archived if no action |
|-------------|-------------------|------------|----------------------------|
| Free        | 30 days           | Day 23     | Day 44 (30 + 14)           |
| Starter     | 60 days           | Day 53     | Day 74 (60 + 14)           |
| Premium     | 120 days (4 mo.)  | Day 113    | Day 134 (120 + 14)         |

### 5. WITHDRAWN
- Seller-initiated soft delete — sold, no longer available, or changed mind
- Hidden from buyers immediately
- Row is kept in the database (Trust Score history and intro audit trail preserved)
- Seller can reactivate to **DRAFT** within 90 days for review before re-listing
- After 90 days with no reactivation → auto-moves to ARCHIVED

### 6. BLOCKED
- Platform-initiated removal due to a verified breach of EULA
- Listing AND seller account suspended simultaneously
- Cause is logged internally using a cause code (B1–B6)
- Seller notified by email with cause code and appeals process reference
- Reinstatement is possible only on legally enumerated grounds (see below)

**Enumerated block causes:**

| Code | Cause | Reinstatement |
|------|-------|---------------|
| B1 | Fraudulent Trust Score evidence (forged/altered credential) | ✅ Possible — authenticated original document + re-verification |
| B2 | Fraudulent listing (not authorised to sell/market) | ✅ Possible — proof of authority within appeal window |
| B3 | Systematic intro ignoring (3+ ignored in rolling 30 days) | ✅ Possible — 60-day cooling period + acknowledgement |
| B4 | Buyer harassment (contact after declined intro) | ✅ Possible — first offence only, buyer consent + 90-day suspension served |
| B5 | Payment fraud / chargeback abuse | ❌ Permanent — referred to Paystack fraud team |
| B6 | Identity fraud (false or stolen identity) | ❌ Permanent — may be referred to relevant authority |

**Appeals window:** Seller has 30 days from BLOCKED notification to lodge an appeal.
If no appeal is received within 30 days → auto-moves to ARCHIVED.

### 7. ARCHIVED
- Permanent terminal state — cannot be reactivated under any circumstances
- Reached from: DRAFT (30d expire), WITHDRAWN (90d), FADE OUT (14d no response),
  BLOCKED (appeal denied, permanent cause, or no appeal in 30 days)
- Row kept indefinitely for:
  - Trust Score history (intro counts, tenure, signals)
  - Listing version snapshots (audit trail)
  - Legal compliance
- Never visible to buyers

---

## All Transitions

| From      | To         | Trigger                                              | Initiated by       |
|-----------|------------|------------------------------------------------------|--------------------|
| —         | DRAFT      | "Save as draft" on publish screen                    | Seller             |
| —         | LIVE       | "Publish now" on publish screen                      | Seller             |
| DRAFT     | LIVE       | "Publish" from seller dashboard — one tap            | Seller             |
| DRAFT     | ARCHIVED   | "Discard" by seller, or auto at 30 days              | Seller / System    |
| LIVE      | PAUSED     | Commitment model intro received, or manual pause     | System / Seller    |
| LIVE      | FADE OUT   | Inactivity exceeds tier window                       | System             |
| LIVE      | WITHDRAWN  | Seller taps "Withdraw listing"                       | Seller             |
| LIVE      | BLOCKED    | Verified EULA breach (B1–B6)                         | Admin / System     |
| PAUSED    | LIVE       | Intro resolved or seller resumes                     | System / Seller    |
| PAUSED    | WITHDRAWN  | Seller withdraws while paused                        | Seller             |
| FADE OUT  | LIVE       | Seller taps "Keep live" within 14-day nudge window   | Seller             |
| FADE OUT  | ARCHIVED   | No response within 14 days of nudge                  | System             |
| WITHDRAWN | DRAFT      | Seller reactivates within 90 days                    | Seller             |
| WITHDRAWN | ARCHIVED   | Auto after 90 days, or admin action                  | System / Admin     |
| BLOCKED   | LIVE       | Successful appeal on enumerated legal ground         | Legal / Admin      |
| BLOCKED   | ARCHIVED   | Appeal denied, permanent cause, or no appeal in 30d  | Admin              |

---

## BEA Implementation Rules

### Public buyer endpoints (GET /listings, browse, search)
```sql
WHERE listing_status = 'live'
AND (suspension_reason IS NULL OR suspension_reason = '')
```

### Intro request creation
- Reject with HTTP 409 if `listing_status != 'live'`
- Error message: `"This listing is not currently accepting requests."`

### Seller dashboard (GET /listings/mine)
- Returns ALL statuses — seller sees draft, live, paused, faded, withdrawn
- Frontend renders each state with its own card style and CTA
- ARCHIVED and BLOCKED are visible to seller as read-only history

### Trust Score and intro history
- ARCHIVED listings must never be hard-deleted — intro history references `listing_id`
- BLOCKED listings: `block_cause` column stores B1–B6 code for admin audit

---

## Schema Migration

Four columns added to the `listings` table (idempotent `ALTER TABLE`):

```sql
ALTER TABLE listings ADD COLUMN listing_status TEXT NOT NULL DEFAULT 'live';
ALTER TABLE listings ADD COLUMN status_changed_at TEXT;
ALTER TABLE listings ADD COLUMN block_cause TEXT;        -- B1–B6 code
ALTER TABLE listings ADD COLUMN fade_nudge_sent_at TEXT;

CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(listing_status);
```

**Backfill:** All existing listings default to `'live'` via the column default.
No data migration required.

**Valid values:** `'draft'` | `'live'` | `'paused'` | `'faded'` | `'withdrawn'` | `'blocked'` | `'archived'`

---

## EULA Clauses Required

**Acceptance gate:** The EULA must be accepted (checkbox + timestamp) before a seller account can be created. No registration completes without it. The acceptance event is stored in the `users` table as `eula_accepted_at`.

---

### § 1 — Listing Lifecycle

The seller acknowledges that every listing exists in exactly one of seven states: DRAFT, LIVE, PAUSED, FADE OUT, WITHDRAWN, BLOCKED, or ARCHIVED. The platform may transition a listing between states automatically (system-triggered) or manually (admin-initiated) in accordance with the rules set out in this agreement. The seller's rights in each state are defined in the sections below.

---

### § 2 — Listing Count Limits

The number of simultaneously active (LIVE or PAUSED) listings is governed by the seller's subscription tier:

- **Free tier:** maximum 2 live listings at any time
- **Starter tier ($5/month):** maximum 25 live listings
- **Premium tier ($15/month):** maximum 50 live listings
- **Batch expansion:** Starter and Premium sellers may purchase additional listing capacity at 2 Tuppence per batch of 20 extra listings. Batches stack and are permanent. Free tier sellers must upgrade to Starter first — extra slots are not available on the free tier.

Attempting to publish beyond the tier cap (without a batch) will be rejected with an in-app message showing the upgrade or batch-purchase option.

---

### § 3 — Fade Out (Inactivity)

A listing enters FADE OUT when there has been no intro request received and no seller login recorded within the inactivity window for the seller's current subscription tier:

| Tier | Inactivity window | Nudge sent | Auto-archived if no action |
|------|-------------------|------------|----------------------------|
| Free | 30 days | Day 23 | Day 44 (30 + 14) |
| Starter | 60 days | Day 53 | Day 74 (60 + 14) |
| Premium | 120 days | Day 113 | Day 134 (120 + 14) |

On entering FADE OUT the listing is hidden from buyers immediately. A nudge email is sent to the seller's registered address. The seller has 14 days from the nudge to tap "Keep live" — if no action is taken within that window the listing is automatically ARCHIVED. The seller may renew a Free tier listing's active status at no charge by logging in within the inactivity window.

---

### § 4 — Suspension and Blocking

The platform may suspend and BLOCK a listing, along with the associated seller account, only upon verified evidence of one of the following enumerated causes. All causes are empirical and objectively verifiable — no subjective or discretionary blocking is permitted.

#### Causes with recourse (B1–B4)

**B1 — Fraudulent Trust Score evidence**
Uploading a forged, altered, or misrepresented credential document (certificate, registration number, ID). *Reinstatement:* seller provides authenticated original document and passes re-verification.

**B2 — Fraudulent listing**
Marketing a property or service the seller does not own or is not authorised to sell or represent. *Reinstatement:* seller provides proof of authority (mandate letter, ownership deed, written instruction from owner) within the 30-day appeal window.

**B3 — Systematic intro ignoring**
Three or more intro requests left without response within any rolling 30-day window, measured empirically by the platform. *Reinstatement:* 60-day cooling-off period must be served in full, followed by written acknowledgement of the platform's commitment model rules.

**B4 — Buyer harassment**
Confirmed contact of a buyer outside the platform following a declined or withdrawn introduction. *Reinstatement:* available on first offence only; requires the buyer's written consent and completion of a 90-day suspension period.

#### Causes without recourse (B5–B6) — permanent block

**B5 — Payment fraud / chargeback abuse**
Disputed Tuppence charges, fraudulent Paystack transactions, or a deliberate pattern of chargebacks. *No reinstatement.* The case is referred to Paystack's fraud team and may be escalated to relevant financial authorities.

**B6 — Identity fraud / deliberate deception**
Operating under a false or stolen identity, or any deliberate deception of the platform or its users intended to circumvent the anonymity and trust model. *No reinstatement.* The case may be referred to relevant legal authorities.

**By accepting this EULA the seller explicitly acknowledges that B5 and B6 carry permanent account termination with no right of appeal, and waives any claim to reinstatement on those grounds.**

---

### § 5 — Appeals Process

For causes B1–B4, the seller has **30 days from the date of the BLOCK notification email** to lodge a formal appeal via the platform's designated appeals channel. The notification email will state the cause code, the evidence on which the block was based, and the appeals contact. If no appeal is received within 30 days the listing and account are automatically ARCHIVED and the seller's right of appeal is extinguished.

Appeals are reviewed by a human administrator. The outcome (reinstatement or permanent archive) will be communicated within 14 days of receipt of the appeal.

---

### § 6 — Data Retention

All listing data, including ARCHIVED listings, is retained indefinitely in the platform database. Retention serves the following purposes:

- **Trust Score integrity** — intro counts, tenure signals, and credential history remain part of the seller's permanent record
- **Listing version snapshots** — all edit history is preserved for audit purposes
- **Legal compliance** — blocking and appeal records may be required by law

The seller consents to this retention as a condition of using the platform. Retained data is not visible to buyers and is not used for any purpose other than those stated above.

---

## Presentation Assets

- `LISTING_STATE_MACHINE_DIAGRAM.html` — visual state diagram (all seven states, transitions, tier table, block causes)
- This document (`LISTING_STATE_MACHINE.md`) — canonical reference

---

*This document is the source of truth for listing state logic. All BEA endpoints, frontend state rendering, and admin tooling must conform to it. Update version number and date on any change. Architect agent arbitrates conflicts.*
