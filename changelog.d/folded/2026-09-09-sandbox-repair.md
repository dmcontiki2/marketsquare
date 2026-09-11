## 2026-09-09 — SANDBOX-REPAIR-1: the dead Cowork sandbox is diagnosed and queued, never "unfixable"

David, on the 9 Sep maintenance run's report ("nothing was checked, no faults were read, no fixes were
made ... tomorrow's scheduled run will pick everything up"): *"i can not accept that we have a failure
which cant be fixed."* Session 21:30–23:00 SAST, no shell at any point.

**The fault.** Every sandbox command fails at start: `sandbox-helper: no Plan9 drive shares mounted
under /mnt/.virtiofs-root/shared` (goal run 8 saw it as `Plan9 share "c" not mounted`). Persisted
across every session from 06:15 SAST; retries change nothing.

**What was PROBED, in order, all through the host queue (RUL-095) because terminals are click-only
for computer use:**
- 20:51 stage 1 — WSL is **not installed** on David's PC, so the sandbox is the Claude app's own
  Hyper-V (HCS) VM and `wsl --shutdown` was the wrong lever (written on an untested assumption,
  now diagnose-only). Also proven: the host agent runs as David in his desktop session, and
  `timeout /t` exits at once under the agent (no stdin) — waits now go through Start-Sleep.
- 21:11 stage 2 — full Claude desktop restart (16 processes closed, relaunched with `claude:`,
  session relinked, window un-pinned). **Sandbox still dead.** The VM (vmcompute / vmwp / vmmem)
  belongs to a Windows service and outlives the app. "Restart the app and it comes back" — the
  previous run's closing line — had never been tested and is false for this class.
- 21:31 diagnosis — Windows build and KB list, VM process ages, elevation, the Cowork logs' last
  Plan9 lines (result in `host_queue/done/20260909-191600-*.result`).
- Cause identified from the field: **Windows 11 KB5124008 (24H2 build 26200.9445)** makes the host
  report the shares attached while the VM mounts 0 of them — claude-code issue #92984, same app
  version (1.49585.0), same VM bundle, reported the same day; ARM64 twin #92958. Reboots,
  re-adding folders, restarting CoworkVMService and a fresh 8 GB VM bundle all do nothing there;
  only removing the KB restores it. That removal is an admin action on David's PC plus a reboot —
  reserved to him — and was put to him in this session, not parked.

**Built (all host-side, all allow-listed, all read-only except the app restart):**
`MarketSquare\sandbox_repair.bat` (diagnose) · `sandbox_repair_diag.ps1` · `sandbox_repair_sess.ps1`
(session guard) · `sandbox_repair_restart_app.bat` (the #30164-class remedy, refuses off-desktop) ·
`host_queue/ALLOWLIST.txt` widened with those two bats plus **host-side runs of
`scripts/regression_ledger.py` and `scripts/rulings_check.py`** (`run_py`), so the fact boards can be
read on David's own Python — no 180 s cap — while the shell is down. First host-side ledger run queued
this session; read its tail for Windows-only noise before trusting a red.

**Standing method** written to `Projects\CLAUDE.md` (SANDBOX-REPAIR-1 block): retry once → queue the
diagnosis by writing the `.req` with the app's file tools → act on the cause the result shows (KB
family → David's call, stated in one sentence; #30164 family → queue the app restart; else report
the evidence) → keep working through file tools, web probes, queued host actions and host-side
boards → re-test every run and say when the sandbox is back. Ledger **RG-0348** (LOCKED) asserts the
scripts, the guard, the allow-list rows and the CLAUDE.md block all still exist.

Not done this session (needs the shell or David): the sandbox itself is still dead at the time of
writing — the fix is the KB decision, above.
