## 2026-08-30 — Red/amber cleanup pass (David: "clean and close the red; close the ambers or give workarounds")

Coverage board 47/2/10/1/7 -> **49 green · 3 blue · 4 amber · 1 red · 10 grey**.
- **GREEN:** FEA baseline (DW-064 closed, probed ok/[]) · cost sweep — reference-doc exemption BUILT in cost_compliance_sweep.py (5 named docs read INFO not WARN; exact filenames, sonnet-branch only; opus + any other file still full severity) — **sweep exit 0, first fully-clean board**.
- **GREY with reasons on file:** both gate-era cards (product public by design, RUL-001 — RG-0090 stays open in the ledger as the class record) · watch desktop-bound (RUL-070(c) accepted residue).
- **BLUE:** failover destination — PROBED server-side: OPENAI_API_KEY + GEMINI_API_KEY both live in the app env = two non-Anthropic lanes to move to; turns green by assertion when MS_API_KEY lands in .secrets/ops_api_key.txt (David's batch).
- **AMBER (4, each with its stated path):** sample rows + Monday lint (fixed, awaiting closing checks) · connect-src (DRAFT_034 migration staged — allowlist to be MEASURED from live traffic 2 Sep, not guessed on launch weekend) · five gate-script copies (post-launch consolidation; RG-0074 LOCKED polices drift meanwhile).
- **THE RED (DW-078):** fix built + verified (16/16 harness); the deploy hook was triggered but re-shipped the OLD ref — the sandbox holds no GitHub push credential, so publishing the ref is David's click (deploy_marketsquare.bat). Closes on the first post-deploy probe; RG-0198/RG-0211 promote on READY TO LOCK.
- DAVID'S BATCH: (1) the deploy push · (2) MS_API_KEY -> .secrets/ops_api_key.txt · (optional, durable) a push-scoped GitHub PAT for the sandbox so "close it for me" can ship end-to-end next time.
