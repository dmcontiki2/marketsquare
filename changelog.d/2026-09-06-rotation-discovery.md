## 2026-09-06 — ROTATION-DISCOVERY-1: a rotation now knows where the copies are (DW-107, RG-0308)

David: *"rotation is one of those things i battle with as you know well... it takes me some times many
hours to fix rotations."*

**Where the hours actually go.** Minting the new value at the vendor is five minutes, and it is
irreducibly his. The hours go on a question nobody could answer: **which places hold a copy?** That has
been answered from a hand-maintained table with **one row** in it — and it was wrong twice, both times
silently, both times found only when something broke:

- the Resend alert key, orphaned for six days (DW-076);
- the database-backup credentials, orphaned for two weeks (DW-105, found this morning).

**`scripts/secret_consumers.py`** replaces remembering with looking. For each credential name it searches
every place a copy is known to be able to live — systemd drop-ins, `/etc/environment`,
`/etc/marketsquare`, both apps' `.env` files, the crontabs, the cron scripts — and reports where the name
appears. `ROTATE_SECRETS.bat` runs it as **step 0**, before anything is touched, and pauses if copies
exist the register does not know about.

**It never prints a value — by construction, not by care.** The item that prompted this tool exists
because a masking command was hand-written and got it wrong, putting two live keys on screen (DW-106).
A tool that cannot leak beats a habit of being careful.

**First run, and it earned its keep immediately: 13 of 22 credentials have copies the register does not
list.** `RESEND_API_KEY` has a **third** copy in CityLauncher's `.env` that nobody knew about.
`LAUNCH_CODE_SECRET` is in five places. Every one of those is a rotation that would half-succeed and go
quiet.

Tracked by **RG-0308**, deliberately OPEN: it fails today with the count and closes when a run reports no
surprises. The register must catch up with reality, not the reverse.

**Two bugs in my own assertion, both the same shape — reporting a number I had not actually read.** It
first re-derived the count from the layout of the tool's output and said "2"; then read a truncated tail
and said "1"; the tool said 13. It now runs the tool directly and reads the tool's own count. A board
that is read for its numbers may not invent them.

**Also surfaced, not fixed, because deletions are David's:** stale `*.bak` copies of `secrets.env` are
sitting on the server from the 22 August rotation — dead files holding live-shaped values.
