# Overnight video run — started 28 Jun 2026 (~12:05)

Goal: get as many of the 10 feature videos to DRAFT as possible by morning, on the proven
Higgsfield recipe (production-kit/cast/HIGGSFIELD_RECIPE.md). David reviews + "cleanifies" tomorrow.

## Honest constraints (so the morning holds no surprises)
- I can't see/hear playback → auto-checks catch wrong-face & wrong-words only; delivery/lip-sync
  quality is David's call. These are DRAFTS.
- Videos 03–10 have NO cast stills on disk and NO clips → each needs cast built first (drift-prone,
  can't verify visually) then ~5 clips. Cast-building is the most likely to need rework.
- Two-person dialogue shots (hook/payoff with both faces) = unproven hard case.
- Browser automation may stall over the night; run continues where it can.

## Status legend
✅ done (draft stitched + auto-verified) · 🟡 clips generated, not stitched · 🟠 cast built only
· 🔴 not started · ⚠️ flagged for David

## Progress
- 01 Collectables — ✅ DONE (pre-existing FINAL)
- 02 Heritage — ✅ DRAFT DONE (heritage-tour-planner-AD-NEWCAST-DRAFT-28jun.mp4, 51s, new cast:
  wife hook + husband wt1/wt2/payoff + existing inserts. ⚠️ hook is wife-solo only — original
  script has a 2-person husband+wife hook; David may want husband's "Let's use TrustSquare" line
  added. Two-person shot not attempted blind.)
- 03 Expedition — ✅ FULL DRAFT DONE (expedition-dossier-AD-FULLDRAFT-28jun.mp4, 57s, 6 presenter
  clips + 3 LABELLED INSERT SLOTS in position: [form 6s] [Siberia dossier-scroll 12s] [route-map
  6s]. Swap real reports into slots tomorrow. Slot-maker tool: /tmp/make_slot.sh.)

## RUN MODE (rest of night): working solo through 03→10. Logging every step here. Will surface to
## David only at per-VIDEO completion or real blockers (drifted face / browser stall / low credits).
## Cast all hearted-approved. Inserts built as authentic-styled placeholders (real API reports
## swapped in by David later). Two-person shots cut as alternating singles.
## CREDITS: ~40 (Heritage) + 6 Expedition (dreamer x5 + friend) = ~100 of 2883 used.

## HONEST PACE RE-ASSESSMENT (mid-run):
Each video = ~30-40 min cycle (generate ~5 clips @90s each + download/sort + build inserts + stitch),
all human-driven via a browser that intermittently drops. 6 videos left. Building inserts for
03-10 from scratch is real HTML/Playwright work (none exist yet). Doing ALL 7 remaining fully
tonight is NOT realistic to stand behind. REVISED GOAL: finish Expedition (03) as 2nd full draft,
generate as many other videos' presenter clips as time allows, leave clear status. David + I
finish inserts/stitch together tomorrow.

## EXPEDITION (03) status: 5 dreamer clips filed to 03-expedition/clips/ (hook, wt1, wt2,
payoffA, payoffB — NAMING APPROX, verify by content). FRIEND clip was still generating at
download time → MISSING, re-fetch needed. Then build inserts + stitch.
NOTE: zip-download misses clips still rendering — wait for ALL to finish before downloading.

## DAVID DIRECTIVE (firm): build each video FULL-LENGTH tonight with PREDEFINED INSERT SLOTS
## (labelled blank placeholder segments, correct duration + position) so real reports drop in
## tomorrow as a simple swap. NEVER pause/hold waiting on David — reversible work proceeds + is
## flagged; the run must continue to completion all night. No blockers that freeze the night.
## Insert-slot convention per video: a 6s "form" slot, a 10s "report-scroll" slot, a 6s "map/
## payoff-visual" slot — black segment w/ centred label text "[INSERT: <name> — swap real report]".
- 04 Property — 🟡 3/5 clips filed (04-hook-man, 04-hook-woman, 04-wt1-woman). Woman wt2 + payoff
  were still rendering at download — RE-FETCH next pass, then stitch full draft w/ slots.

## ⚠️ HONEST FRICTION (logged ~2h in): Higgsfield render queue SLOWED for later clips (132529→
## 140853 = ~43min gap). Batch-download misses still-rendering clips → multiple passes needed per
## video. "All 10 fully stitched tonight" now UNLIKELY at this pace. Proven: pipeline works e2e,
## 2 full drafts done, cast+tooling banked. Recommend finishing remainder FRESH tomorrow (fast,
## discovery done) + real-API inserts together. Continuing through night regardless per David's ask;
## morning = mix of complete drafts + clips-ready-to-stitch. CREDITS ~120/2883.
- 04 Property — ✅ FULL DRAFT (all 5 real clips + 3 slots, 50s) — completed via recovered queue
- 05 Car — ✅ FULL DRAFT (car-dossier-AD-FULLDRAFT-28jun.mp4, 50s, buyer x4 + mate + 3 slots).
  PARALLEL APPROACH worked great — queued all 5 clips concurrently (8-way), much faster. NO boost
  (boost = $97 real money, declined). Credits ~2,719 → continuing.
- 06 Retirement — ✅ FULL DRAFT (retirement-planner-AD-FULLDRAFT-28jun.mp4, 55s). Woman's 3 real
  clips (hook/line/payoff, reused hearted scarf woman). Husband's 3 clips MISSED firing (button
  shifted on rapid batch) → 3 CLIP-PENDING slots + 3 insert slots. Re-gen husband clips when handy.
- SLOT-MAKER FIXED: apostrophes/brackets broke drawtext → now escaped (/tmp/make_slot.sh). Use
  plain ASCII labels to be safe.
- LEARNING: rapid multi-submit can miss when the Generate button shifts vertically (short vs long
  prompt changes panel height). Mitigation: screenshot-verify "Processing" after each submit, or
  generate slightly slower. Worth it vs re-fetch cycles.
- 07 Liquidation — ✅ FULL DRAFT (liquidation-plan-AD-FULLDRAFT-28jun.mp4, 50s, all 5 real clips:
  son hook/wt1/wt2/payoff + sister + 3 insert slots). Verify-after-each-submit fix worked — all
  5 fired cleanly, no misses. Indian SA siblings.
- 08 Weekend — ✅ FULL DRAFT (weekend-adventure-AD-FULLDRAFT-28jun.mp4, 48s, all 5 real clips:
  flatmate1 hook/wt1/wt2/payoff + flatmate2 + 3 slots). Two women flatmates (curly + gym).
- 09 Exam — ✅ FULL DRAFT (exam-study-plan-AD-FULLDRAFT-28jun.mp4, 49s). 3 real student clips
  (hook + 2 beats) + slots for: student payoff + MOM line (never generated) + 3 inserts. The
  fullscreen-renderer view shifted the Generate button → coordinate clicks missed; FIX: use
  find tool → click by element ref (ref_94 worked). 1 student clip lost to missed clicks.
- 10 Offer — ✅ FULL DRAFT (offer-strategy-AD-FULLDRAFT-28jun.mp4, 48s, ALL 5 real clips:
  Latino buyer hook/wt1/wt2/payoff + European woman friend + 3 insert slots). CLEANEST run of all
  — element-ref Generate clicks fired every clip first time, ZERO misses. ⭐ ELEMENT-REF FIX SOLVED
  the click problem regardless of view: find tool → ref_296 (Generate) / ref_247 (Turn to video).

## 🎉 ALL 10 FEATURE VIDEOS NOW HAVE DRAFTS (01 Collectables existed; 02-10 built this run).

## ⚠️ LESSON (important for next session): the "fullscreen renderer" Chrome view (enabled via the
## popup early on) MOVES the Generate button + makes fixed-coordinate clicks unreliable. Either
## (a) turn it OFF, or (b) click Generate via the find tool → element ref each time, and ALWAYS
## screenshot-verify the "Processing" state before moving on. This was the main friction source.

## RUN STOPPED at 8/9 target videos drafted (Heritage already existed = 9 total feature videos
## now have drafts incl. Collectables). Offer(10) + the few flagged clips = fresh session.

## Log
- 12:05 — Test husband-payoff clip APPROVED by David (face/voice/lipsync). Recipe + retrieve
  path documented. Downloads folder connected. Starting full run with Heritage finish.
- 12:20 — RELIABLE RETRIEVAL METHOD FOUND: per-clip in-player download is flaky; instead go to
  Assets → tick the day-group checkbox → "Download" → it zips selected clips → archive.zip lands
  in Downloads → unzip -j → file by timestamp. This is the pattern for all clips. Map by mtime:
  earliest = first generated.
- 12:20 — Heritage husband SOLO clips done (3/3): payoff, walkthrough1 (sites), walkthrough2
  (waypoint) — new high-quality cast, filed as *-husband-NEW-28jun.mp4. Inserts already exist.
  STILL NEEDED for Heritage: the WIFE (laughing scarf woman) lines + the HOOK (two-person, hard).
- NOTE: faster-whisper install TIMED OUT in sandbox → automated word-check degraded this run.
  Falling back to frame-checks (face/scene) + flagging spoken-word accuracy for David's review.
  Will retry a single batched whisper pass later if time allows.
- CREDITS so far: 3 clips x 10 = 30 (of 2883).
- 12:35 — Wife hook clip generated (new cast, laughing scarf woman, "We need a proper tour...
  Kruger... Properly, this time"). Frame-check good. Heritage now has 4 new-cast solo clips:
  husband wt1/wt2/payoff + wife hook. CREDITS: 40 total.
- STRATEGY (so David knows what to expect): switching to steady production mode — I log per-VIDEO
  here rather than per-clip. Two-person dialogue shots (both faces one frame) I'm NOT attempting
  blind; Heritage hook will use existing couple clip as placeholder + flag, OR cut as wife-solo
  then husband-solo. Casts for 03–10 mostly DON'T exist → must build portraits first (drift-prone).
  Assets already has some extra faces (younger men, other women) that may serve some scripts.
- PACE REALITY: ~90s generate + retrieval per clip, all human-driven by me via browser. Browser
  connection stability over 19h is the main risk. Aim: as many videos to DRAFT as possible.
