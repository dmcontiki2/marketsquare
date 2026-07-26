# Journey photo generation — runbook & run state (26 Jul 2026)

## Where it stands
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

## Placeholders are safe
Every stop without a photo renders a styled "photo pending" tile, so all four maps
are fully working and presentable right now. Photos drop in incrementally — no
big-bang needed, and nothing breaks part-way.
