### ID-NPR (RUL-039) — the verification LANE IS ARMED · 21 Aug 2026

`GET /id-verify/status` → `{"provider":"didit","configured":true,"available":true,
"note":"READY — sellers can buy a check.","price_t":1}` · `GET /users/{email}/id-status`
answers correctly (a clean 404 "User not found" for an unknown user, not a 500). Live release
`4da2443`.

**Where the environment actually lives — this cost a round-trip, do not rediscover it.**
`/var/www/marketsquare/.env` is NOT read by the service. There is no `load_dotenv` anywhere in
the Python; the app is pure `os.getenv`, so systemd supplies everything. The ID-verify vars are
set in a **systemd drop-in**: `/etc/systemd/system/marketsquare.service.d/id-verify.conf`.
Editing them needs `systemctl daemon-reload` then `systemctl restart marketsquare`.

OPEN: we still have not confirmed where the OTHER secrets (PAYSTACK_SECRET_KEY etc.) come
from — `systemctl cat marketsquare | grep -i environmentfile` answers it. If it names a file,
fold the drop-in into that file so there is ONE place for secrets, not two.

**What is live:** the endpoints, the three-state model, the duplicate-ID trap, the buyer
notice helper, the EULA §3.5A (v1.15), the probe.
**What is NOT live:** the front-end. No green tick renders, no buy button exists on the ID
upload screen, and the buyer warning is computed but never shown. **No seller can actually buy
a check yet** — the capability is armed and unreachable. Do not describe this as done.

**Not yet proven:** no real NPR query has ever run. The first live check will confirm (a)
whether Didit's 500 free monthly verifications cover Database Validation or whether it bills
$1.10 from call one, and (b) that the outcome mapping behaves against a real registry
response. RG-0136 stays OPEN until then.

**Security note:** the first API key was pasted into a chat window and has been rotated. The
replacement went straight to the server. Never paste a live key into a chat — the probe
reports READY/DARK without ever exposing it.
