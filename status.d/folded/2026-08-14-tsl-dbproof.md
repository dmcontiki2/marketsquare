- **TSL-DBPROOF-1** — the `/TSL` pre-deploy gate no longer needs David's SSH key to prove the
  live database. `/health` now carries a facts-only `db` block (presence, bytes, integrity,
  redis; cached integrity scan, cannot raise) and `tsl_gate.py` reads it over plain HTTPS
  first, with SSH demoted to a second opinion. REVIEW now means "neither transport could
  prove it", not "this session is not David's desktop". Ledger `RG-0069` OPEN — flips to
  READY TO LOCK on the next deploy.
