# Tutor Spotlight video — generation progress log
Pipeline: Higgsfield (higgsfield.ai, greenswan1646, Ultra Plan). Image: Nano Banana Pro (2 credits/portrait). Video: Kling 3.0, 9:16, 720p, 6s (12 credits/clip).
Credits at session start: 1,570.

## STATUS as of this session (14 Jul, ~06:00) -- ALL 24 CLIPS DONE
**24 of 24 clips done, downloaded, and verified** (E1-E19 Ester + A1-A5 Anathi). Every file hash-checked distinct (no duplicates), every file confirmed 716x1284/24fps/6.042s/h264+aac via ffprobe. Credits spent: ~250 of 1,570.
FULL RAW STITCH BUILT: ALL-CLIPS-RAW_24of24.mp4 -- 145.06s (2:25), narrative order E1-E10, A1-A5, E11-E19, ffmpeg concat -c copy (stream copy, no re-encode). Verified: ffprobe duration/spec, volumedetect real audio (mean -26.3dB, max -3.5dB, not silent), and visual frame-check at both character-switch splice points (E10->A1 and A5->E11) -- both clean, correct character, no corruption.
This is the RAW narrative cut only. NOT yet done: real UI screen-capture inserts (4 needed), on-screen text/captions, background music/SFX, final logo card, and the edit pass that drops the inserts into the 4 marked beats. Old partial file ROUGH-CUT_partial_0-54s_of_155s.mp4 (E1-E9 only, 9 clips) is now superseded by this full 24-clip stitch -- left in place, not deleted.
One deviation from the original script, done deliberately for the 6s-per-clip time budget: E18's line was trimmed from the full "One introduction. One tuppence. A verified tutor. A verified student. That's the service. Nothing more -- and nothing less." to "One introduction. One tuppence. That's the service. Nothing more, and nothing less." (dropped the middle "A verified tutor. A verified student." sentence -- fits natural pacing in 6s; can be restored as on-screen text in the edit if wanted).
NEXT: build the 4 UI inserts (Playwright/local HTML per project convention), then final edit pass (captions, music, logo card, insert placement) and QC.

## Cast portraits (DONE)
- Ester Booysen portrait — generated, hearted. 768x1376 (9:16).
- Anathi Jacobs portrait — generated. 768x1376 (9:16). NOT yet hearted (queue).

## Clips — status
| # | Character | Line | Status | File |
|---|---|---|---|---|
| E1 | Ester | "People see the number first. Eighty-three. Then they meet me." | DONE, downloaded, verified (h264 716x1284 24fps 6.04s + aac) | clips/ester-01-people-see-the-number.mp4 |
| E2 | Ester | "I tutor matriculants here in Wellington, Science and Mathematics, at their own kitchen tables." | DONE, downloaded, verified (h264 716x1284 6.04s + aac) | clips/ester-02-i-tutor-matriculants.mp4 |
| E3 | Ester | "Final year. Big exams. Nervous mothers." | DONE, downloaded, verified (h264 716x1284 6.04s + aac) | clips/ester-03-final-year-big-exams.mp4 |
| E4 | Ester | "I never advertise. I don't have to. My Trust Score does the introducing now." | DONE, downloaded, verified (6.04s) | clips/ester-04-i-never-advertise.mp4 |
| E5 | Ester | "Thirty-eight years of teaching, and it took a number to say it plainly." | DONE, downloaded, verified (6.04s) | clips/ester-05-thirty-eight-years.mp4 |
| E6 | Ester | "You can't type in eighty-three. Nobody can. TrustSquare worked it out itself." | DONE, downloaded, verified (6.04s) | clips/ester-06-cant-type-eighty-three.mp4 |
| E7 | Ester | "My ID, verified. My teaching qualification and my registration, checked, not claimed." | DONE, downloaded, verified (6.04s) | clips/ester-07-my-id-verified.mp4 |
| E8 | Ester | "And then the record: every session I've shown up for, every family that came back." | DONE, downloaded, verified (6.04s, hash-checked distinct from E7) | clips/ester-08-and-then-the-record.mp4 |
| E9 | Ester | "Evidence, not promises. That's the whole idea." | DONE, downloaded, verified (6.04s) | clips/ester-09-evidence-not-promises.mp4 |
| E10 | Ester | "Seventy puts you in green. Ninety, in gold. I'm earning my way there." | DONE, downloaded, verified (6.04s) -- ALL ESTER BEAT 1+2 CLIPS COMPLETE (E1-E10) | clips/ester-10-seventy-green-ninety-gold.mp4 |
| E11 | Ester | "The introductions come to me now, and I choose." | DONE, downloaded, verified (6.042s) | clips/ester-11-introductions-come-to-me.mp4 |
| E12 | Ester | "I look at where they are. I drive to their homes, so nearby matters." | DONE, downloaded, verified (6.042s) | clips/ester-12-i-drive-to-their-homes.mp4 |
| E13 | Ester | "And I look at their side of the square. Buyers carry a score too." | DONE, downloaded, verified (6.042s) | clips/ester-13-buyers-carry-a-score-too.mp4 |
| E14 | Ester | "Anathi was close, verified, serious. I accepted before my tea went cold." | DONE, downloaded, verified (6.042s) | clips/ester-14-anathi-was-close-verified.mp4 |
| E15 | Ester | "Two mornings a week now. Her trig is coming right." | DONE, downloaded, verified (6.042s) | clips/ester-15-two-mornings-a-week.mp4 |
| E16 | Ester | "TrustSquare didn't teach her trigonometry. I did." | DONE, downloaded, verified (6.042s) | clips/ester-16-didnt-teach-trigonometry.mp4 |
| E17 | Ester | "It stood between two strangers and said: she is who she says she is. And so is he." | DONE, downloaded, verified (6.042s) | clips/ester-17-stood-between-two-strangers.mp4 |
| E18 | Ester | "One introduction. One tuppence. That's the service. Nothing more, and nothing less." | DONE, downloaded, verified (6.042s) -- NOTE: trimmed from full script line, see status banner | clips/ester-18-one-introduction-one-tuppence.mp4 |
| E19 | Ester | "Because the introduction isn't a feature of TrustSquare. It is TrustSquare." | DONE, downloaded, verified (6.042s) -- ALL 24 CLIPS COMPLETE | clips/ester-19-it-is-trustsquare.mp4 |
| A1 | Anathi | "I typed 'maths tutor.' Got hundreds. Anyone can write 'twenty years experience' - how would I know?" | DONE, downloaded, verified (h264 716x1284 24fps 6.042s + aac) | clips/anathi-01-typed-maths-tutor.mp4 |
| A2 | Anathi | "So I filtered. Local Market: Wellington, walking distance, my ma insisted." | DONE, downloaded, verified (6.042s) | clips/anathi-02-so-i-filtered.mp4 |
| A3 | Anathi | "Then Trusted-plus, seventy and up. There's a gold button too, Highly Trusted, ninety." | DONE, downloaded, verified (6.042s) | clips/anathi-03-trusted-plus-seventy.mp4 |
| A4 | Anathi | "Suddenly it wasn't hundreds. It was a handful. One of them was Aunty Ester, eleven minutes away." | DONE, downloaded, verified (6.042s, hash-checked distinct) | clips/anathi-04-one-of-them-was-ester.mp4 |
| A5 | Anathi | "I didn't send a message into the dark. I requested an introduction. That's different." | DONE, downloaded, verified (6.042s) -- ALL ANATHI CLIPS COMPLETE (A1-A5) | clips/anathi-05-requested-an-introduction.mp4 |


## FULL RAW STITCH (14 Jul, ~06:00)
File: ALL-CLIPS-RAW_24of24.mp4 -- 145.06s (2:25), 716x1284, h264/aac, ffmpeg concat -c copy.
Order: E1-E10 (Ester Beats 1-2) -> A1-A5 (Anathi Beat 3) -> E11-E19 (Ester Beats 4-5).
Verified: ffprobe spec/duration, volumedetect (mean -26.3dB max -3.5dB, real audio confirmed), visual frame check at both character-switch splices (E10->A1, A5->E11) -- clean cuts, correct character each side, no corruption.
This is raw AI footage only -- no UI inserts, captions, music, or logo card yet. See "Known open items" below for what's left.


## SEAM/TRANSITION INVESTIGATION (14 Jul, ~07:10)
David asked why cuts between clips are visible and whether Higgsfield can stitch them invisibly. Findings:
- ROOT CAUSE: every clip was generated independently from the character's static REFERENCE PORTRAIT (image-to-video), not chained from the previous clip's last frame. Each cut resets to a fresh pose/expression, and each clip carries its own separately-generated lip-synced audio (24 separate vocal takes, not one continuous read) -- hence the audible pause/reset at every boundary.
- Checked Higgsfield live for a native multi-clip stitcher: Cinema Studio (Canvas/AI Director) and Shorts Studio are generation/restyle tools, not multi-clip timeline editors -- no "invisible stitch" button found in the Create Video / History UI (checked the "..." menu, asset detail Tools tab: Edit video/Reframe/Upscale/Remove Background/Change scene -- none of these).
- Higgsfield DOES have a real "AI Video Extender" (higgsfield.ai/ai-video-extender, model Kling 3.0 Omni Edit) that continues motion+audio from an existing clip's last frame with a claimed invisible seam -- but it is a forward-chaining generation tool (continue clip N to make clip N+1), not a retroactive fixer for clips already generated independently. Also noted: the Create Video panel has an "End frame" slot (start+end keyframe interpolation) which could in principle bridge two already-existing clips' boundary frames -- not tested.
- TESTED the free/cheap fix: ffmpeg crossfade dissolve (xfade+acrossfade, 0.35s) across clip boundaries. Built SAMPLE-CROSSFADE_E1-E4.mp4 (4 clips, 23.1s) and visually inspected the mid-dissolve frame. RESULT: REJECTED -- produces visible double-exposure ghosting (two overlapping hand/arm/face positions) because the poses don't match between independently-generated clips. Crossfade dissolve is not a fix for this footage.
- Real options going forward (costed, David's call): (a) regenerate as an Extend-chain within each unbroken monologue section for genuine continuity -- full re-spend, ~250-300 more credits, another session; (b) decouple a single continuous VO track from the Kling visuals, treat clips as cut-on-beat B-roll -- no new Higgsfield credits, but discards the baked-in lip-synced audio and requires new audio + resync; (c) ship current hard cuts as-is (legitimate talking-head style, especially once the 4 UI inserts and captions break up the monotony) -- free, ships today.

## EXTEND-CHAIN REBUILD (14 Jul, ~08:20) -- David approved, in progress
David approved (verbatim): "Claude, now that Paystack is up live. Lets go with the first choice and get a clean single sweep long continuous video for youtube. It is worth the 300+ credits :-)" -- i.e. regenerate each unbroken monologue section as a true continuity chain instead of shipping independent hard cuts.

MECHANISM USED (not the broken video-upload Extend tool): Higgsfield's native video-upload dropzone (AI Video Extender / Kling 3.0 Omni Edit) would not accept uploaded video files via the file-input method -- confirmed broken after 4+ attempts (see SEAM/TRANSITION INVESTIGATION above). Instead, used the Create Video panel's start-frame image slot: extract the ACTUAL LAST FRAME of clip N via ffmpeg, upload it as the sole reference image (no end frame) for clip N+1, keep the same character/scene description, and set the prompt text to clip N+1's actual line. This makes each new clip start from literally the same pixels the previous clip ended on. PROVEN via a first test (start-frame + end-frame keyframe interpolation between E1's last frame and E2's first frame) which produced a natural, artifact-free bridging motion -- confirmed by contact-sheet frame inspection.

RESULT -- ESTER BEAT 1-2 (E1-E10) FULLY REBUILT AS A CHAIN:
- New files in clips-chained/ (NOT overwriting the original clips/ folder): ester-01 (unchanged anchor, copied as-is) through ester-10, each generated Kling 3.0, 720p, 6.042s, 716x1284.
- Chain method per clip: extract last frame of previous NEW clip -> upload as start frame -> prompt = character/scene description + "Continuing naturally from this exact pose, she speaks ...: '<line>'" -> generate -> download -> verify duration via ffprobe -> extract its own last frame for the next link.
- VERIFIED: stitched all 10 into CHAINED-E1-E10.mp4 (60.47s, ffmpeg concat -c copy) and extracted paired before/after frames at all 9 cut points. Visual contact-sheet inspection: pose, expression, lighting and framing match cleanly at every single boundary -- a clear improvement over the old independent-generation cuts. Audio is still a separate take per clip (not a single continuous VO), so a small vocal-tone/pacing reset may remain at each cut, but the visual jump-cut is gone.
- Credits spent this stage: 9 new generations x 12 credits = 108 credits (E2-E10; E1 reused unchanged).

NEXT: same chain method for Anathi Beat 3 (A1-A5, 4 new generations) and Ester Beat 4-5 (E11-E19, 8 new generations), then final assembly joining the 3 chained sections at the 2 legitimate character-switch cuts (E10->A1, A5->E11), replacing ALL-CLIPS-RAW_24of24.mp4 as the deliverable once complete.

## ANATHI BEAT 3 (A1-A5) CHAIN COMPLETE (14 Jul, ~09:05)
Same chain method as Ester. Files in clips-chained/: anathi-01 (unchanged anchor) through anathi-05.
NOTE ON A RECURRING BUG HIT AND WORKED AROUND: Higgsfield's start-frame upload slot sometimes fails to visually/functionally update when REPLACING an already-loaded image in the same page session (silent failure -- file_upload tool reports success but the reference used for generation stays on the old image). Symptom caught before wasting credits: one throwaway generation (~18:20) used a stale Ester frame instead of Anathi's -- not used, not counted in the chain. Reliable fix found: do a full page reload (navigate to /ai/video fresh) before each upload so the slot starts empty, then upload once -- confirmed via zoom-screenshot on the small reference thumbnail BEFORE clicking Generate every single time from A2 onward. This extra verification step should be kept for the remaining E11-E19 section and any future chain work on this tool.
VERIFIED: stitched into CHAINED-A1-A5.mp4 (30.26s) and inspected paired before/after frames at all 4 cut points -- clean matches, no ghosting, no pose resets.
Credits spent: 4 new generations x 12 = 48 credits (A2-A5; A1 reused unchanged). Running total for the rebuild so far: 108 (Ester 1-2) + 48 (Anathi) = 156 credits.

NEXT: Ester Beat 4-5 (E11-E19, 8 new generations), verifying each upload via the zoom-before-generate check, then final assembly.

## FULL CONTINUITY REBUILD COMPLETE (14 Jul, ~09:45) -- DELIVERABLE
File: ALL-CLIPS-CHAINED_24of24.mp4 -- 145.06s (2:25), 716x1284, h264/aac, 24fps, ffmpeg concat -c copy.
Order: E1-E10 (chained) -> A1-A5 (chained) -> E11-E19 (chained). Same narrative order/content as the original raw cut, but each within-section boundary now genuinely continues pose/lighting/framing from the literal previous frame instead of resetting.
Ester Beat 4-5 (E11-E19) chain: 8 new generations (E12-E19; E11 reused unchanged). Credits: 8x12=96. Running total for the whole rebuild: 108 (Ester1-2) + 48 (Anathi) + 96 (Ester4-5) = 252 credits.
VERIFIED:
- ffprobe spec/duration match original raw cut exactly (145.055s vs 145.06s -- same).
- volumedetect: mean -25.5dB, max -3.3dB (real audio, not silent).
- All 21 within-section cut points (9 in Ester1-2, 4 in Anathi, 8 in Ester4-5) visually inspected via before/after contact sheets -- pose, expression, lighting all match cleanly, no ghosting or resets.
- Both legitimate character-switch cuts (E10->A1 at ~60.4s, A5->E11 at ~90.6s) visually inspected -- correct character each side, clean hard cut (these are SUPPOSED to be hard cuts, different people).
This REPLACES ALL-CLIPS-RAW_24of24.mp4 as the answer to "where is the finished video" -- the raw version is left in place for comparison, not deleted.
Still NOT done (unchanged from before): 4 UI screen-capture inserts, on-screen captions, background music/SFX, final logo card. These are a separate edit pass on top of this footage.
One process note for any future Higgsfield chain work: the start-frame upload slot intermittently fails to visually/functionally update when replacing an already-loaded image in the same page session (silent failure). The reliable fix used throughout: fully reload the page before each upload (so the slot starts empty) and confirm the correct face is showing via a zoomed screenshot of the small reference thumbnail BEFORE clicking Generate, every single time. This caught one wrong-reference generation before it wasted a download (not used, not counted above).

## Known open items
- ASPECT RATIO: Kling 3.0 on Higgsfield only proven at 9:16 today (no 16:9 option seen). All howto-library videos are 9:16 already; the one 16:9 video (introduction_v2.mp4) was assembled from REUSED old Veo-era clips, not fresh Higgsfield output. Plan: shoot native 9:16, then decide pillarbox-to-16:9 vs native-vertical-on-YouTube at edit time.
- UI screen inserts (Trust Score profile card, Tutors browse + filter, request-intro flow, incoming-requests list) not yet built — per project convention these are rebuilt as local HTML mockups (Playwright), not live captures.
- Voice/TTS canon from introduction_v2 QC applies if any VO is re-recorded outside Higgsfield's built-in voice: en-GB-RyanNeural +4%, en-ZA-Luke banned, lowercase emphasis words for TTS (caps reserved for on-screen text).
