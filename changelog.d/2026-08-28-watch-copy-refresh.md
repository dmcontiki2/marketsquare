## 2026-08-28 — WATCH-COPY-REFRESH-1: the outage alarm is alive, and the cause is fixed (RG-0201)

**The RED-alert channel answers again after six days dead — PROBED `HTTP 200` at 10:44 UTC**, on the
eve of soft-public. D2 (Paystack 2FA) and D3 (this) both closed today; David's queue is 9 open.

**What was wrong.** `/etc/marketsquare/resend.watch.conf` is the out-of-band copy of the Resend key
the daily watch uses to send RED alerts — the only channel that wakes David when the site is down.
It is a duplicate of the app's systemd drop-in, installed ONCE by `fix_watch_alerts.bat` on 5 Aug
2026, which was then retired. The 22–23 Aug rotation replaced the drop-in and left the copy holding
a deleted key. **Nothing noticed for three days**, because nothing exercises that path except a real
outage; it surfaced on 26 Aug only when a genuine RED fired and never arrived.

**The repair — one command, the original mechanism:**
`install -o root -g msdeploy -m 640 /etc/systemd/system/marketsquare.service.d/resend.conf
/etc/marketsquare/resend.watch.conf` → 74 B, `0640 root:msdeploy`, probe returns **200**.

**The class fix (this is the half that matters).** `ROTATE_SECRETS.bat` gains step **[4b/6]**, which
re-installs the watch copy inside every rotation and shouts if it cannot. The unwritten human step
that failed no longer exists. **Ledger RG-0201 (LOCKED)** asserts the rotation carries the refresh
and that the copy stays listed in `SECRETS_REGISTER.md`'s out-of-band table — source-half by
necessity, since the copy lives on the box and the board runs from anywhere. CRLF guard re-run, bat
still clean (RG-0194).

### The sharper lesson, recorded rather than smoothed over

**The repair itself went wrong twice before anyone read what the file was.** It was assumed to be a
plain `key=value` config and edited with a split on the FIRST `=`, which destroyed the variable name
in `Environment=RESEND_API_KEY=…` — it is a **systemd drop-in**. A second attempt inherited the
damage and a third leaked markdown escaping into the pasted commands, producing a `400` that was
read as a bad key when the probe had simply run with no key at all. Two of David's `.bak` copies
were overwritten in the process, so the original content was lost.

**The answer was in the repo the whole time**, in the retired one-shot that created the file. One
`grep` for `resend.watch` found it; the fix was then one command and returned 200 first time.
**A format assumed is a format not probed** — the evidence ladder applies to file structure, not
only to status. Recorded in `SECRETS_REGISTER.md` beside the row, including the reversal of the
same morning's CTO call (that the replacement must be a newly-minted dedicated key): sound in the
abstract, wrong about what is built here, and made without reading the mechanism first.

**Also corrected:** David was handed option menus and branching alternatives mid-task, against his
standing instruction, which cost several rounds on a launch-eve job that was one command long.

**Board after:** ledger **exit 0 · 180 holding · 0 REGRESSED · 12 open**; `RG-0201` reads `[ ok ]`.
Note: `RG-0200` was taken by a concurrent session and LEDGER-DUP-1 caught the collision — the guard
worked, and this entry renumbered.
