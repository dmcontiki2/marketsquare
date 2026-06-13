# Heritage Site Tour Planner — Flow Prompt Pack (Video 02)

Per `production-kit/VIDEO_PRODUCTION_KIT.md` and `TrustSquare_Feature_Video_Scripts.docx` §02.
Flow settings: Video → Ingredients → 9:16 → 1x → **Omni Flash** → 8s (12 cr) / 6s (10 cr).

## ⚡ 50-credit shooting plan (tomorrow)
| # | Clip | Length | Credits |
|---|------|--------|---------|
| 0 | Couple reference STILL (ingredient) — generate first, reuse in every clip | image | ~0–2 |
| 1 | Hook — wife + husband | 8s | 12 |
| 2 | Walkthrough A — husband picks sites | 8s | 12 |
| 3 | Walkthrough B — husband adds waypoint | 8s | 12 |
| 4 | Payoff (MERGED call + thank-you — fits 50-cr budget) | 8s | 12 |
| | **Total** | | **48 / 50** |

The script's original 5-clip cut (~60 cr) splits clip 4 into call-ending + thank-you; shoot that version when credits refresh if the merged take feels rushed. If the reference still costs credits, drop clip 3 to 6s (10 cr) → total 46 + still.

## Reference still (generate FIRST, attach to every clip)
> Middle-aged South African couple at a kitchen table, Cape Town home, morning light, Table Mountain glimpsed through the window. WIFE: warm smile, colourful scarf. HUSBAND: glasses, golf shirt. Photoreal, 9:16.

**Character line for every clip prompt:**
> The same middle-aged South African couple from the reference image — wife with warm smile and colourful scarf, husband with glasses and golf shirt, same Cape Town kitchen, morning light, Table Mountain through the window.

## Clip 1 — Hook (8s)
> [Character line]. The wife turns to her husband and says, warm and determined: "We need a proper tour — I want to see the Kruger National Park. Properly, this time." The husband smiles, lifts his phone and says: "No problem — let's use TrustSquare." Vlog talking-head style, warm light, 9:16 vertical.

*Pacing risk: two speakers, ~24 words in 8s. Retake fallback (shorter): wife "I want to see Kruger — properly, this time." · husband "Let's plan it on TrustSquare."*

## Clip 2 — Walkthrough A (8s, husband presents)
> [Character line]. The husband holds his phone toward camera, tapping as he speaks, friendly and clear: "I pick my heritage sites — Kruger first — set our dates and budget, from Cape Town." The wife watches over his shoulder. 9:16 vertical.

## Clip 3 — Walkthrough B (8s, husband impressed)
> [Character line]. The husband taps the phone once, eyebrows up, impressed, and says: "I can even add a waypoint — Graskop! — and every overnight stop has lodging links built in." 9:16 vertical.

## Clip 4 — Payoff MERGED (8s)
> [Character line]. The husband lowers his phone from his ear, ending a call: "…perfect, see you Tuesday." He turns to his wife, delighted: "That was easy — map, planned days, budget, every stay arranged. Thank you TrustSquare!" She beams. 9:16 vertical.

## Negative prompt (every clip)
> No brand logos, no readable gibberish text on phone screens, no trademarked park signage.

## $0 inserts (no Flow credits — inserts.py pipeline)
1. **Form fill** — heritage form: sites=Kruger National Park, from=Cape Town, dates, 2 travellers, budget High → Run press → "5T reserved" toast. (Rebuild `form.html` variant + re-extract `form_rects.json`.)
2. **Report scroll** — rebuild `report.html` from the REAL Kruger replay (route legs table, day-by-day, lodging links, cost estimate — source: the delivered report, ai_jobs `dry_72abfbeede61`).
3. **Route MAP (~6s)** — the report's Leaflet map, Cape Town → Graskop → Kruger with day pins. Screenshot the real map from the app (needs your subscribed session).

## Assembly (ffmpeg, kit-standard)
hook 8s → sting 1.6s → walkA 8s → INSERT form ~8s → walkB 8s → INSERT report scroll ~8s → INSERT map ~6s → payoff 8s → sting out 1.6s ≈ **57s master**. Normalize 720x1280/30fps/44.1k, concat; whisper-verify line order before delivery.
