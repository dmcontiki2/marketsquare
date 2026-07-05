# Video QC — all 10 FINALs checked (2 Jul 2026, two parallel agents, read-only)
All: 720x1280@30fps H.264 + AAC 44.1k. QC frames: Cowork outputs/vidcheck/<id>/ (4 per video).

## Scorecard (sharpness = laplacian var; presenter <30 = soft; inserts 700–4300 = crisp)
| # | video | dur | v-kbps | audio mean/max dB | presenter | insert bugs |
|---|---|---|---|---|---|---|
| 01 collectables | FINAL | 45s | 1436 | −26.6/−3.9 | soft (41/53) | none |
| 02 heritage | 28jun | 51s | 1081 | −25.9/−2.5 | ok (98/99) | tofu glyphs, title clip |
| 03 expedition | 28jun | 45s | 1026 | −27.2/−3.4 | SOFTEST 01-05 (~9) | title clip (cosmetic) |
| 04 property | 28jun | 45s | 1310 | −25.8/−4.5 | soft (37); mushy keyboard | subtitle overlap |
| 05 car | 28jun | 45s | 1291 | −26.6/−3.1 | soft (21–29) | title clip (cosmetic) |
| 06 retirement | 28jun | 56s | 2099 | −30.0/−3.7 | best of set (57–91) | none — fine as-is |
| 07 liquidation | 28jun | 44s | 1218 | −29.2/−4.3 | soft (18–40); garbled phone UI | DOUBLED HEADER + BLACK VOID |
| 08 weekend | 28jun | 44s | 1233 | −27.0/−4.3 | SOFTEST of all (5–15) | RAW MARKDOWN LEAK + overflow + tofu |
| 09 exam | 28jun | 54s | 987 | −28.1/−3.4 | soft (7–23); garbled badge | 3 tofu + truncations |
| 10 offer | 28jun | 44s | 1019 | −26.4/−3.6 | soft (11–15); BEATS-style logo | WORST: doubled header + md URL + 60% void |

## Cross-cutting
1. Audio uniformly QUIET (−26..−30 mean vs −16..−20 social norm) → one batch loudnorm pass at restitch fixes all.
2. Insert-renderer bug family (same renderer, /tmp/insrender per 29-Jun handoff): doubled-header+void (07,10), markdown leak (08,10), tofu/emoji (02,08,09) → fix renderer (emoji font + md strip + header/height bug), re-render — FREE, no credits.
3. Inserts are otherwise razor-sharp; upscale spend belongs ONLY on presenter clips.
4. No higher-res sources exist anywhere (all clips 720x1280) except 02-heritage 4k_clips/: hook+wt1+3 inserts DONE at 2160x3840, 2 more staged (upload_*) — reuse, never redo.
5. Masters need higher-bitrate re-export when restitched (1.0–1.4 Mbps is low for masters; 06 at 2.1 ok).
6. 10-offer trademark exposure (Beats-style logo) → blur in post (free) or clip regen (credits) — David's call.

## Upgrade worklist (priority order)
10 offer (insert re-render + upscale 5 + logo fix) → 07 liquidation (insert + 5) → 08 weekend (insert + 5)
→ 03 expedition (5–6) → 09 exam (insert glyphs + 5) → 05 car (5) → 04 property (5) → 01 collectables (5)
→ 02 heritage (remaining ~6, incl. 2 staged) → 06 retirement (optional polish only).
Credit estimate: ~50 presenter-clip upscale ops total (~5/video, 06 excluded) at Higgsfield; confirm actual
per-op cost on the first video before batch. Free work first: renderer fix + re-renders + loudnorm plan.

## Phase-2 plan (per established way of working)
1. FREE pass (sandbox): fix insert renderer, re-render broken inserts (07/10/08/09/02), stage.
2. Template video end-to-end LIVE with David's Higgsfield tab: 10-offer (worst case = best template):
   upscale 5 clips → new insert → logo blur → restitch 4K/1080 master + loudnorm → David reviews.
3. Overnight scheduled runs for the rest per OVERNIGHT_RUN pattern (log + morning report, credit-gate:
   stop + surface if credits low). 02-heritage completes from its staged uploads. 06 skipped unless wanted.
