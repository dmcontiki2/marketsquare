## 2026-09-09 — Goal run 8 (Fable 5.1): no shell, missed 00:10 wave re-queued, Colorado register found

- **Session fired at 06:15 SAST instead of 01:03** (task `lastRunAt` 04:15Z) and the host DailyWave left
  no `logs/launchday_09Wed09_*.log` — the PC was asleep/off overnight. Two independent misses, one cause.
- **Sandbox shell never mounted** (3 identical `failed to mount ... Plan9 share "c" not mounted` errors;
  stopped retrying as instructed). Consequences this run: `onboarding_number.py`, the regression ledger,
  `rulings_check.py`, `request_host_action.py` and all heredoc writes were impossible. Number this run:
  **UNKNOWN (not measured)** — last PROBED value 0 on 8 Sep. Ledger/rulings: NOT RUN this session.
- **WAVE-REQUEUE-1:** queued `CityLauncher\launch_day_wave.bat` and `CityLauncher\run_us_registers.bat`
  by writing the `.req` files directly (`host_queue/20260909-042000-000_…` and `…-042100-000_…`), same
  five-line format `request_host_action.py` emits, both allowlisted, both read back complete. Permission
  quoted: David 5 Sep ("keep the emails flowing as fast as is possible") and RUL-095/096. Small-file
  Write was used because the shell was down; every write was verified by re-reading the last line.
- **COA-1 (draft, not wired):** Colorado Outfitters Association is an open register — public WP REST
  index `/wp-json/wp/v2/outfitter?per_page=100` returns **92** profiles; each profile page carries
  `Email:`, `Phone:`, `Website:`, `Address:` (PROBED via David's Chrome, e.g. Jackson Outfitters →
  roy@jacksonoutfitters.com). The `/find-your-outfitter/` HTML is script-rendered (filters only).
  Adapter written to `CityLauncher/us_registers/coa_adapter_DRAFT.py` in the `_wyoga` shape; needs
  splicing into `us_register_reader.py` + `run_us_registers.bat` via heredoc next run (needs shell).
- Not done this run (needs shell): ledger shards, rulings_check, funnel probe (`/onboard/funnel` is
  gated; web_fetch provenance-blocked), reading the 9 Sep wave outcome (queued, result not yet in).
- Ledger entries owed next run: (a) COA-1 adapter → LOCKED once the `.result` shows an import;
  (b) an OPEN entry for "DailyWave skipped when the PC is asleep at 00:10" — the task is registered
  with wake-from-sleep, and it still did not fire; the goal task also slipped 5 h. Class, not instance.
