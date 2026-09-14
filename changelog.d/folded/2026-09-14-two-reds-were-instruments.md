## 2026-09-14 — The last two reds were the instruments, not the product

Both remaining regressions were checked against the running system before anything was touched, and
neither was a fault in the app. Each assertion was fixed and the reason written into its entry, per the
ledger's own rule that a wrong assertion gets fixed and said so — never weakened to make it pass.

**RG-0094 — the wallet is NOT broken.** Two instrument faults in one entry, both caused by the same-day
RG-0371 change that moved identity from the app key to the `ts_user` session cookie:

- the source leg matched an exact character string, and both defs had GROWN parameters (`ts_user`,
  `x_admin_key`) — it now reads the def and checks its parameter list for `Depends(auth.require_api_key)`;
- the live leg demanded `keyed -> 200`, which since RG-0371 asserts the very hole this entry exists to
  close — a keyed caller with no session is refused ON PURPOSE. PROBED: keyless 401 "missing API key",
  keyed-without-session 401 "Please sign in to do that", which proves the key was accepted and only the
  session was absent. The browser still gets its balance because `BEA_URL` is this origin, so the
  same-origin fetch carries the cookie. The live leg now fails only on a 200, which is stricter.

**RG-0367 — the Buzz consent line is on screen.** The copy was factored into `bzTermsCopy()` and moved
2,860 characters ABOVE `buzzRender`, so the check's forward-only 4,000-character window stopped seeing it
and reported a missing consent line that had never gone. PROBED on the LIVE `ms.js`: `bzTermsCopy`,
"section 3.8", `"/terms"` and the call site are all present and served. The assertion now accepts the copy
living in a helper, provided `buzzRender` calls it — the property is that the wording is shown at the
switch, not where it sits in the file.

**Board:** three shards + combine — every locked fix is holding, 0 regressions, 22 known defects still
open and expected. RG-0187's contract applied in both cases: an instrument that cannot see a thing must
never report it as gone.
