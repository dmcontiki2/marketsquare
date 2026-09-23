# PENDING — run 17's publish fixes (BLOCKED ON A WORK LOCK, not on a decision)

**Status: APPLIED 23 Sep 2026 ~20:25Z, awaiting the commit+deploy tick.** David released the
language lane's lock at his own instruction and the four changes are in the working tree,
validated (`py_compile` on bea_main.py, `node --check` on ms.js), with ledger entries RG-0443
(EULA-PUBLISH-1) and RG-0444 (RETURN-LINK-1) proven to FAIL against the pre-fix files and RG-0430
promoted to LOCKED. What follows is kept as the record of what was changed and why.

**One thing here turned out to be wrong and is corrected below: fix A's `accepted_terms` was
unreachable from HTTP** until the AUDIT-AUTH-1 route wrapper (added by the language lane the same
morning) was taught to forward it — a consent gate one function call away from being decoration.

**Original status line:** specified, not applied. `bea_main.py` and `ms.js` are locked by
`lang-quick-2026-09-23` (lock taken 2026-09-23T19:55:21Z; scope includes `bea_main.py`, `ms.js`,
`scripts/regression_ledger.py`, `migrations/*`, `changelog.d/*`). RUL-140 / SO-5: a lane told to
stand off a scope does not edit it. David asked for these fixes at 20:03Z; they are written out
here in full so whoever holds the lock — or the first run after it clears — applies them without
rediscovering anything.

**Already done, because it needed no locked file:** listing 382 (Rick Wemple, Montana) was
stamped `country='ZA'`; it is now `'US'` on the live database.

---

## A — EULA-PUBLISH-1 · `bea_main.py`, `publish_listing()`  (THE ONE THAT MATTERS)

**The defect, proven live on 23 Sep 2026, not inferred.** The gate reads:

    if user_row and not user_row["eula_accepted_at"] and not is_super:

A seller with **no users row at all** falls straight through it. That is not a corner case: the
guided wizard creates a listing from `seller_email` alone, so every first-time seller is exactly
that shape. Test: a fresh address created a draft through `POST /listings` and then published it
with `PUT /listings/391/publish?email=...` — **200, "Listing is now live"**, publicly visible,
with no account and no acceptance of the Terms anywhere on record. (Test listing 391 archived
immediately; it was public for about two minutes.)

**Why it must be closed before Rick is written to:** Rick has no users row. The recovery link we
are about to send him leads into precisely this path, so as it stands we would be inviting him
to publish without ever accepting the Terms, and relying on the browser to have asked him.
Client-side-only consent is not consent.

**The change.** Add `accepted_terms: int = 0` to the signature, and replace the gate with:

    # EULA-PUBLISH-1 (23 Sep 2026): acceptance is REQUIRED on every path and RECORDED
    # server-side. A caller that has not accepted sends accepted_terms=1 with the publish --
    # the tick the seller just made -- and the row is created and stamped here.
    if not user_row or not user_row["eula_accepted_at"]:
        if not is_super:
            if not int(accepted_terms or 0):
                conn.close()
                raise HTTPException(
                    status_code=403,
                    detail="EULA not accepted - seller must accept the TrustSquare Terms before publishing.")
            conn.execute("INSERT INTO users (email) VALUES (?) ON CONFLICT(email) DO NOTHING", (email,))
            conn.execute("UPDATE users SET eula_accepted_at = COALESCE(eula_accepted_at, CURRENT_TIMESTAMP) "
                         "WHERE email = ?", (email,))
            user_row = conn.execute(
                "SELECT trust_score, eula_accepted_at, is_superuser FROM users WHERE email = ?",
                (email,)).fetchone()

**Blast radius, checked rather than assumed — two callers, both in `ms.js`:**
- `sobGoLive` (7241) registers the user and stamps the EULA *before* publishing, so it is
  unaffected; it should still be given `&accepted_terms=1` so one failed stamp is not a dead end.
- `dashPublish` (10144) already handles the 403 and offers the seller a way to accept
  (HUB-EULA-1, 18 Sep) — that handler should re-issue the publish with `&accepted_terms=1`.

**This strictly tightens.** No path that publishes today without acceptance keeps doing so, and
no path that publishes today *with* acceptance changes behaviour.

## B — LISTING-COUNTRY-1 · `bea_main.py`, `POST /listings`

The INSERT names no `country`, so every wizard-created listing takes the table default `'ZA'`.
`ListingCreate` has no `country` field either. Note the trap: deriving it from `geo_cities` is
**not sufficient** — 'Montana' is not in `geo_cities` at all, which is why Rick's row had a NULL
`geo_city_id` and fell to the default.

- Add `country: Optional[str] = None` to `ListingCreate`.
- Widen the existing lookup to `SELECT id, country_iso2 FROM geo_cities WHERE name=? AND active=1`.
- `_country = (listing.country or (_gcity_row["country_iso2"] if _gcity_row else None) or "ZA").upper()[:2]`
- Add `country` to the INSERT column list and bind `_country`.
- `ms.js` must pass the magic link's `country` through on create — the link already carries it
  (`build_magic_link`), the create call drops it.

## C — RECOUP-WITHDRAW-1 · `bea_main.py`, new `GET /listings/{id}/withdraw?email=`

The "take it down" link in the recovery letter. One click, no account: archive the listing, clear
`photo_urls` / `thumb_url` / `medium_url`, delete the R2 objects, return a plain confirmation
page. **The letter's wording and this endpoint must match exactly** — if the R2 delete is not
implemented, the letter may not say the photographs are deleted. Auth is bare `?email=`, the same
shape the publish endpoint already uses; the action is the seller's own and benign.

## D — Correct RG-0429 on the board (blocked: `scripts/regression_ledger.py` is locked)

RG-0429 as written says the wizard has no route past the account wall. **That is wrong and must
not stand.** `HANDOVER-PUBLISH-1` already exists: a link of the shape
`?magic=1&email=...&name=...&cat=...&city=...&country=US&drafted=1&publish=1` routes to
`seller-onboard`, sets `_publishNow='ask'`, skips the plan screen, opens the Terms, publishes, and
asks for the account afterwards — RUL-145's shape, already built. `dashPublish` is a second such
surface ("publish a stranded draft"). The real defect is narrower and worse: **nothing in the
system ever sends that link**, so the fixed road has no on-ramp. Rewrite the entry to assert that
a stranded draft has a generated recovery link, not that the flow is unbuilt.

## E — The letter itself

Drafted at `RECOUP_RICK_LETTER.md`. Permission recorded at `.secrets/recontact_permission.json`.
**Not sent.** David set the order: flow first.
