- **Deploy gate unblocked (19 Aug).** The two guards that had put DANGER on every
  pre-deploy scan since 4 Aug are fixed: PG-PORTABLE-1 (demand lane no longer grows
  SQLite-only date arithmetic; surface 53 → 49) and EMAIL-NOT-A-PAGE-1 (3 orchestration
  consoles now carry the tester fault widget; 14 outreach email bodies correctly exempt
  and asserted script-free). Strict-mode pre-deploy now exits 0 — the 02:00 nightly,
  which aborted every night, will pass.
- **RG-0114 LOCKED** — new class tripwire: no guard verdict may sit red for 8+ consecutive
  scans. Both faults above were detected on day one and never escalated to a human; this
  is the assertion that makes that impossible to repeat.
