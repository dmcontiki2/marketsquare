- **DRIFT-FILEMAP-1 (15 Aug 2026) — the second half of the phantom-drift fault.** The 07:22 release
  proved DRIFT-CACHEBUST-1 in the wild: the drift line fell from TWO files to ONE, marketsquare.html
  cleared, and `Tester fault-intake guards: ok` replaced the standing DANGER from the stale
  maint-scope guard. The residual `dashboard.html` was a DIFFERENT cause wearing the same face:
  `check_deploy_drift.py` FILEMAP mapped local `dashboard.html` -> served `dashboard.html`, but the
  served file is built from `dashboard.server.html` (deploy_manifest.txt:72). Local `dashboard.html`
  is a separate file that is never deployed, so that row could not match no matter what shipped.
  Fixed by comparing what actually ships.
- **The guard now asserts the INVARIANT, not the instance.** RG-0072 gained a cross-check: every
  file in the drift map must agree with the deploy manifest about where the served copy comes from.
  A future mis-mapping goes red the same day instead of producing years of ignorable noise. Known
  exception recorded in the check itself: `demo_sellers.json` is SERVER-OWNED (migration 017
  rewrites it live, the deploy never places it), so "local ahead of live" is meaningless for it.
- **Standing lesson, third instance in two days:** a monitor must compare the thing that actually
  ships, in the form it actually ships in. DRIFT-CRLF-1 (line endings), DRIFT-CACHEBUST-1 (the
  server's own ?v= rewrite) and now DRIFT-FILEMAP-1 (the wrong source file) are one fault class —
  comparing an artefact of transport or build instead of content. Each produced a permanent red
  that trained everyone to ignore the monitor.
- **Still open and genuinely real:** PG-READINESS `strftime` 38 -> 40. It is the ONLY remaining
  contributor to the DANGER verdict, and unlike the other two it is a true finding — two new
  SQLite-specific calls that make the eventual Postgres move dearer.
