# MarketSquare · Session Notes
*Running log — append as decisions are made. Never delete entries. Most recent at top.*

---

## Session 37 · 2 May 2026 — Listing State Machine & Sell Flow

### Decisions locked this session

**Listing state machine** — 7 states confirmed and locked: DRAFT, LIVE, PAUSED, FADE OUT, WITHDRAWN, BLOCKED, ARCHIVED. Reference doc: `LISTING_STATE_MACHINE.md` v1.1.

**Fade Out tier windows** — confirmed correct as already documented:

| Tier | Inactivity window | Nudge sent | Auto-archived |
|------|-------------------|------------|---------------|
| Free | 30 days | Day 23 | Day 44 |
| Starter ($5) | 60 days | Day 53 | Day 74 |
| Premium ($15) | 120 days | Day 113 | Day 134 |

**Free tier listing count** — **2 simultaneous live listings** (not 1, not 3). Confirmed by David. Fixed in both `LISTING_STATE_MACHINE.md` and `LISTING_STATE_MACHINE_DIAGRAM.html`.

**EULA structure** — 7 clauses drafted and added to both files:
- § 1 Listing Lifecycle
- § 2 Listing Count Limits (Free = 2)
- § 3 Fade Out
- § 4 Suspension — causes with recourse (B1–B4)
- § 5 Permanent Block — causes without recourse (B5–B6)
- § 6 Appeals Process
- § 7 Data Retention

Key EULA principles confirmed:
- EULA must be **signed (checkbox + timestamp) before seller registration completes** — `eula_accepted_at` stored in users table
- Blocking requires **valid, empirical, legally enumerated grounds only** — no discretionary blocking
- B1–B4: recourse available (appeals, reinstatement on defined conditions)
- B5 (payment fraud) and B6 (identity fraud / deliberate deception): **permanent, no recourse** — seller waives appeal rights via separate checkbox at onboarding

**Subscription tier listing counts** — corrected from "unlimited" to:
- Free = 2 · Starter ($5) = 25 · Premium ($15) = 50
- Batch expansion confirmed: +20 listings per 1 Tuppence spent, batches stack and persist
- Fixed in `LISTING_STATE_MACHINE.md`, `LISTING_STATE_MACHINE_DIAGRAM.html`, and `SELL_FLOW.md`

**+Sell flow v1** — initial rebuild (incorrect — superseded by v2 below)

**+Sell flow v2** — recovered from uploaded session transcript docx, rewritten as `SELL_FLOW.md` v2.0 + `SELL_FLOW.html` v2.0:
- **Core principle:** 1·2·3 — new sellers live in 3 taps, no extra friction
- **Path A (new seller):** Step 1 = single photo · Step 2 = category + headline + price (commitment note below) · Step 3 = identity + EULA on submit → live immediately
- **Path B (returning seller):** B1 account picker sheet → B2 category + agent/private gate (Property) → B3 structured fields (beds/baths/etc feed AI) → B4 AI drafts description from inputs, seller edits → B5 room-by-room photo gallery (after fields, because now we know what to ask for) → B6 selfie last, always skippable → B7 Trust Score checklist (skippable, live score preview, AI confirms each upload, declaration text alternative) → B8 publish
- **AI coach NOT in sell flow** — inline AI (free) used in B3/B4/B7; full AI Coach is dashboard-only tool
- **Agent/private gate** — Property only, gates which Trust Score signals appear
- **Trust Score checklist** — vertical, skippable, live score ticks up, AI upload confirmation per signal

### Work completed this session

- [x] BEA schema migration — `listing_status`, `status_changed_at`, `block_cause`, `fade_nudge_sent_at` added to listings; `eula_accepted_at` added to users; `idx_listings_status` index created
- [x] BEA query guards — `listing_status = 'live'` enforced on `GET /listings`, `GET /local-market/listings`, `GET /local-market/listings/{id}`, `POST /intros`, `POST /local-market/intro`
- [x] Deployed to production — active and running as of 14:32 UTC 2 May 2026

### Work remaining — next session

- [ ] Seller dashboard frontend — render each of the 7 listing states with its own card style and CTA
- [ ] New +Sell flow frontend — implement Path A (3-tap) and Path B (8-step) in `marketsquare.html` per `SELL_FLOW.md` v3.0
- [ ] Cars category Trust Score signals — build in BEA (ownership, finance_clear, dealer_reg, rwc, inspection, service_history, safety_recall)
- [ ] `POST /listings/expand-batch` — batch capacity purchase (1T = +20 listing slots)
- [ ] 3 free AI sessions on registration — award in `POST /users`, remove `/dev/credit` dependency
- [ ] Conditional signal display logic — store `product_type`, `in_home_flag`, `agent_type` to gate Trust Score signal visibility
- [ ] Paystack live mode — awaiting approval (submitted 30 Apr 2026)
- [ ] CIPC Beneficial Ownership filing — due ~13 May 2026

---
