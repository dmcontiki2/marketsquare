## 2026-08-31 — The three "regressions" on David's board were two stale reads and one false red (LEDGER-DEPS-2)

David's ledger run showed 3 regressions that my Linux run did not. Diagnosed by having him run
the three scripts directly and reading the output rather than inferring it.

**Two were not failing at all when tested directly:**
- `session_counter --check` → **OK**, session 184, 29 sittings since anchor
- `dashboard_provenance --check` → **OK**, 70 chips, 0 unfed health chips, 0 orphans

Both had reported red during a ledger run and pass standalone — consistent with the earlier
UNSTABLE RUN (LEDGER-STABLE-1 correctly refused a verdict when I edited `regression_ledger.py`
mid-run). Lesson already owned: do not touch the tree while the board is reading it.

**The third was a genuine false red, and the first explanation I gave for it was wrong.**
`prove_csp_discovery.py` printed `nginx -T unavailable (FileNotFoundError)` and failed 2 of 10.
I attributed it to nginx not being installed and shipped a demotion on that basis — then caught
it: **nginx is absent on the Linux runner too, and it passes 10/10 there.** The stated reason was
false, so the gate was reverted before it could hide anything.

**True cause:** the harness simulates an `/etc/nginx` tree by patching `SEARCH`, `os.walk` and
`_nginx_T_files` at POSIX paths. On Windows the discovered paths return from `os.path.realpath()`
with backslashes while the fixture's expectations carry forward slashes, so the "FINDS the nested
emitter" comparison cannot match regardless of what the migration does. A **harness portability
limit**, not a rotted fix — and production nginx runs on Linux.

**Fix (LEDGER-DEPS-2):** on Windows only, and with the accurate reason printed, the harness returns
`3` = NOT EVALUATED; the ledger entry demotes that to UNVERIFIED instead of REGRESSION. Linux still
evaluates it fully and must still pass 10/10 — verified after the change.

This is RG-0187's rule for the third time today: **an instrument that cannot faithfully run must
read UNVERIFIED, never REGRESSION.** A demotion carrying a *false* reason is worse than a red,
because it retires the assertion and misleads the next reader — which is why the first attempt was
reverted rather than kept.

Files: `scripts/prove_csp_discovery.py` · `scripts/regression_ledger.py` (csp entry demotion).
