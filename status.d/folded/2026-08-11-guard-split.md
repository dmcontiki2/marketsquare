- **GUARD-SPLIT-1 — pre-launch autonomy is now available without dropping the trust core.**
  `MAINT_PHASE` was controlling both the design lane (the autonomy David wants) and the
  identity/auth/kyc/schema/safety refusals (which nobody asked to drop). Split them:
  `TRUST_CORE_GUARD` defaults ON in **both** phases; `MAINT_PHASE` now only decides whether
  design changes are implemented or batched. **RG-0056 LOCKED.**
- **Why now:** the 9 Aug "no real users/sellers/money" premise has expired — three real
  reporters, and Maroushka's live listing 335 with 8 real photos. Evidence: the B4 storm at
  prelaunch failed **2/6** before the split (SYN-ANON and SYN-SAFETY routed PATH_B instead of
  escalating) and passes **6/6** after, banner reading `phase=prelaunch trust-core=GUARDED`.
- **B4 Tier 2 PASSED on the server, 06:45 UTC** — first time the brain has ever answered
  (`brain[anthropic/claude-haiku-4-5-20251001]`), real model's patch gated green end-to-end,
  commit withheld. The earlier 06:42 "NOT READY" was invalid: the server was still on 9cc3725,
  one commit behind BRAIN-PATH-1, so it re-ran the import bug.
- **Arming is now David's single act, and the config to use is `MAINT_PHASE=prelaunch` with the
  trust-core guard left at its default.** Two items still outstanding before the runbook's own
  gate is satisfied: `static/maint/b4_tier2.json` returns **404** (migration 011 has never run —
  it fires from `post_deploy.sh` on a *deploy*, and only `main` has been pushed), and Tier 2 has
  not yet been run in prelaunch mode to prove the design lane actually routes PATH_A.
