## 19 Aug 2026 — pre-launch gate: lockout class closed (GATE-NOLOCK-1)

David was locked out of both the app and the dashboard on his laptop while the phone that opened
the emailed link got in. Root causes were three, not one: a magic link can only unlock the
browser that opens it; `/admin/login` was not exempt at the origin so the super-admin password
never reached the app; and the gate screen reported that origin 401 as "Incorrect reviewer code".

Shipped in source (awaiting deploy): a 6-digit cross-device code in the same access email,
redeemed at `POST /review/claim-code` on the locked device; a correct admin password or team PIN
now grants the gate cookie itself; `migrations/025_gate_nolock.py` exempts the four credential
endpoints at the origin while the catch-all stays armed; gate and dashboard messages corrected.

Ledger: RG-0107 + RG-0108 OPEN, expected to flip READY TO LOCK the moment migration 025 lands.
RG-0066's assertion corrected (it pinned a sentence that had itself become the lie).

**Next:** ship (`/tsl` or `/ship`), then re-run the ledger — RG-0107/RG-0108 promote to LOCKED
once the live half answers with an app-JSON 401 instead of an nginx HTML 401. Then have David and
Maroushka each enter once from a fresh browser before the link goes to agencies.
