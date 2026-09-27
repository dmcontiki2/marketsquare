## 2026-09-23 — David's go: languages ON, one-tap publish, ONE Quick door, arrival, free-lane AI cap (RUL-163 / RUL-164)

- LANG-ON-1: migration 049 arms `launch_switches.lang_layer` for everybody (audited row; reversible via /admin/flags).
- ONE-TAP-PUBLISH-1: `POST /listings/quick-publish` (not under /quick/ -- nginx serves that prefix as the app file; the first cut answered 405, caught by the live probe) creates the advert, records the terms accepted by the tap, and publishes it in one call; a signed-in member publishes as her session; slot limit, velocity and price-basis guards stand; a "your advert is live" letter carries her way back.
- QUICK-ONE-DOOR-1: the reworked app is promoted into `quick.html`; the manifest serves it for every `/q/<category>` too (category from the path); `/quick_next.html` 301s to `/quick/`; `genie/HARNESS.html` kept identical to `quick.html`; `genie/q_index.html` retired.
- ARRIVAL-1: after the tap her photo and title rise into a finished card with a tick, then "See my advert" and a WhatsApp note to herself (reduced motion respected).
- QUICK-I18N: the draft, publish and arrival words drafted in isiZulu, isiXhosa, Afrikaans and Sepedi (RUL-160 readers).
- RUL-164: the advert's second-language draft (a free feature) counts against the translation lane's daily ceiling and a 5-a-day per-advert cap.
- Ledger: RG-0413/0414/INTL door entries now read quick.html (the one door); RG-0414 and RG-0436 LOCKED; RG-0435 re-aimed at /quick/; RG-0438 (OPEN until measured live), RG-0439 LOCKED.
