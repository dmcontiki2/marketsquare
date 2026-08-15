## 2026-08-15 — DRIFT-FILEMAP-1: the drift monitor now compares what actually ships

The 07:22 release confirmed DRIFT-CACHEBUST-1 live — drift fell from two files to one and the
tester-intake guard went clean, clearing that half of the standing DANGER verdict.

The remaining `dashboard.html` row was a separate fault: the drift map compared local
`dashboard.html` against the served `dashboard.html`, which is built from `dashboard.server.html`.
Different source file, so it could never match. Corrected, and RG-0072 now cross-checks the drift map
against the deploy manifest so a mis-mapping fails the same day. `demo_sellers.json` is recorded as a
known server-owned exception — migration 017 writes it live and the deploy never places it.

Remaining DANGER contributor is PG-readiness (`strftime` 38 → 40), which is a real finding.
