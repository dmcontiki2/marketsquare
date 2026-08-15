## 2026-08-14 — GATE-ORIGIN-1: the dashboard stops asking for a password it cannot accept

**Second face of the same fault.** With GATE-TRUTH-2 in place the gate finally named its failure
honestly — and the honest name was *"the browser could not reach trustsquare.co"*. That is the
`file://` path: origin `null` is not in `ALLOWED_ORIGINS` (`bea_main.py:133`), the pre-flight is
refused, `fetch` rejects. **No password can ever work from there**, and the old message had been
hiding that behind the same sentence it used for the gate lock.

`STATUS.md:379` records that the local sibling is the copy David actually opens — a documented
habit, not an accident. So the fix is not "tell him afterwards", it is "do not ask".

**Two defects fixed.** The gate hardcoded `BEA` absolute while `_apv3B`, two thousand lines below
in the same file, already did the `file://` check correctly — so a served page was making every
gate call a needless cross-origin request. And nothing warned until after a failed round-trip.

Now the gate detects `location.protocol` at render, explains that the browser blocks it before the
request leaves, and links the working URL.

**Locked.** `RG-0076` asserts both halves: no hardcoded absolute `BEA`, and a live protocol test.

Files: `dashboard.server.html`, `dashboard.html`, `marketsquare_admin.html`,
`scripts/regression_ledger.py`. Not deployed.
