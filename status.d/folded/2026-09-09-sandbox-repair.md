- **SANDBOX-REPAIR-1 (9 Sep, 23:00 SAST):** the Cowork Linux sandbox is dead on David's PC since
  ~06:15 — cause is Windows update KB5124008 (claude-code #92984), not the app: a full app restart
  via the host queue at 21:11 changed nothing (PROBED). Decision put to David: remove the KB
  (admin + reboot) or wait for Anthropic's fix. Until then every session works shell-less by the
  CLAUDE.md SANDBOX-REPAIR-1 method: file tools, web probes, queued host actions, and the ledger +
  rulings boards run HOST-SIDE via `run_py` (allow-listed 9 Sep). Ledger RG-0348 locks the machinery.
