## 2026-08-21 — ACCOUNT-CLOSE-1: EULA §14.1/§14.2/§14.3 in code, and the sweep scheduled

David: "the three left items — proceed with them and close them." Done: the closure/restore
path, the monthly schedule for the dormancy sweep, and the commit.

### The endpoint was destroying what §14.1 promises to give back
`DELETE /users/{email}` was literally `DELETE FROM users WHERE email = ?`. It said nothing
about Tuppence, left orphaned `transactions` rows, kept no audit trail, and made §14.1's
restore promise impossible to honour — a deleted row cannot be restored to. It also
contradicted §14.1's own wording ("deleted or anonymised within 30 days"): an immediate hard
delete is neither.

### New `account_closure.py` (168 lines, stdlib)
- **§14.1 user closes / §14.3 Platform closes for convenience** → balance RETAINED. One
  offsetting `closure_retention` row moves the wallet to zero; the amount is recorded in the
  new `account_closures` table. The user row is soft-closed (`users.closed_at`), never deleted.
- **§14.2 breach** → forfeits ONLY for cause **B5** (payment fraud / chargeback abuse) and
  **B6** (identity fraud), per David's express ruling. B1–B4 retain like any other closure.
- **Restore on return** → hooked into `POST /users`. Matched on `users.id_number_hash` where
  the closed account had one (strong proof), else on email (weak proof). Both are recorded in
  `restore_match` so an auditor can see which was used, and so a pattern of weak-match abuse
  is visible. Restores across a NEW email address when the verified identity matches.
  Idempotent. Wrapped so a restore failure can never block a registration.
- Wallet remains a pure `SUM(amount)` throughout — no destructive UPDATE anywhere.

**Bug caught by the test, not in production:** the first implementation looked up the balance
with `WHERE user_email = ?` while looking up the user with `lower(email) = ?`. A mixed-case
address therefore read a ZERO balance and retained NOTHING — it would have quietly destroyed
the very credit the clause exists to protect. Both lookups are now case-insensitive and the
ledger rows are written against the address as stored. RG-0129 tripwires the regression.

Verified: 30 checks green across user/breach/convenience closures, all six breach causes,
mixed-case addresses, returns under a new email, idempotency, zero balances, unknown users,
and a stranger attempting to claim someone else's retention (refused).

### The sweep is now scheduled
`ops/dormancy/tuppence-dormancy.{timer,service}` + `INSTALL.md`, mirroring the existing
maintenance-agent unit pattern. Monthly, 04:40 UTC on the 1st, clear of the 05:20 maintenance
run. Monthly rather than daily is deliberate: the notice window is measured in days, so a
monthly cadence can never make a warning late by more than a few days, and the sweep is a
no-op the rest of the time. The unit passes `--apply`; the script itself refuses to run that
way without RESEND_API_KEY, so an expiry can never ride on a warning that could not be sent.

### Shipping
- `migrations/028_account_closure_and_dormancy.py` — creates `account_closures`,
  `tuppence_dormancy_notices` and `users.closed_at` on the live box. Purely additive,
  idempotent, refuses rather than guesses.
- `ops/autodeploy/deploy_manifest.txt` — two lines added: `account_closure.py` and
  `scripts/tuppence_dormancy.py`.

### Ledger
RG-0129 extended from two halves to three: the dormancy sweep, the EULA wording, and now the
closure lane in code. **Tripwire proven twice** — thirteen deliberate reversions injected
across both sessions (sweep deleted, notice-age check removed, dry-run default removed,
forfeiture wording restored, no-cash-out softened, fraud-only forfeiture widened, restore path
removed, case-sensitivity reintroduced, hard DELETE restored, registration hook removed…) and
every single one turned the entry red; the intact state is green.

INSTALL STILL NEEDED ON THE BOX (one-time, root): copy the two unit files to
/etc/systemd/system/, `systemctl daemon-reload`, `systemctl enable --now
tuppence-dormancy.timer`. Steps and a safe dry-run recipe are in ops/dormancy/INSTALL.md.

Cost model impact: none. No new services; warning emails ride existing Resend and expected
volume is zero for ~20 months.
