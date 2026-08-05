## 2026-08-05 — Peer round 2: F2 + F3 fixed, F1 briefed

- **F3 / RG-0036 — KYC SSRF guard (KYC-SSRF-1) + lane pin (KYC-PIN-1).** verify-identity
  fetched a caller-supplied doc_url with a bare urllib.urlopen (no allowlist, no
  private-IP block, no redirect ban, no size cap) — SSRF + memory-DoS with the public
  app key. New _fetch_kyc_document: pins to R2_PUBLIC_URL, forbids redirects, rejects
  hosts resolving to private/loopback/link-local/reserved, caps read at 12 MB. KYC
  vision call now allow_fallback=False so ID documents never fan out to standby vendors.
- **F2 / RG-0037 — atomic pre-dispatch spend reservation (C1-RES).** _check_cost_ceiling
  summed only LOGGED spend (written after the call) so concurrent calls could overshoot.
  New ai_spend_holds table: a worst-case hold ($0.06, 180 s TTL) placed in the same
  transaction as the ceiling check and counted by it; _log_ai_spend settles the hold on
  real cost; holds self-expire so an aborted call can't wedge the budget. Isolated-logic
  test proved the bound (10 concurrent -> admitted up-to-cap only, not all 10).
- **F1 — account binding: DECISION BRIEF, no code changed.** Caller-passed email selects
  the charged account behind a shared public key = app-wide authorization hole. Brief in
  Records/F1_ACCOUNT_BINDING_DECISION_BRIEF.md (+ nice docx); recommendation Option A
  (session-bound charges via the existing ts_review token). Awaiting David: A / B / C.
- Ledger RG-0036/0037 LOCKED (repo-side assertions green). Peer pack v3 regenerated.
  Backups: bea_main.py.bak-20260805-ssrf. py_compile green.
