# Session handoff — Feature videos + report enrichment (29 Jun 2026)

## DONE today (all verified on disk / live on server)
- **10 real Feature reports** generated live on Hetzner, saved in `real-reports/`.
- **Live engine enrichment** (advert_agent.py + report_images.py, deployed + healthy):
  every route report gets a REAL OSM road-route map (national roads, flight arcs for air legs),
  CLICKABLE Google-Maps pins + "open full route" button, and a GEO-VERIFIED licensed place photo.
  Item features: Car = real model photo (Wikimedia), Collectables = real card (Scryfall),
  Study/Offer = no photo (no correct subject). HTML-primary, markdown fallback. `result_html` column added.
- **The "403 bug" SOLVED** = it was the Pro-plan gate (ai_service_tiers.tier_may_run), NOT a key bug.
  Made dormant while no paid feed is live (auto-reactivates when one is contracted). See THE_403_TRUTH.md.
- **5 missing clips** generated (retirement husband x3, exam mom, exam student-payoff), downloaded, stitched.
- **All 10 feature videos FINAL** with real-report inserts (form -> real report scroll -> real payoff),
  script-beat order, 720x1280, AAC audio, 44-59s. David VIEWED ALL 10.

## TOMORROW — pick up here
1. **Fix David's 2 minor items** (from his review — ASK HIM what they are; not yet recorded).
2. **Higgsfield 4K upscale** experiment on one finished video (or redo Intro), then the rest.
3. **Place videos back in the app**: AI_VIDEOS map in ms.js + deploy videos to /static/videos/ via
   deploy_marketsquare.bat (cache-bust the version string).

## Notes / small follow-ups (not blocking)
- Reports occasionally truncate mid-JSON when long (model hits max_tokens on the waypoints appendix).
  Parser salvages it, but bump token budget or move waypoints block earlier when next in the engine.
- I (Claude) cannot see/hear playback — lip-sync/clip-order checks are David's.

## Key paths
- FINAL videos: feature-videos/<nn>/<name>-AD-FINAL-28jun.mp4 (01 = 01-Collectables-FINAL.mp4)
- Real reports: feature-videos/real-reports/
- Insert renderer: /tmp/insrender/ (render_inserts.py + build_all.py) — regenerate if needed
- Server: root@178.104.73.239 via repo SSH key MarketSquare/.ssh/id_ed25519 (passwordless)
