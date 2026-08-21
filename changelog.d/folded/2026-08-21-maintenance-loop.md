## 2026-08-21 — maintenance-loop (B2b brain, daily run)

- **Regression ledger: GREEN before and after.** Every LOCKED entry holding; 3 known
  defects still OPEN (RG-0121 photo-anon canary not armed; RG-0132 openai absent from
  GOLDEN_PASS; one further open entry). No regression to chase — no top item.
- **Shadow maintenance agent ran clean in the foreground** (BRAIN-DEPS-2 pattern; httpx
  installed into the sandbox first). `mode=SHADOW (kill switch OFF)`, phase=postlaunch,
  trust-core=GUARDED, rate<=3/h, brain KEYED:anthropic. Report:
  `.maint_agent/run_20260821T053334Z.json` — **0 seen, 0 acted**.
- **Heartbeat confirmed posted.** `GET /dashboard/maint` (read through the ts_review
  credential, migration 018 still not on the box) returns this run:
  `run=2026-08-21T05:33:34Z, received_at=2026-08-21T05:33:49Z, brain_keyed=true,
  brain_lane=anthropic, seen=0, acted=0` — the B2b readiness row on the dashboard is fed.
- **Fault queue empty of work.** `/admin/faults` counts: new 0 · triaged 0 · fix-shipped 0
  · verified 26 · closed 7. No SHADOW "gates GREEN, patch ready" rows, no PATH_B routes,
  no escalations — nothing to patch, so no fixes, no AIK-VERIFY-1 evidence rows and no new
  ledger entries were due this session.
- **Escalation brief: none written.** `scripts/escalation_brief.py` reported "no escalations
  in the last 24h" — no `Records/ESCALATION_BRIEF_2026-08-21.md` exists.
- No push, no deploy (NIGHTLY-SHIP-1 owns shipping).
