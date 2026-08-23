## 2026-08-23 — Third-party launch sweep: secrets rotation CONFIRMED CLEAR; EULA v1.15 live; deploy debt is the remaining gate

**TPSWEEP-3** (scheduled `pre-soft-launch-third-party-check`, unattended). 6 days to soft launch — verdict AMBER.

- **Yesterday's ONE BLOCKING item is CLEARED and the register now says so**: the secrets rotation
  finished 22 Aug after the morning sweep ran. SECRETS_REGISTER.md 'Still burnt' table EMPTY,
  RG-0146 LOCKED and passing. OPEN_LOOPS B1's stale "Ten still BURNT" cell corrected (row left
  open for attended close; residue = 2 superseded Cloudflare tokens to delete + FOUNDERS_ID_SALT call).
- **Probe overruled a file, again**: LEGAL_VERSIONS.md said EULA v1.15 "Not yet deployed" —
  `GET /terms` serves v1.15 (200). File corrected in the same run (ONETAP-DOC-1 rule).
- Probed green: /health ok 1.3.1 · google:true (start 302s with real client_id) · apple 503 (RUL-030
  enforcing) · Didit available:true · TLS 32 d · ledger exit 0, 151 entries, 0 REGRESSED, 14 honestly
  open · rulings 42/0/0 · eula_sync green.
- **What blocks or threatens 29 Aug now**: (1) deploy debt — 4 commits unpublished
  (SESSION-COUNTER-1, PROVENANCE-1, DEPLOY-COHERENCE-1/migration 030, SAW-1 teaser — live teaser
  probes 404), ship by Wed 27 Aug, RG-0154/RG-0158 close on ship; (2) GOOGLE_CONSENT_SCREEN
  UNRECORDED (RG-0139); (3) DOMAIN_* UNRECORDED (RG-0137); (4) RG-0156 orchestrator.html
  (manifest + hardcoded 96315 + empty-state honesty) — the one build owed before 27 Aug, for an
  attended session.
- Uptime watcher (RG-0138) is now UNBLOCKED — rotation done, fresh Resend key available; David runs
  the 3 runbook commands.
- Register rewritten from evidence: Paystack sk_live now PROBED-confirmed (22 Aug, /transaction/totals
  200); tours row moved from "declined 5 Aug" to RESUBMITTED 22 Aug AWAIT OUTCOME (RUL-041/D10);
  Gmail SMTP fallback recorded as first-ever successful auth; JustTCG recorded deliberately dark
  (licence). Backups kept beside all three edited files.
