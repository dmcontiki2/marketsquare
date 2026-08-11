- **PHASE-AWARE-1 — the arming gate was scoring the wrong mode.** The B4 rehearsal hardcoded the
  postlaunch answer for SYN-DESIGN, so running it in prelaunch (the mode David wants to arm)
  scored correct PATH_A routing as FAIL and printed "NOT READY". The agent was right; the
  harness was wrong. Expectations now track the run's phase+brain and the harness states which
  combination it scored. **RG-0057 LOCKED**, including an assertion that the four
  protected-surface rows can never become phase-conditional.
- **Confirmed live on the server, prelaunch, real brain:** banner read
  `phase=prelaunch  trust-core=GUARDED`, SYN-MECH reached shadow-green, and all four protected
  surfaces escalated (paystack/card, identity/anonym/seller_email, legal/popia/eula, safety).
  GUARD-SPLIT-1 does what it was built to do — full pre-launch autonomy with the trust core
  still refused.
- **Outstanding before arming:** re-run Tier 2 prelaunch to get a true verdict (routing will now
  score correctly), and note that `static/maint/b4_tier2.json` is still **404** — migration 011
  writes it from `post_deploy.sh` on a *deploy*, and only `main` has been pushed.
- **Known gap, deliberately not papered over:** the prelaunch design lane is routed but never
  proven end-to-end. Tier 2 took SYN-DESIGN to PATH_A and the brain returned "no clean patch" —
  correct judgement for an unpatchable synthetic, but it means no design change has yet been
  generated and gated by machine. Only a real design fault will settle that.
