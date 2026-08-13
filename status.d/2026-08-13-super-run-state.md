- SUPER-RUN STATE (13 Aug, live counter — updated as the run advances): journey photos
  **164/164 COMPLETE** (MZ final 7 claimed this morning; map rebuilt 32/32 embedded;
  RG-0062 locks the report-widget class in journey_template.html). Kenya super stills:
  **advexp a+b+c COMPLETE (24/114)** — Naivasha, Nairobi NP, Maasai Mara sets all in
  assets/super/. RESUME RECIPE for the 90 remaining: /tmp/super_queue.json rebuilds from
  SUPER_LADDER_PROMPTS.md (make_super_prompt_pack extraction in this session's log);
  next item = index 24 (sup_ke_advacc_a_1_*). Method that works: JS-dispatched clicks
  ONLY (coordinate-free — window resizes don't matter): focus editor via .focus(),
  ctrl+a + type action, verify textContent, JS-click Generate, poll 70s in 10s waits,
  JS-click newest tile (left<480, top>50, w>250), verify lightbox text has the SHOT
  phrase + LISTING name, JS-click Download, bash-poll Downloads for hf_*.png newer than
  per-image floor, `python3 scripts/claim_super.py --since <floor> <name.jpg>` (new
  helper, same hard guard as claim_photos). NSFW rewords banked in
  status.d/2026-08-13-mz-run-prompts.md. EVENING (David): media_push.bat → release.bat
  — post_deploy seeds whatever tiers have full photo sets on disk (proven no-op-safe).
