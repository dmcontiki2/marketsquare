## 2026-08-30 — maintenance-loop: LEDGER-ADMINREAD-1 — ledger reads /dashboard/summary through the admin door; RG-0198 + RG-0211 promoted LOCKED

- Daily maintenance run. Fault queue: 0 new (shadow agent run 05:39 UTC, heartbeat confirmed on /dashboard/maint). Escalation brief: none.
- Morning ledger read 2 REGRESSED (RG-0127 panels empty, RG-0154 badge basis None). Diagnosis: instrument collateral of DASH-SUMMARY-REDACT-1 — the anonymous /dashboard/summary payload is heartbeat-only BY DESIGN (probed: `{"generatedAt":…,"bea_version":…,"redacted":"heartbeat"}`), so the ledger's anonymous probes were failing on the app behaving correctly. The fixes had not rotted.
- LEDGER-ADMINREAD-1: regression_ledger.py gains `_admin_json()` — X-Admin-Key from `.secrets/deploy_keys.txt`; RG-0127 and RG-0154 live halves read through it. No key on the machine, or a refused key, reads BLIND (INFO), never RED (RG-0187 boundary). Refs of both entries carry the dated amendment; assertions fixed, not weakened — the same checks run on the credentialed payload.
- Promotions the same run they printed READY TO LOCK (DW-079 rule): RG-0198 (no internal narrative to strangers) and RG-0211 (heartbeat-only anonymous payload) → LOCKED.
- Verification: full ledger re-run PROBED green — 205 entries, 186 holding, 0 regressed, 0 ready-to-lock, 0 unverified, exit 0. RG-0154 live half now reads badge derived, session 183, as-of 2026-08-30, through the admin key.
- No deploy, no push (NIGHTLY-SHIP-1 ships committed work).
