# Seller Vacancy Pause — Codex Amendment + Build Spec

**Status:** DRAFT for David's approval · 1 June 2026
**Author:** Architect lane (Cowork session)
**Scope:** Add a seller-initiated "vacancy pause" so a let/sold property can be hidden from buyers but retained by the lister, then re-activated when it becomes available again.

This document has two parts: (A) the proposed **Codex amendment** to lock the rule, and (B) the **build spec** that implements it. Per the Codex-first operating rule, no code lands until Part A is approved.

---

## Background — the gap

The Codex (v4.7 §11) governs listing *duration* (tier inactivity windows, the 14-day nudge, fade totals Free=44d / Starter=74d / Premium=134d, auto-archive) and concurrent-listing slot caps. It does **not** cover a seller-initiated vacancy state.

The word "pause" already exists in the Codex for an unrelated concept: a Property listing is "Paused immediately" on an intro request (the commitment model, table 4 — one buyer at a time). The vacancy pause defined here is a **separate** lifecycle state and must not be conflated with the intro-commitment pause.

The 7-state listing machine (Session 37) already defines `DRAFT, LIVE, PAUSED, FADE_OUT, WITHDRAWN, BLOCKED, ARCHIVED`. The buyer feed already filters to `listing_status = 'live'`, so a paused listing is invisible to buyers with no extra work. What is missing: a controlled pause/reactivate transition, a seller-facing view of paused listings, and the slot-count + fade-out rules below.

---

## Decisions locked with David (1 June 2026)

1. **Visibility:** A paused listing is hidden from buyers; visible only to the lister in their own listings view. No public "rented/sold" label (avoids buyers spending non-refundable Tuppence on an unavailable listing, and preserves seller anonymity).
2. **Seller control:** The lister decides — keep it **paused** (held for the next vacancy) or **remove** it (free up a listing slot).
3. **Slot count:** A paused listing **counts against the concurrent-listing tier cap**. Pausing holds the slot; only removal frees it.
4. **Fade-out on reactivation:** Re-activating a paused listing **restarts the fade-out clock from the new listed date** (re-stamp `published_at = now()`).

---

# Part A — Proposed Codex Amendment (§11.4)

> **§11.4 · Seller Vacancy Pause (v4.8 — Session TBD)**
>
> A seller may pause a published listing to take it temporarily off the market (e.g. a rental that has been let, a service fully booked). This is distinct from the intro-commitment pause in §[intro model].
>
> 1. **State.** A vacancy pause sets `listing_status = 'paused'`. The transition is seller-initiated and reversible.
> 2. **Buyer visibility.** Paused listings are excluded from all buyer-facing feeds, search, and intro eligibility. No public label indicates the listing is paused, let, or sold.
> 3. **Seller visibility.** Paused listings remain fully visible to their owner in the seller's own listing management view, with their state clearly indicated.
> 4. **Slot consumption.** A paused listing **counts against the seller's concurrent-listing cap** (§11.1) exactly as a live listing does. To reclaim a slot, the seller must withdraw/archive the listing, not merely pause it.
> 5. **Reactivation.** Returning a paused listing to `live` re-stamps `published_at` to the reactivation time. The tier inactivity/fade-out clock (§11.1) therefore restarts from the new listed date.
> 6. **Fade interaction.** Pausing does not exempt a listing from fade-out; the inactivity clock is governed by `published_at`/activity as in §11.1. (A paused listing that is never reactivated will still fade per its tier window.)
> 7. **Audit.** Every pause and reactivation is recorded as a listing version snapshot (existing `listing_versions` mechanism) and stamps `status_changed_at`.
>
> *Rationale:* Rentals and services churn. Forcing a full re-list on every turnover discards Trust Score history and seller effort. Holding the slot keeps the slot economy (§11.2) honest — a seller parking many dormant listings must pay for the capacity or remove them.

**Open Codex question for David:** confirm the §11.4 version label (v4.8?) and whether this also belongs in the EULA's listing-lifecycle language.

---

# Part B — Build Spec

All file paths relative to `C:\Users\David\Projects\MarketSquare`. Surgical edits only; one change per task; CHANGELOG entry per task.

## B1 · BEA — controlled transition endpoint

**New:** `PUT /listings/{listing_id}/status`

- Body / query: `email` (seller auth, same pattern as `/publish`), target `status` ∈ {`paused`, `live`}.
- Auth: `?email=` must match `seller_email` (or stamp it if NULL, mirroring `update_listing`).
- EULA gate: same check as publish/edit.
- Transition rules:
  - `live → paused`: set `listing_status='paused'`, stamp `status_changed_at=now()`. **Do not** touch `published_at`.
  - `paused → live` (reactivate): run the **slot guard** (see B2), then set `listing_status='live'`, **re-stamp `published_at=now()`** and `status_changed_at=now()`.
  - Reject transitions from `draft`, `blocked`, `archived`, `withdrawn` here (those have their own flows); return 409 with a clear message.
- Archive a `listing_versions` snapshot before the change (reuse the block at `bea_main.py:1900–1909`).
- Returns `{listing_id, listing_status, status_changed_at, published_at}`.

**Lock down the generic PUT:** in `update_listing` (`bea_main.py:1861`), explicitly **reject or drop** `listing_status` if it appears in the update body, so status can only change via the controlled endpoint. (Confirm whether `ListingUpdate` even exposes `listing_status` today; if it does, remove it from the editable set.)

## B2 · BEA — slot guard counts paused

The slot guard in `publish_listing` (`bea_main.py:1743–1747`) currently counts only live:

```sql
SELECT COUNT(*) FROM listings
WHERE LOWER(seller_email)=?
  AND (listing_status IS NULL OR listing_status = 'live')
```

Change the count to include paused (paused holds the slot, per §11.4.4):

```sql
SELECT COUNT(*) FROM listings
WHERE LOWER(seller_email)=?
  AND (listing_status IS NULL OR listing_status IN ('live','paused'))
```

Apply the **same** guard inside the new `paused → live` reactivation path in B1 (a seller who removed/over-filled slots while paused can't exceed the cap on reactivation). Superusers remain exempt.

*Cost-model note for CHANGELOG:* this tightens slot consumption (paused now counts) — append `Cost model impact:` since it touches listing-slot mechanics.

## B3 · BEA — confirm feed already excludes paused

The buyer feed filter (`bea_main.py:1288`) is `listing_status IS NULL OR listing_status = 'live'` — paused is already excluded. **No change**, but add a one-line test asserting a paused listing does not appear in `GET /listings?city=…`.

## B4 · Seller view — paused listings + controls

Location: the seller's own listing-management surface. `GET /listings/mine?email=` (`bea_main.py:1837`) already returns **all** statuses, so the data is present.

- Render paused listings with a clear, non-public state indicator (e.g. a muted "Paused — hidden from buyers" chip). This is owner-only UI; it is **not** the public "rented" banner we rejected.
- Two actions per listing:
  - **Pause** (on a live listing) → `PUT /listings/{id}/status` `status=paused`.
  - **Mark available** (on a paused listing) → `status=live` (re-stamps date, runs slot guard; surface the 402 slot-limit message if hit).
  - **Remove** → existing withdraw/archive flow (frees the slot).
- ⚠️ Per project rule, do **not** Edit/Write the large HTML files directly — use a Python string-replace driver + verify the file still ends in `</html>`. Determine first whether this view lives in `marketsquare.html` (buyer app "my listings") or `marketsquare_admin.html`; spec the edit into whichever owns the seller listing list.

## B5 · Verification (required before done)

- BEA: unit/smoke test each transition (`live→paused`, `paused→live` with date re-stamp, illegal transitions rejected, generic PUT can't set status).
- Slot guard: a seller at cap with one paused listing cannot publish/reactivate a new one until they remove one.
- Feed: paused listing absent from buyer feed; present in `/listings/mine`.
- UI: screenshot the seller view showing a paused listing + working Mark-available / Remove controls.
- Run `python3 smoke_test.py` (must pass) and the demo-data audit if `LISTINGS`/`SELLERS` touched.

## Sequencing

1. Codex §11.4 approved & written (David).
2. B1 transition endpoint + generic-PUT lockdown.
3. B2 slot-guard change (+ cost-model CHANGELOG flag).
4. B4 seller UI.
5. B3/B5 tests + verification.
6. Deploy (scp BEA + HTML from PowerShell), session-end checklist.

---

## Items still needing David's confirmation

- Codex §11.4 version label and EULA inclusion (Part A).
- Which file owns the seller "my listings" view (B4) — buyer app vs admin tool.
- Wording of the owner-only paused indicator chip.
