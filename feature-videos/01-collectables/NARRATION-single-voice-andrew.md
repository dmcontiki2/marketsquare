# Collectables advert — AS DEPLOYED (v2-dry), live 2026-06-30

Live file: /static/videos/collectables-advert-howto.mp4  (cache tag ?v=20260701)
Server: root@178.104.73.239:/var/www/marketsquare/static/videos/  · 12,039,278 bytes · 60.5s · dry (no music bed)
Approved by David 2026-06-30. Built 100% free (edge-tts + ffmpeg), zero Flow credits.

## Voice design (what actually shipped)
TWO voices, by deliberate choice after iterating with David:
- ON-CAMERA shots keep their ORIGINAL Flow audio (perfect lip-sync). This preserves the
  girlfriend's two lines in HER real voice: "Try TrustSquare" (end of hook) and "Told you" (payoff).
- The four faceless UI screens are narrated by Andrew (edge-tts en-US-AndrewMultilingualNeural,
  rate +5%) — no lips to sync, so no drift.
  (An earlier "single Andrew voice over everything" version was rejected: dubbing the talking
   on-camera shots caused lip-sync drift + dead air. Keeping original on-camera audio fixed it.)

## Beat map (live order)
| # | Beat (clip) | Voice | Line |
|---|---|---|---|
| 1 | Hook (n01) | ORIGINAL | guy: cards-to-sell hook · HER: "...Try TrustSquare." |
| 2 | Desk · 6 cards (b_desk, UI) | ANDREW | "So here they are — all six. Gaea's Cradle, Tundra, Plateau, the Vesuvan Doppelganger, Swords to Plowshares, and the Veteran Bodyguard." |
| 3 | Snap/walkthrough (n03) | ORIGINAL | guy snapping each card |
| 4 | Report scroll (b_report, UI) | ANDREW | "And there's the report — my whole collection, forty-two thousand five hundred rand. Gaea's Cradle alone, almost twenty-five thousand. Every card valued and priced to sell." |
| 5 | Payoff (n05) | ORIGINAL | guy: "Twenty-four thousand..." |
| 6 | Payoff 2 (n06) | ORIGINAL | HER: "Told you." + guy |
| 7 | Choice lead-in (n08_choice) | ORIGINAL | guy: choosing how to list |
| 8 | Choice screen (b_choice, UI) | ANDREW | "I'll take the combined option — all six listed together as one collection." |
| 9 | Live listing (b_final, UI) | ANDREW | "Wow — look at them. All six, advertised globally, at forty-two thousand five hundred rand. Impressive." |
| 10 | Logo sting (n07) | original | (no VO) |

## Deploy notes (2026-06-30)
- Cloudflare purge token in /var/www/marketsquare/.env is DEAD ("Authentication error"); /admin/purge-cache
  is a silent no-op. Cache was busted by bumping this video's tag (?v=20260630n -> ?v=20260701) and
  re-shipping ms.js (ms.js?v=211 -> 212). HTML is DYNAMIC (uncached) so it propagated immediately.
  TODO for David: rotate the Cloudflare cache-purge API token so normal purges work again.
- Local masters synced to live: feature-videos/01-collectables/collectables-advert-howto.mp4 and
  videos/collectables-advert-howto.mp4 (timestamped .bak files kept beside each).

SUPERSEDES: VO-EXPANSION-script-30jun.md (Luke experiment) and the full-single-voice Andrew draft.
