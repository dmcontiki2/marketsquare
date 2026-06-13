# Heritage Site Tour Planner — video build progress

## Done (13 Jun, today's free 50 Flow credits)
**Presenter clips** (`clips/`, 8s each, 720x1280, same cast throughout — verified consistent + correct dialogue):
- `hook-couple.mp4` — wife: "We need a proper tour — I want to see the Kruger National Park..." husband: "...Let's use TrustSquare for the planning."
- `walkthrough1-sites.mp4` — "I pick my heritage sites — Kruger first — set our dates and budget, from Cape Town."
- `walkthrough2-waypoint.mp4` — "I can even add a waypoint — Graskop! And look, every overnight stop has lodging links built in."

Cast reference still ("Couple in Cape Town kitchen") lives in the Flow project — reuse it as the ingredient for tomorrow's payoff clip so the couple stays identical.

**UI inserts** (`inserts/`, free, rendered offline):
- `insert1-form.mp4` (6s) — filled Heritage form, phone frame.
- `insert2-run.mp4` (3.2s) — Run · holds 5T press + "5T reserved · planning…" toast.
- `insert3-report-scroll.mp4` (12s) — full Tour Plan scrolling: route + lodging links, Graskop waypoint, lunches, excursions, R28,420 cost estimate.
- `insert4-route-map.mp4` (6.5s) — Cape Town → Kruger route map with Graskop waypoint (payoff visual).

`ui-source/` holds the editable HTML + render scripts.

## Full draft cut DONE — `heritage-tour-planner-AD-61s-DRAFT.mp4`
61.4s, 720x1280. Order: hook → logo-sting → wt1 → insert1(form) → insert2(run) → wt2 → insert3(report scroll) → insert4(route map) → payoff → logo-sting. Verified: whisper transcript in order, boundary frames correct.

### One beat is a STAND-IN (swap when credits refresh)
The closing payoff uses `inserts/payoff-STANDIN.mp4` — a Ken Burns shot of the couple (frame lifted from the hook) + caption "That was easy — everything planned, booked, and done. Thank you, TrustSquare!" + synthetic voiceover. It holds the slot but is NOT the scripted husband-spoken clip.

**To finalize (needs Flow credits — was 6 left, daily-refresh tier):**
1. Generate the real payoff clip (~15 credits): couple reference attached, husband ends a call and turns to wife: "That was easy — map, planned days, budget, every stay arranged and booked. Thank you TrustSquare!"
2. Re-run the same stitch command but swap `/tmp/payoff_temp.mp4` for the new clip (it's input #9). Everything else stays identical.
3. Optional: 7s short = hook + payoff.

## Notes
- Heritage report is a faithful rebuild from the script (trustsquare.co blocked for capture). Verify the figures match the real "See an example" output when convenient.
- Sandbox tip for next session: Chromium headless needs libXdamage.so.1 — fetch the .deb, `dpkg-deb -x` to /tmp/libfix, and `export LD_LIBRARY_PATH=/tmp/libfix/usr/lib/x86_64-linux-gnu` before running Playwright.
