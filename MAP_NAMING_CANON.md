# Country codes & journey maps — canon (26 Jul 2026, David)

## 1. Country codes are ISO 3166-1 alpha-2. Always.
The code is the single source of truth: `ZA`, `GB`, `US`, `AU`, `DE`, `NA`, `BW`, `MZ`.
**`GB`, never `UK`** — UK is not the ISO code. No local abbreviations, ever.

## 2. The map filename IS the code, lowercased
`adventures_<code-lowercase>_map.html`. No exceptions, no nicknames.
Drift found on 26 Jul, both to be corrected:
- `GB` -> `adventures_uk_map.html`   (should be `adventures_gb_map.html`)
- `ZA` -> `adventures_reserve_map.html` (should be `adventures_za_map.html`)

## 3. Only real countries belong in the country tables
`ADV_COUNTRY_FLAGS` currently carries `EU` and `LL`, which are not countries
(`LL` is in flags but not in currency — an asymmetry nothing checks). Region or
special-purpose keys belong in their own clearly-named table, never mixed in with
countries, or every lookup keyed on `listing.country` has to know the exceptions.

## 4. Multi-country journeys: HOST + SPANS  (David, 26 Jul)
A journey that crosses borders — Cape to Cairo crosses five — declares two things:

- **`host`** — the ISO code of its **starting point**. This is David's rule and it is
  the right one: it is unambiguous, never changes, and matches how a traveller thinks
  about where a trip begins. Cape to Cairo starts in Cape Town, so `host: 'ZA'`.
- **`spans`** — every ISO code the route passes through, in order. Cape to Cairo:
  `['ZA','ZW','TZ','SD','EG']`.

`host` decides where the journey LIVES. `spans` decides where it is FINDABLE.
A buyer browsing Egypt must be able to find a journey that ends in Egypt, even
though it is hosted in South Africa. Without `spans` that journey is invisible to
everyone except South Africans, which is the whole point of it existing.

## 5. Consequence: one country hosts MANY journeys
`ADV_COUNTRY_MAP` is currently one map per country key. That cannot hold once ZA
hosts both the Big Five reserve map and Cape to Cairo. The table must become a
LIST per country, each entry carrying `id`, `file`, `title`, `blurb`, `spans`.
Until that lands, a multi-country journey has no in-app home and is reachable by
direct URL only — which means no menu entry, no search hit, no discovery.

## 6. Enforcement
`scripts/regression_ledger.py` RG-0011 checks 1-3 on every run: codes are ISO,
every map key's file matches its code, and no non-country keys sit in the country
tables. A rule with no assertion behind it is a preference, and preferences drift.

## 7. Market tiers — launch depth vs global readiness (David, 26 Jul 2026)

David's framing: the app cannot be boxed into four countries, but the launch push
is four. Peripheral markets must be able to arrive **without breaking the mould** —
and the fact that they arrive cleanly is the rehearsal for global onboarding.

**LAUNCH markets (4):** `ZA`, `GB`, `US`, `AU`.
Full depth is required: currency, flag, own tour map with real photos, legal
must-haves, seller-flow labels in local currency, and full QA coverage.

**OPEN markets:** everything else — `DE`, `CA`, `NZ`, `NA`, `BW`, `MZ`, …
Required: an ISO code, a currency and a flag. Everything else must DEGRADE
GRACEFULLY — no map is fine (no entry = no map, the existing safe default), no
bespoke assets, no special-casing. An open market must never be a blocker.

### The readiness test (this is the actual rule)
> Adding a market must be **additive data, not code.**

If adding Germany means editing several parallel hardcoded tables, the mould is
already broken and global onboarding will be a rewrite. Today a market lives in at
least three separate objects (`ADV_COUNTRY_FLAGS`, `ADV_COUNTRY_CURRENCY`,
`ADV_COUNTRY_MAP`) that nothing keeps in step — which is exactly how `BW` came to
exist in none of them while a Botswana tour was being built.

**Target shape:** ONE market registry keyed by ISO code, one row per market:
`{ iso, name, flag, currency, tier, maps:[…] }`. Adding a market = adding a row.
The three existing tables derive from it. Then a launch market and an open market
differ by a field, not by scattered special cases.

### What QA then enforces (tier-aware, so peripherals never block launch)
- EVERY market, all tiers: has a currency and a flag. No exceptions — a market
  without a currency silently renders in Rand (the RG-0003 family).
- LAUNCH markets only: must additionally have a map, complete photos, and
  seller-flow labels in their own currency.
- An OPEN market missing a map is CORRECT, not a defect. QA must not report it.

### Naming traps this immediately catches
- `AUS` is not the code — ISO alpha-2 is **`AU`**. (`AUS` is alpha-3.)
- **Scotland is not a country code.** It is part of `GB`. If Scotland ever needs to
  be addressed separately it is the ISO 3166-**2** subdivision `GB-SCT`, never a
  top-level market. Treating it as one would fork `GB` and break every `GB` lookup.

## 8. Outstanding work — owned by Claude, no action needed from David (26 Jul 2026)

Recorded here so it survives session ends. Neither is urgent; both are pre-launch.

**A. Market registry consolidation — FRONT-END, not database.**
Three objects in `ms.js` (`ADV_COUNTRY_FLAGS`, `ADV_COUNTRY_CURRENCY`,
`ADV_COUNTRY_MAP`) must be edited in step and nothing enforces it — which is how
`BW` came to be absent from all three while a Botswana tour was being built.
Collapse to one registry keyed by ISO code (§7), derive the three from it.
Do it when `ms.js` is quiet — it is a shared file.

**B. Backfill `country` on listings — DATABASE, small.**
243 of 302 live listings carry no country, so they fall back to `'ZA'` and render
in Rand (the RG-0003 family). The column already exists; this is populating data,
not restructuring. Then make country required at write time so it cannot recur.
Separately: confirm completed transactions STORE their currency rather than
deriving it — a payment is a financial fact and must not change if a mapping does.

**Neither is a David task.** They are recorded so the next session picks them up
without being told.
