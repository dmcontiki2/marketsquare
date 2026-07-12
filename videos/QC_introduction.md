# QC — introduction.mp4 (in-app introductions explainer)
Run: 2026-07-12 · 64.0s · 1280x720 · 25fps · h264+aac · 8.2MB

VERDICT: FIX — 3 fixes, 3 notes

| # | t | severity | issue | evidence |
|---|---|----------|-------|----------|
| 1 | 36.6s | FIX | Caption overflows BOTH screen edges — "…urity and trust verifier…" unreadable, worse on mobile | frame f08 |
| 2 | 59.5s + outro | FIX | Same overflow on closing line — "…verified seller…service we provid…" cut off | frames f13/end |
| 3 | 3.4–5.8, 8.1–11.4, 24.6–27.4, 33.3–34.9, 46.6–48.9 | FIX | Five dead-air gaps ≥1.6s, total 12.4s = 19% of runtime — the measured "slow" | silencedetect |
| 4 | throughout | NOTE | Style whiplash: cinematic AI segments (0s, 4.6s, 50.3s) alternate with flat slide graphics (9s, 23s, 27s, 36s) — the "too obvious" transitions | frames |
| 5 | 27.5s | NOTE | Trust-square renders as a grey placeholder-looking block | frame f06 |
| 6 | cinematic segments | NOTE | Veo watermark bottom-right on generated shots | frames f00/f01/f11 |

Duration vs script: render 64s vs script v1's ~80s plan — narration compressed but the pause structure kept, which concentrated the dead air.

Keepers: the faces+orb open (4.6s) and the handshake (50.3s) are genuinely strong — REUSE, don't regenerate (candidates already on disk: open.mp4 / handshake.mp4 / reveal.mp4 in Projects root).
