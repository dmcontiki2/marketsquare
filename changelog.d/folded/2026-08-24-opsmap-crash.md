## 2026-08-24 — OPSMAP-CRASH-1: the Ops Map's phantom blocker

The +1 page's Ops Map froze at its placeholders — "flags loading…", "service checks
loading…", and a Maintenance lane whose unfilled chips wore hardcoded red/amber, which
read as "1 blocker + ambers" (David, 24 Aug). Root cause: PROVENANCE-1 (22 Aug) wrote
`fetch(EP + '/dashboard/fixed-costs')` into `loadFixedCosts` while the ops-map IIFE's
base is `B`; `omLoad()` calls it first, the ReferenceError killed the loader, none of
the 10 feeds ever fired. The fault register itself was clean: 35 rows, 0 active,
0 awaiting close (probed via /admin/faults this session).

Fix: `EP`→`B` (one line), plus RG-0133's rule applied to the map — the 11 placeholder
chips (fault lane, fault-intake flag, BIT, the two loading pills) now default to the
grey dashed `nw` class until `fill()`/`fail()` paints them from a live answer, so a
future loader crash shows grey "—", never a counterfeit verdict. Verified: node stub
run fires all 10 fetches with no throw. Ledger: RG-0172 LOCKED.
