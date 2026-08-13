## 2026-08-13 — MAINT-DASH-1: B2b launch-readiness card on the +1 page

- David: "put this in the ops dashboard as a switch for launch." Honest form shipped as a
  TRUTH CARD, not a switch: the brain key is a gitignored file and MAINTENANCE_AGENT_ENABLED
  is env on the loop's machine — David's acts; a web toggle could only lie or hazard, so the
  card deliberately has no control surface.
- Server: POST /dashboard/maint (maintenance credential, facts-only whitelist — lane NAMES,
  never key material, RG-0042 rule) → maint_status.json; open GET mirrors /dashboard/bit.
- Agent: _post_heartbeat() after every completed REAL run — brain keyed?/lane, armed?, mode,
  phase, seen/acted, lane counts, code stamp. Fail-SOFT (RG-0049 spirit): proven live — 404
  from the not-yet-deployed endpoint absorbed, run unaffected, exit 0. Rehearsal runs
  (--faults-file) never post: a synthetic storm must not stamp the production card.
- Dashboard (+1 page): 🤖 Maintenance Agent (B2b) card above the Launch Switch — three
  colour rows (heartbeat fresh/stale 36h, brain KEYED/NO KEY with the one-line .secrets/
  ai_keys.env remedy, ARMED/SHADOW) + LS-TIPS-1 hover explainer. JS node-checked.
- Ledger RG-0061 added OPEN same-session (RG-0029's unasserted-fix lesson): pins the POST
  credential, whitelist, rehearsal guard, no-toggle design, and end-to-end liveness — goes
  READY TO LOCK after the next deploy + first real heartbeat. Ledger: 61 entries, 57
  holding, 0 regressed, exit 0. Ships via NIGHTLY-SHIP-1; no deploy from this session.
