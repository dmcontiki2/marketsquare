# Next Session Prompt — Expand World Heritage / Wonders List (+200 sites)
> **📍 Deferred content task, tracked in `BACKLOG.md` → Deferred items.** Live loops live in `OPEN_LOOPS.md`.


**Goal:** Add at least **200 new sites** to the Wonders/World Heritage content layer, taking the total from the confirmed **120 base → ~320**, so that listings in well-covered areas link to a rich set of nearby sites (8–15+ candidates within radius), not just the 2–3 they currently show. Prioritise density in and around the **launch region (South Africa + Southern/East Africa)** first, then global breadth.

> ✅ **Base count confirmed (verified live this session).** The live server `GET /wonders` and `/var/www/marketsquare/wonders.json` both serve exactly **120 sites** (40 National Park `np_001–np_040`, 40 UNESCO `un_001–un_040`, 20 National Museum `nm_001–nm_020`, 20 Archaeological `ar_001–ar_020`; only **5** are in South Africa). The local `assets/wonders.json` is the same 120 count. **The CHANGELOG entry claiming "expanded to 400 sites and deployed" never actually shipped — there is no 400-site file anywhere. Build from the real 120 base. Do not go looking for a 400-site file; it does not exist.** New IDs therefore continue from `np_041 / un_041 / nm_021 / ar_021`.

Copy everything below the line into the new session.

---

Read `STATUS.md`, then `CLAUDE.md`, then this file before doing anything. This is a content-data task on the Wonders layer — **one focused task, no refactors of the matching engine.**

## Context — how the Wonders system actually works

- The entire feature is driven by a single JSON file: **`wonders.json`**. Each entry is one site (natural wonder, UNESCO/World Heritage site, national museum, or archaeological site).
- BEA loads it via `_load_wonders()` in `bea_main.py`, which reads from **`os.path.dirname(__file__)`** — i.e. the **project root / server working dir**, NOT `assets/`. The local copy currently lives at **`assets/wonders.json`** (120 entries). Resolve this path mismatch as step 1 below — do not skip it.
- Listings get sites auto-attached at publish by `_match_nearby_wonders(...)`: haversine distance from the listing's city to each site, filtered by a **category affinity map** (`_CAT_AFFINITY`), within a **country-derived radius** (`_derived_radius_km`: country bounding-box diagonal ÷ 3, clamped 150–800 km, default 300 km), capped at **`max_links = 3`**.
- Sellers can also manually set up to **5** linked wonders via `POST /listings/{id}/wonders`.
- FEA renders them from `linked_wonders` (JSON array of `{id, auto_linked}`) on the listing detail screen and the Wonders browse strip. `GET /wonders` serves the full list.

## Root cause of "only 2–3 sites linked" — confirm before fixing

There are **two** compounding causes. Verify both on the **server** (server is source of truth for `wonders.json`):

1. **Sparse data near the launch region.** The local 120-entry file has only **5 South Africa** sites and ~19 across all of Southern/East Africa. A Pretoria listing simply has very few sites within radius to match. **This is the primary thing to fix** — add density.
2. **Auto-link cap of 3.** `max_links = 3` in `_match_nearby_wonders`. Even with more data, auto-link tops out at 3. Consider raising the auto-link cap (e.g. to 5–6) and/or surfacing additional in-radius sites as "more nearby" suggestions in the FEA. **Decide with David** whether to raise the cap — flag it, implement best guess (suggest raising auto-link to 5 to match the manual cap), keep it reversible.

> ⚠️ **Path mismatch to fix first (not a count discrepancy).** The base count is settled at 120 (see confirmation above). The remaining issue is *where the file lives*: `_load_wonders()` reads from `os.path.dirname(__file__)` (project root / server working dir), but the local canonical copy is at `assets/wonders.json`, and there is **no** `wonders.json` in the local project root. Before adding entries, decide and apply ONE canonical location and make the loader, the edited file, and the deploy target all agree (see step 1). Pull the server copy first as your working base (`cd C:\Users\David\Projects\MarketSquare; scp root@178.104.73.239:/var/www/marketsquare/wonders.json ./wonders_server.json`) since the server is the source of truth — it and `assets/` are both 120 but not byte-identical (server has the photo-metadata audit fields), so start from the server copy.

## Exact data schema (every new entry must match this)

```json
{
  "id": "un_041",
  "name": "Mapungubwe Cultural Landscape",
  "type": "UNESCO Site",
  "country": "South Africa",
  "region": "Limpopo",
  "photo": "https://commons.wikimedia.org/wiki/Special:FilePath/<EXACT_Commons_filename>.jpg?width=1280",
  "description": "<~4–6 sentences, factual, visitor-oriented>",
  "history": "<~4–6 sentences of historical narrative>",
  "wikipedia": "https://en.wikipedia.org/wiki/<Article>",
  "lat": -22.1939,
  "lon": 29.3886
}
```

Field rules:
- **`id`** — keep the existing prefix-by-type convention and continue the numeric sequence from the current max per prefix:
  - `np_` = National Park · `un_` = UNESCO Site · `nm_` = National Museum · `ar_` = Archaeological Site
  - Find the current max for each prefix in the reconciled base file and continue (e.g. if base has `un_040`, new UNESCO sites start `un_041`). **No duplicate IDs, ever.**
- **`type`** — must be exactly one of: `National Park`, `UNESCO Site`, `National Museum`, `Archaeological Site` (these map to `_wonder_type_key()` and to FEA badge CSS classes `wd-type-*`). Do not invent new type strings.
- **`lat`/`lon`** — decimal degrees, accurate to ~4 dp. These drive haversine matching, so wrong coordinates = wrong/no links. Verify against Wikipedia/Wikidata coordinates.
- **`photo`** — Wikimedia Commons `Special:FilePath` URL with `?width=1280`. **Every photo URL must be verified to resolve** (the codebase has been bitten by FILE_MISSING and malformed-thumb URLs before — see CHANGELOG photo-audit entries). Run a HEAD/GET check on every new URL; replace any that 404 with a verified Commons alternative. Default `photo_author` to "Wikimedia Commons" only if Artist metadata is absent.
- Optional but preferred (existing entries have them): `photo_author`, `photo_licence`, `photo_source` from the Commons `extmetadata` API. If you add photos, batch-fetch these three for the new entries too, to match the existing 120/400.

## Distribution target for the 200+ new sites

Density where listings are, breadth everywhere else:

1. **Launch region first (≈80–100 sites): South Africa + neighbours.** Get South Africa to a strong density (aim ~30–40 SA sites total across all four types — national parks, UNESCO sites like Mapungubwe / Cradle of Humankind / Richtersveld / iSimangaliso / Vredefort Dome / uKhahlamba-Drakensberg, museums, and archaeological/fossil sites). Then Namibia, Botswana, Zimbabwe, Zambia, Mozambique, Lesotho, Eswatini, plus East Africa (Tanzania, Kenya, Uganda, Rwanda, Ethiopia). The point: a Pretoria/Joburg/Cape Town listing should find a genuinely rich set within radius.
2. **Rest of the world (≈100–120 sites):** broaden coverage of the UNESCO World Heritage list and major national parks/museums/archaeological sites across under-represented countries and continents, so future Wave-1 cities (New York, London, Sydney) and beyond are also well covered. Bias toward the official UNESCO World Heritage list for `un_` entries.

Keep a rough balance across the four `type` values so the type filter stays useful; UNESCO/`un_` can be the largest bucket since the request is World-Heritage-led.

## Steps

1. **Pull the server copy as your base and fix the path mismatch.** `scp` the live `wonders.json` (120 entries) down and work from it. Then make the canonical location consistent: either move the file to project root and update deploy scripts, or update `_load_wonders()` to read `assets/wonders.json`. Pick one, state which in the changelog, and make the matcher path, the edited file, and the deploy target all point at the same file. (Base count is already confirmed at 120 — no reconciliation of a phantom 400-set needed.)
2. **Generate the 200+ new entries** following the schema and distribution above. Source facts/coordinates from Wikipedia/Wikidata and the UNESCO World Heritage list. Write real `description` and `history` prose for each — no placeholders, no "TBD", no Lorem.
3. **Validate the data** with a script before deploy:
   - JSON parses; every entry has all required keys.
   - No duplicate `id`; prefixes match `type`; `type` is one of the 4 allowed strings.
   - `lat`/`lon` are floats in valid ranges and plausibly inside the stated country.
   - **Every `photo` URL resolves** (HTTP 200); list and fix any that don't.
4. **(Decision, flag it) Raise auto-link cap.** Implement best guess: bump `max_links` in `_match_nearby_wonders` from 3 → 5 so listings auto-attach up to 5 nearby sites (matching the manual cap), and confirm FEA renders >3 cleanly. Note it in the changelog as a behaviour change and flag for David to confirm/revert.
5. **Re-run auto-linking for existing live listings** so they pick up the new denser data. The matcher only runs when `linked_wonders` is NULL/empty — so add a one-off admin/maintenance script (or a `?force=1` path) that re-matches **all** live listings against the expanded set, overwriting auto-linked (but never seller-set) wonders. Verify a Pretoria listing now links a healthy set (target 5).
6. **Deploy & verify.** `scp` the reconciled `wonders.json` to `/var/www/marketsquare/wonders.json` on Hetzner, restart BEA, hit `GET /wonders` to confirm the new count live, purge Cloudflare cache, and spot-check the Wonders strip + a listing detail in the browser. Confirm yourself (screenshot) before reporting done — don't hand the check to David.

## Constraints & definition of done

- Follow `CLAUDE.md`: this is **one task**; if it must split (data add vs. cap-change vs. re-link script), complete each fully before the next.
- **Never** edit `marketsquare.html` / `marketsquare_admin.html` with Write/Edit — use Python `open/replace/write` + the integrity check (only relevant if you touch FEA for the >3 render).
- Ask David to run the git add/commit/push from PowerShell — never commit from the sandbox. Remind him `wonders.json` is a data file that must be committed.
- Smoke test passes (`python3 smoke_test.py`, all checks) — note it references heritage; make sure it still passes after the count change.
- **Done = ** server `GET /wonders` returns **≥ 320 sites** (120 base + ≥200 new), every photo URL resolves, no duplicate IDs, existing live listings re-linked (Pretoria listing shows a rich set, target 5), one-paragraph entry appended to `CHANGELOG.md` (with a `Cost model impact:` line only if anything affects API/photo bandwidth meaningfully — likely negligible), and `STATUS.md` updated. Also correct the stale CHANGELOG record so the project history no longer implies 400 sites are live when they were not.

## Cost / sovereignty note (per founder principles)

This is **static JSON + free Wikimedia Commons photos + free Wikipedia/Wikidata sourcing** — $0 ongoing, fully self-hosted, no consumption-based cost. The only token cost is this build session. No paid APIs needed. If you consider any paid geocoding/enrichment service, flag it first and prefer the free Wikidata SPARQL endpoint instead.
