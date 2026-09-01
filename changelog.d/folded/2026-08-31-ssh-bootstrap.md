## 2026-08-31 — SSH-BOOTSTRAP-1: the recurring "no SSH key in the sandbox" class is closed

The fault that stalled sessions repeatedly (latest strike: this morning's Gate 1 board
shipped with clicks unreadable) was never a missing key — `ssh_hetzner_key` and
`load_sandbox_ssh.sh` sat on the mount the whole time. It was knowledge placement: the
instruction lived in MarketSquare/CLAUDE.md, which a CityLauncher session never loads.
Same class as GIT-LOCK: machinery existed, memory failed. Fixed at class level:
(1) `CityLauncher/ssh_bootstrap.py` — `ensure_ssh()` self-heals ~/.ssh from the mounted
key, idempotent, proven from cold + live server probe in the same session;
(2) all 6 SSH-using CityLauncher entry points (pull_from_server, sync_local_to_server,
push_estate_agents, push_us_uk_cities, run_local_scraper, run_za_estate_agents) call it
at entry, so they work from a cold sandbox with zero setup;
(3) the standing note moved to Projects/CLAUDE.md — the one file every session loads.
Ledger RG-0230 (LOCKED) asserts all three layers; a new SSH script that skips the
bootstrap trips red. Only remaining David-side case: the key file itself vanishing from
the mount (re-run `setup_sandbox_ssh.ps1`).
