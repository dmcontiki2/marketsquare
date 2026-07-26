# Journey photo generation — runbook & run state (26 Jul 2026)

## Where it stands  (updated 26 Jul 09:25)
- Photos: **54 of 104**. Cape to Cairo COMPLETE (31/31, deployed). Namibia COMPLETE
  (23/23) — adventures_na_map.html rebuilt (23 embedded/0 pending), NA UN-GATED in
  ms.js ADV_COUNTRY_MAP (syntax checked, regression ledger 0 regressions). Mozambique
  Mozambique IN PROGRESS: **5/25** (Day 1 done: d1_start/sight/food/view/over). Botswana not started (LAST — 0
  listings). Resume: photo_status --next, continue Mozambique d1_sight onward, then
  Botswana. Un-gate MZ (and BW once it has a listing) in ms.js when each set is done.
  Higgsfield queue slowed ~09:5x-10:0x then recovered; if a gen stalls past ~2 min,
  wait it out or regenerate — it clears.
- All four maps are DEPLOYED and load from `/static/adventures_{c2c,na,bw,mz}_map.html`.
  adventures_c2c_map.html rebuilt 26 Jul with all 31 photos embedded (0 pending) —
  NOT yet uploaded to the server; David runs the deploy.
- `ms.js` v387 is live: NA/BW/MZ are **gated out** of ADV_COUNTRY_MAP (they have no
  photos); live keys are ZA, US, GB, AU, DE. c2c is NOT a gated country entry — the
  Cape to Cairo map surfaces without any ms.js change, so ms.js was left untouched.
  Un-gate a country the moment its photos are done — the commented lines are right there.
- Botswana has **zero listings** live, so even un-gated its map cannot surface.
  A market needs listings before a map means anything.
- Canon for codes and market tiers: `MAP_NAMING_CANON.md`. Enforced by RG-0011.

## NEXT ACTION (start here)
Cape to Cairo DONE. Next: Namibia (23), Botswana (25), Mozambique (25) = 73 photos.
Prompts are in JOURNEY_HIGGSFIELD_PROMPTS.md;
`python3 scripts/photo_status.py --next 10` lists the exact filenames still missing.

## Original notes
4 of 104 photos generated and placed, all in Cape to Cairo:
`l1_start` (Cape Town platform) · `l1_food` (dining-car bobotie) ·
`l1_view` (winelands) · `l1_over` (sleeper cabin).
Run `python3 scripts/photo_status.py` for the live count — the FILESYSTEM is the
progress state, there is no separate ledger to drift.

## To resume (start here)
1. Connect BOTH folders: `C:\Users\David\Projects` AND `C:\Users\David\Downloads`.
   The Downloads grant is **per session** — a new session must ask for it again, and
   David has to approve on the device. This is why an unattended overnight run is
   NOT possible: a scheduled session cannot get that approval at 3 a.m.
2. `python3 scripts/photo_status.py --next 10`  -> the next filenames needed.
3. Prompts: `JOURNEY_HIGGSFIELD_PROMPTS.md` (all 104, generated from the specs).
4. Generate on higgsfield.ai/ai/image — model **Nano Banana Pro**, aspect **3:2**,
   2 credits each. Account greenswan1646, Ultra plan.
5. Claim each batch:
   `python3 scripts/claim_photos.py --since <epoch> cape_cairo l1_sight.jpg ...`
   (`date +%s` BEFORE generating — the guard needs a floor timestamp.)
6. `python3 scripts/build_journey.py journeys/cape_cairo.json` then check the map.

## Hard-won lessons — do not relearn these
- **ONE generation at a time.** Firing 4 in quick succession made 2 fail outright
  ("Failed — Credits refunded"). Rate limiting. They also serialise anyway, so
  parallel buys nothing. ~50-60 s per image.
- **Never claim by count alone.** The first claim script only checked for "unclaimed"
  files; Downloads was full of hf_*.png from earlier batches, so when two downloads
  silently failed it assigned a 22 June and a 22 July image to real stops. The
  rewritten script requires files NEWER than `--since` and claims nothing unless the
  count matches exactly. Keep that guard.
- **The mount blocks unlink.** Cannot delete anything under Projects or Downloads.
  Wrong files get blanked to zero bytes (status + builder both treat 0 bytes as
  absent) and overwritten later.
- **Downloading is the fragile step**, not generating. The hover download icon moves
  when tiles change (failed tiles vanish and reflow), and a mis-click opens the
  lightbox instead. The lightbox Download button is steadier, but downloads stopped
  producing files entirely after ~5 in a row — check Chrome for a blocked-download
  prompt before assuming the click failed.
- **Verify every claim.** Never trust that a download happened; `photo_status.py`
  after each batch is the check.
- **Higgsfield now GROUPS outputs into 2x2/collage tiles (26 Jul).** Each generation
  returns a *set* of images (specific-stop cell + style-block riffs: stations, trains,
  savanna). The hover/tile "Download" on a grouped tile saves the whole set as ONE
  collage PNG, not a single photo. Two working paths, both proven this session:
  (a) SINGLE result — right after generating, scroll the gallery to the TOP; if the
  newest is a lone large tile, open it (lightbox shows one image), Download, claim
  normally with claim_photos.py. (b) GROUPED result — hover-download the collage,
  stage+view it, and crop the matching cell with PIL (2x2 cells are exact quarters;
  a 2+3 layout has 3 narrower bottom cells). The build downsizes to 640px wide, so a
  ~632px cropped cell is full quality — place it straight into assets/journey/<id>/.
  VIEW every crop before placing; that visual check replaces the freshness guard when
  you bypass claim_photos.py.
- **The prompt box vs the search box.** After closing a lightbox with Escape, a stray
  click can land in the top search overlay instead of the prompt field, and your whole
  prompt gets typed into search. Screenshot before typing; if the typed text shows in a
  centred search modal, close it (x) and click the bottom prompt bar again.
- **Food/interior prompts drift to "dining in the cabin."** If a food stop renders as a
  cabin scene with the dish tiny in a corner, regenerate with a tight close-up prompt
  ("close overhead bowl filling the frame, no train interior") — worked first try for l6_food.

## Placeholders are safe
Every stop without a photo renders a styled "photo pending" tile, so all four maps
are fully working and presentable right now. Photos drop in incrementally — no
big-bang needed, and nothing breaks part-way.
