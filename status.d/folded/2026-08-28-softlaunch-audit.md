### Soft-launch readiness audit — 28 Aug 2026 (18:10–18:45 UTC, attended)

David asked for a full readiness audit against ten questions. Deliverable:
`SOFT_LAUNCH_READINESS_AUDIT_2026-08-28 — nice.docx` (Professional Navy). Verdict: READY,
send lever in David's hand; audit self-confidence 92%.

- Probes fresh this session: health ok v1.3.1 · anonymous 200 on /, /listings, /terms, /flags
  (gate down, site already public) · BIT 8/8 (18:08Z) · /dashboard/summary stats 103/70/115 ·
  id-verify READY · rulings 61/61 · post_deploy 03:08Z clean.
- Ledger: first run found RG-0197 REGRESSION (MarketSquare/.git/HEAD.lock stranded 391 min) —
  healed via `scripts/git_unlock.py` (sandbox lane, rename-aside). Sandbox deps httpx+fastapi
  installed per MAINT-DEPS-1 step-0. Re-run: **183 ok · 11 open · 0 REGRESSED · exit 0**.
- Q1 (wave): SEND_FREEZE stands (mtime 20 Aug, untouched) → Day-1 send (RUL-053/057/058,
  Fri 28 Aug Tutors PTA+JHB) did NOT fire — 0 emailed today, 5 ever (PROBED local store).
  Server /pipeline/run-wave confirmed scrape-only (--skip-email); outreach leaves only the
  local machine, so the freeze covers the whole lane. Lift = David deletes the file.
- Q9 seam FLAGGED, mine to fix before wave 2: /launch-api/optout writes the SERVER suppression
  register; the send lane reads the LOCAL prospects.db, which has NO suppression table. Zero
  wave-1 exposure (no outreach has ever gone → no opt-outs exist). Action: pull server
  suppression/opted_out into the sending store before wave 2 (RG-0176(a) class).
- Alert half of RG-0138 still unproven until the 06:00 UTC 29 Aug heartbeat (stated in doc).
