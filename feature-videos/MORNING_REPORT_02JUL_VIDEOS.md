# Morning report — TrustSquare feature-video 4K upgrade (scheduled run, 02 Jul 2026)

## Bottom line
**All 9 target videos have new 4K masters on disk.** 06-retirement skipped per plan.
Credits: **21 spent** (1,988 → 1,967) across 47 ByteDance-Standard 4K/30fps upscale ops (~0.4–0.8 cr each — far under the ~50-credit estimate).
No existing file was modified; every output is a NEW file. Originals untouched.

## Per-video status
| # | video | master (in video folder) | dur vs orig | specs | notes |
|---|-------|--------------------------|-------------|-------|-------|
| 10 offer | ✅ | offer-FINAL-4K-02jul.mp4 | 44.468 / 44.470 | 2160x3840@30, 9.4Mbps, 52MB | FIXED scroll insert; **logo blur applied** (see below) |
| 07 liquidation | ✅ | liquidation-FINAL-4K-02jul.mp4 | 44.468 / 44.470 | 9.6Mbps, 53.5MB | FIXED scroll insert (doubled header/void gone) |
| 08 weekend | ✅ | weekend-FINAL-4K-02jul.mp4 | 44.468 / 44.470 | 9.9Mbps, 54.8MB | FIXED scroll insert (md-leak/tofu gone) |
| 03 expedition | ✅ | expedition-FINAL-4K-02jul.mp4 | 44.468 / 44.470 | 9.7Mbps, 54MB | own inserts kept (QC: cosmetic only) |
| 09 exam | ✅ | exam-study-plan-FINAL-4K-02jul.mp4 | 54.468 / 54.467 | 10.0Mbps, 68MB | FIXED scroll insert (tofu gone); 10s mom + 10s payoff segments |
| 05 car | ✅ | car-FINAL-4K-02jul.mp4 | 44.468 / 44.470 | 9.5Mbps, 52.7MB | own inserts kept |
| 04 property | ✅ | property-FINAL-4K-02jul.mp4 | 44.468 / 44.470 | 9.5Mbps, 53MB | own inserts kept; hook order woman→man verified |
| 01 collectables | ✅ | collectables-FINAL-4K-02jul.mp4 | 45.334 / 45.335 | 10.9Mbps, 62MB | 6 presenter clips AI-upscaled; report/UI screens lanczos (kept text crisp) |
| 02 heritage | ✅ | heritage-FINAL-4K-02jul.mp4 | 51.268 / 51.275 | 9.9Mbps, 63.7MB | FIXED scroll insert (tofu gone); rebuilt from TRUE sources (see below) |
| 06 retirement | ⏭ skipped | — | — | — | per plan (best of set, fine as-is) |

All masters: H.264 2160x3840@30, AAC 44.1k, **two-pass loudnorm to −16 LUFS / TP −1.5** (verified −15.7…−16.2 on output; originals were −20…−23.5).

## Verification done per master (my checks — sandbox, no playback)
- ffprobe specs + exact frame counts per segment (all segments frame-exact vs cut map).
- Beat-alignment: 9–11 probe timestamps per video, downscaled-frame MSE vs original FINAL — same beat order everywhere; synthetic segments (logos/inserts) MSE ≈ 1.
- Insert frames extracted + visually checked: clean headers, no tofu, no black void, no raw markdown (10/07/08/09/02 got the FIXED scale-3 render; math glyphs in 09 render correctly).
- **YOUR check (I can't hear/see motion): lip-sync + playback quality on all 9, and the 10-offer blur.**

## 10-offer trademark blur (David review)
Beats-style "b" was CLEARLY legible on the wt1 cup and faintly on hook/payoff after upscale. Applied strong boxblur (24:2), full-clip, 4K-pixel regions:
- 10-hook-buyer & 10-wt1-buyer: x520 y2060 340x280
- 10-payoff-buyer: x500 y2020 340x300
- 10-wt2-buyer: logo face not visible → NO blur.
Check the cup area on playback; if a flash of logo remains anywhere, tell me the timestamp and I'll widen the window.

## 02-heritage: why it was rebuilt differently
The 29-Jun 4K assets (hook_4k, wt1_4k) and the two staged uploads turned out **time-shifted ~0.1–0.2s and slightly reframed** vs the segments actually in the FINAL — would have caused visible lip-sync error. I re-upscaled the four true source clips from clips/ (~2.4 credits) and used those; beat alignment went from MSE ~1500 to ~5-100. The two staged-upload results (upload_*'s upscales) are on disk in 4k_clips/ but deliberately unused. The 29-Jun "unsupported content" failures did NOT recur — both retries succeeded, so that was transient.

## Process notes (for the next run)
- Retrieval solved WITHOUT Downloads mount: read result mp4 URL from the player (d8j0ntlcm91z4 domain = result; d2ol7… = source preview) → curl into repo.
- Browser gotchas: sidebar '+' goes stale after ~10 job cycles → hard reload /upscale (Ctrl+Shift+R or fresh query param); after reload use the CENTER Upscale button (element-ref click, not coordinates).
- Upscale cost scales with clip length: ~0.4 cr per 5s clip, 0.64 per 8s, ~0.8 per 10s.
- n04_report (01) and other UI/report screens deliberately NOT AI-upscaled (text hallucination risk) — lanczos x3 keeps them pixel-crisp.
- Insert renderer copy patched with --f0/--f1/--encode chunking (sandbox 45s limit); scale-3 renders live in inserts_fixed_02jul/scale3/.
- Full job-id ↔ clip log: RUN_LOG_2026-07-02.md.

## How to resume / redo anything
- Per-video assembly specs: /tmp is wiped, but every cut map + spec is reproducible from RUN_LOG + this report; recon script pattern documented in RUN_LOG.
- To redo one segment: re-run the upscale on the source clip, then re-stitch that video (cut maps in RUN_LOG; all segment frame counts logged).
- Deploy step (ms.js AI_VIDEOS map + /static/videos/) NOT touched — per handoff that's a David+Claude supervised step.
