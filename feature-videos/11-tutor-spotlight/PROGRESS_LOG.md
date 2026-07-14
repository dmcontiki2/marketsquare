# Tutor Spotlight video — generation progress log
Pipeline: Higgsfield (higgsfield.ai, greenswan1646, Ultra Plan). Image: Nano Banana Pro (2 credits/portrait). Video: Kling 3.0, 9:16, 720p, 6s (12 credits/clip).
Credits at session start: 1,570.

## STATUS as of this session (13 Jul, ~18:11)
**9 of 24 clips done, downloaded, and verified** (E1-E9, all Ester). Both cast portraits generated and confirmed on-brief. Credits spent: ~94 of 1,570 (plenty of runway left — 3-min video priced at ~300 total per Higgsfield's own cost guide).
Remaining: E10-E19 (10 more Ester clips) + A1-A5 (5 Anathi clips) = 15 clips left, all prompts already written below, ready to fire in the same session/routine (reference image still attached, Kling 3.0 / 9:16 / 720p / 6s settings unchanged).
Working routine (proven, repeat for each remaining clip): click prompt box -> Ctrl+A -> type new prompt -> Generate (12 credits) -> wait ~60-100s -> click the finished thumbnail once to reveal heart/copy/download icons top-right of the card -> screenshot to CONFIRM icon position before clicking download (icon Y-position has drifted between 99 and 151 across the session -- always confirm, don't blind-click) -> verify a new file landed in Downloads by mtime before filing it into clips/ with the matching name from the table below.
Not yet started: Anathi's clips (need to re-attach her reference image via Assets -> her portrait -> Turn to video, since the panel is currently still on Ester's reference), the real UI screen-insert captures, and ffmpeg stitch.

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
| E11 | Ester | "The introductions come to me now, and I choose." | pending | |
| E12 | Ester | "I look at where they are. I drive to their homes, so nearby matters." | pending | |
| E13 | Ester | "And I look at their side of the square. Buyers carry a score too." | pending | |
| E14 | Ester | "Anathi was close, verified, serious. I accepted before my tea went cold." | pending | |
| E15 | Ester | "Two mornings a week now. Her trig is coming right." | pending | |
| E16 | Ester | "TrustSquare didn't teach her trigonometry. I did." | pending | |
| E17 | Ester | "It stood between two strangers and said: she is who she says she is. And so is he." | pending | |
| E18 | Ester | "One introduction. One tuppence. That's the service. Nothing more, and nothing less." | pending | |
| E19 | Ester | "Because the introduction isn't a feature of TrustSquare. It is TrustSquare." | pending | |
| A1 | Anathi | "I typed 'maths tutor.' Got hundreds. Anyone can write 'twenty years experience' - how would I know?" | pending | |
| A2 | Anathi | "So I filtered. Local Market: Wellington, walking distance, my ma insisted." | pending | |
| A3 | Anathi | "Then Trusted-plus, seventy and up. There's a gold button too, Highly Trusted, ninety." | pending | |
| A4 | Anathi | "Suddenly it wasn't hundreds. It was a handful. One of them was Aunty Ester, eleven minutes away." | pending | |
| A5 | Anathi | "I didn't send a message into the dark. I requested an introduction. That's different." | pending | |

## Known open items
- ASPECT RATIO: Kling 3.0 on Higgsfield only proven at 9:16 today (no 16:9 option seen). All howto-library videos are 9:16 already; the one 16:9 video (introduction_v2.mp4) was assembled from REUSED old Veo-era clips, not fresh Higgsfield output. Plan: shoot native 9:16, then decide pillarbox-to-16:9 vs native-vertical-on-YouTube at edit time.
- UI screen inserts (Trust Score profile card, Tutors browse + filter, request-intro flow, incoming-requests list) not yet built — per project convention these are rebuilt as local HTML mockups (Playwright), not live captures.
- Voice/TTS canon from introduction_v2 QC applies if any VO is re-recorded outside Higgsfield's built-in voice: en-GB-RyanNeural +4%, en-ZA-Luke banned, lowercase emphasis words for TTS (caps reserved for on-screen text).
