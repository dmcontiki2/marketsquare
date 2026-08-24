## 2026-08-25 — WINDOW-ZORDER-1 (the deploy can flash) and CSP-SCRIPT-SRC-2 (031 said ok without proving it)

### WINDOW-ZORDER-1 — "it used to sit in front of Claude and not behind"

**Cause, and it is not David's machine.** The `/start` skill launches
`deploy_marketsquare.bat` **itself** (SKILL.md lines 70-78), and the desktop-control tooling launches
apps in background mode by design — *"the launch does NOT bring it to the front; the user's focus is
preserved."* So the console opens behind whatever he is looking at. When **he** double-clicks it,
Windows grants foreground to a user-initiated launch and it lands in front, exactly as it always did.
Nothing was misconfigured: a general focus-preservation rule met the one window that ends in `pause`.

**Why not just raise it.** Windows refuses `SetForegroundWindow` to a process that does not own the
foreground — deliberately — and fighting that would break the thing that stops every other app
interrupting him. So we use the signal Windows provides for exactly this case: `FlashWindowEx` with
`FLASHW_TIMERNOFG`, which flashes the taskbar button **until the window is looked at**, plus a beep
and a window title readable at a glance in the taskbar.

- **`notify_attention.ps1` / `.bat`** (new, the existing `diag_gmail.bat`→`.ps1` idiom). Fails silent
  by design — a deploy must never die because a beep did not play.
- Wired at **all five** waiting `pause` sites in `deploy_marketsquare.bat`. The three **ABORT** pauses
  matter more than the success one: a deploy that stopped on a gate failure and was never seen is the
  expensive version of this fault. (Line 30's inline guard is left alone — it fires before `%PROJECT%`
  exists, so a `call` there would itself be broken.)
- **`start_session.bat`** reordered: `start "" "claude:"` was step 4 of 4, so the script printed the
  whole SESSION READY summary — git warnings included — underneath the window it had just raised, then
  closed itself 12 seconds later. That summary was never unread; it was never **seen**. Claude now
  launches as the last action, after the timeout.
- **RG-0183 LOCKED**, as a class: any future session adding an abort path that waits silently trips it
  red. The first cut of that assertion **could not fail** — it searched for `notify_attention` in the
  preceding lines and matched its own explanatory comment. It now requires an actual
  `call ...notify_attention.bat`, and was proven against three deliberately broken variants.
- **NOT PROVEN ON THE MACHINE:** PowerShell cannot run from the Linux sandbox. Double-clicking
  `notify_attention.bat` self-tests it in two seconds.

### CSP-SCRIPT-SRC-2 — the half of 031 that did not take, and said nothing

The 24 Aug 22:47 deploy ran migration 031 and recorded **ok**. Half of it worked:
`GET /?cb=…` went from **no security headers at all** to all five, on a cache MISS. **INDEX-HEADERS-1
is genuinely closed — RG-0179 promoted to LOCKED on that probe.**

The other half did not take. The served policy is still `frame-ancestors 'self'`, no `script-src` —
**and 031 reported success anyway.** That is my mistake, and it is the exact class this repo keeps
relearning: **it declared success from the WRITE, not from a PROBE.** It asserted the string landed in
the file it had chosen, ran `nginx -t`, reloaded, and never asked the server what it now serves. A file
write is READ-grade evidence; only the response is PROBED. 031 also globbed `/etc/nginx/*.conf`,
`snippets/`, `conf.d/` and `includes/` but **not** `sites-enabled/` or `sites-available/`, so a CSP
declared in the vhost itself was never a candidate.

**`migrations/033_csp_verify_served.py`** — rewrites *every* `add_header Content-Security-Policy` under
`/etc/nginx` including the vhost, then fetches `127.0.0.1` with a `Host:` header and reads the policy
off the **response**. If `script-src` is not in what the server actually returns, it restores every
backup, reloads, and exits 1. A migration that cannot prove its own effect must not claim it.

### Also

- **`migrations/032`** first fill died with `ModuleNotFoundError('data_flights')` — Python puts the
  **script's** directory on `sys.path`, not the CWD. Fixed. The cron itself installed correctly and
  runs from the live root, so the fare cache fills at 06:20 either way.
- **RG-0182 LOCKED** — the fares lane is deployed and correctly dark, proven by the probe built to tell
  the two dark states apart: `/flights/indicative?map=za` → 404 `{"detail":"flights lane is dark"}`,
  our guard speaking, not FastAPI's `{"detail":"Not Found"}`. Before the deploy the same probe read
  NOT DEPLOYED.

**Verification:** ledger exit 0 · 176 entries · 158 holding · **0 regressed** · 18 open.
