# TrustSquare Feature-Ad Format (v1) — the "Hook · Sting · Show · Payoff" template

Every feature video follows the same 5-part structure, 9:16 portrait, 720x1280+, Omni Flash in Google Flow.

| Part | Length | Source | Content |
|------|--------|--------|---------|
| 1 · HOOK | ~8s (1 Flow clip) | Flow | Two people, real-life problem, natural dialogue. Ends with the other person recommending TrustSquare. |
| 2 · STING | 1.6s | `production-kit/logo-sting-1.6s.mp4` (prebuilt, free) | Logo scale-in + chime. |
| 3 · WALKTHROUGH | 25–40s | Flow presenter clips + UI inserts | The existing tutor style: presenter narrates each step, intercut with real app screens (form fill → run → report scroll). Maroushka's edit list applies here. |
| 4 · PAYOFF | 8–16s (1–2 Flow clips + 1 UI insert) | Flow | The outcome demonstrated in the app (listing live, route mapped, plan pinned), hero says the thank-you line. |
| 5 · STING out | 1.6s | same sting | Logo, then cut back to the app. |

Total: 45–70s per feature. Shorts: Hook + Sting + one walkthrough beat + Payoff line, cut to 7–15s.

## Consistency rules
- Every Flow generation attaches the feature's CAST reference still (generate each cast still ONCE in Flow image mode — Nano Banana, ~0 credits — save to `production-kit/cast/`).
- Style line for all prompts: "warm natural light, handheld vlog feel, shallow depth of field, 9:16 vertical."
- Dialogue inside quotes, max ~22 words per 8s clip; one sentence per clip.
- Settings: Video → Ingredients → 9:16 → 1x → Omni Flash → 8s (12 credits; 6s=10, 4s=7 at mid-2026 promo pricing).
- UI inserts are FREE (rendered from rebuilt app screens — see `production-kit/inserts.py` pipeline). One per feature: form + example report (+ payoff screen).
- South African flavour where natural (Pretoria launch city) — places, prices in R, local trips.

## Per-video credit budget
Hook 1 clip + walkthrough 4 clips + payoff 2 clips = 7 clips ≈ 84 credits; with 30–50% retake margin ≈ **110–130 credits per feature video**. Ten features ≈ **1,100–1,300 credits** — size the Flow subscription tier on this (stings + all UI inserts cost nothing).

## Production order per video
1. Generate cast stills (image mode) → save to cast/.
2. Generate hook clip → review → payoff clips → walkthrough clips (reuse tutor presenter where the script keeps him).
3. Rebuild that feature's form + example report HTML (clone form.html/report.html pattern), render inserts via inserts.py.
4. Stitch: hook + sting + walkthrough + payoff + sting (ffmpeg concat, all normalized 720x1280@30 / 44.1kHz).
5. Verify: whisper transcript for line order + boundary frames.
6. Wire into app: one line in `AI_VIDEOS` map in ms.js + deploy video to `/static/videos/`.

## Maroushka's lane
Segments are modular MP4s — swap, retime, or re-edit any part without regenerating the rest. Keep her edit list per video in `scripts/<nn>-<feature>-EDITS.md`.
