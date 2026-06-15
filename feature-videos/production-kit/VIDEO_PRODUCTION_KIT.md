# TrustSquare Video Production Kit

Repeatable pipeline used for `collectables-advert-howto-7steps-55s.mp4`. Reuse for the other 10 AI-feature videos, category demos (1–3 min), and 7s shorts.

## The presenter
- **Reference image:** `student_ref.png` — attach as ingredient to EVERY Flow generation for character consistency.
- **Character line for prompts:** "The same young man from the reference image — same face, short brown hair, navy hoodie, same warm room with bookshelf, desk with card binders."

## Flow settings that worked
Video → Ingredients → 9:16 → 1x → **Omni Flash** → 8s. Cost observed: 8s = 12 credits, 6s = 10, 4s = 7 (50%-off promo pricing, mid-2026).

**Budgeting:** feature video ≈ 4 clips ≈ 48 credits (+ retakes ≈ 70). A 3-min category demo ≈ 20+ clips ≈ 300+ credits. 7s shorts ≈ 12–24 credits each.

## Prompt formula (per clip)
> [Character line]. He [action with phone/cards], then looks at camera and says, friendly and clear: '[VO line, max ~22 words for 8s]'. Vlog talking-head style, warm light, 9:16 vertical.

Keep one spoken sentence per clip; the model voices whatever is inside quotes.

## UI inserts (no Flow credits)
- `form.html` / `report.html` — rebuilds of app screens; render via Playwright headless Chromium at 430px width, device_scale_factor=2, full_page screenshot.
- `inserts.py` — animates: form-fill typing (uses `form_rects.json` field coordinates), Run-button press with "5T reserved" toast, report scroll in phone frame. Renders 720x1280@30 JPEG frames; key-tick/tap/ding SFX via numpy.
- For a new feature: rebuild its form/report HTML in app style, re-extract rects, adjust FILLS list in inserts.py.

## Stitch (ffmpeg)
Normalize every segment to 720x1280, 30fps, 44.1kHz stereo, then concat filter (n=segments). Presenter clips keep native audio; inserts carry SFX-only tracks.

## Verify before delivery
Transcribe master with faster-whisper (tiny.en) to confirm line order; extract boundary frames to check segment sequence.

## Notes
- Flow blocked trustsquare.co captures in-browser — rebuild UI as local HTML instead.
- Flow downloads are 720x1280. Fine in-app; for ads consider upscaling or a paid tier with higher-res export.
- For paid ad placements, check platform rules on AI-generated presenter disclosure (Meta/Google/TikTok each have their own).
