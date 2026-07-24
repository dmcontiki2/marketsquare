# QC — heritage-tour-howto.mp4 (map-fix re-render, 23 Jul 2026)

```
VERDICT: SHIP
```

Re-render scope: report-scroll segment (48.4s → end) re-rendered against the corrected
report (route figure now scales — the "Namibia crop" bug is gone). Presenter/couple
clips 0–48.4s and the FULL audio track are byte-identical to the previous cut.

## Probe
- 720x1280 @ 30fps h264 + aac, duration 136.407s (matches previous cut to the ms)
- 9,600,790 bytes (~9.6 MB; previous cut was 9.0 MB) · 563 kbps overall

## Checks
| # | t | severity | result |
|---|------|----------|--------|
| 1 | all | — | 20 frames sampled + first/last 2s: no black/blank frames, no placeholder text, no stuck frames |
| 2 | 48.4 | — | splice point clean (logo sting → report top, same cut style as original) |
| 3 | 49–112 | — | route map shows FULL Cape Town→Kruger route everywhere; Namibia crop confirmed gone |
| 4 | 67–94 | NOTE | narration-to-section sync improved vs original: exec-selection table under "three ways side by side", toll table under the plaza narration |
| 5 | 96–106 | — | cost table on screen during cost narration |
| 6 | 106–118 | — | scroll returns to route map on "Every stop is mapped — Colesberg, Dullstroom, Graskop…" |
| 7 | 134–136.4 | — | ending holds on "Tap any stop to navigate" + report title; not mid-sentence; 2.3s tail matches original |
| 8 | audio | — | track copied from previous cut unchanged; silences at 16.2/33.0/47.4/61.1/134.1s — identical profile; whisper transcript verified in order |

Snags: none blocking. NOTE #4 is an improvement, listed for the record.

Pipeline: report HTML from live /ai/example/heritage_tour (result_html) rendered in
headless Chromium at 720px, narration-timed scroll schedule (waypoints eased), spliced
over original audio, two-pass x264 to size budget. Built in Cowork session 23 Jul 2026.
