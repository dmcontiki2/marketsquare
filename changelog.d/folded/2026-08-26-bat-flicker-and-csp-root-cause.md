## 2026-08-26 — BAT-CRLF-1 · CSP-SCRIPT-SRC-7 · RG-0188 locked · four guards cleared

David: *"add secret bat flickered on and off?"* — a window that opened and shut too fast to
read, on the one script standing between him and the Hetzner token, three days before soft
launch. That question opened a thread that ran all the way to the two-day-old CSP failure.

### BAT-CRLF-1 / BAT-FLICKER-1 (RG-0194, LOCKED)
Three stacked faults, each alone enough:

1. **The repo forced LF onto Windows scripts.** `.gitattributes` carried `* text=auto eol=lf`
   — right for everything reaching the Linux server, wrong for every `.bat`. cmd.exe expects
   CRLF, and a caret line-continuation followed by a bare LF does not continue the line, so a
   15-caret PowerShell block was mangled into garbage.
2. **The caret continuations themselves.** The PowerShell call is now one line that line
   endings cannot break.
3. **No `pause` on any exit path**, and an instant exit when double-clicked with no argument.
   Every failure closed the window unread.

Scope measured, not assumed: **16 `.bat` and 10 `.ps1` files were LF-only**, including the
entire nightly deploy lane — those survived only by having no carets and no labels, and
`ROTATE_SECRETS.bat` (the secrets lane, 5 carets) was one run from the same silent failure.
All 26 normalized; `*.bat/*.cmd/*.ps1` pinned to `eol=crlf`. The new guard
`scripts/check_bat_crlf.py` then immediately found two more scripts that could exit on an
error with no pause — `arm_phone_deploy.bat` (fixed) and `publish_whitepaper_auto.bat` (named
unattended, a pause there would hang it) — which is the argument for the guard existing.

### CSP-SCRIPT-SRC-7 — the operative cause of all four 033 failures, finally named
The widened report window (POSTDEPLOY-EYES-3, shipped this morning) paid for itself on the
very next deploy. The 14:34Z report carried the line four previous reports had cut:

    served CSP BEFORE: 'ERROR:port-443-unreachable(TypeError(HTTPSConnection.__init__() go)...

`HTTPSConnection` **has no `server_hostname` parameter** — the full list is host, port,
key_file, cert_file, timeout, source_address, context, check_hostname, blocksize.
CSP-SCRIPT-SRC-5 passed one anyway, so every `:443` attempt died on the *constructor*, before
a packet moved, fell through to the `:80` fallback and measured the very 301 that fix had been
written to stop measuring. **033 could never have passed on any server.** SNI now comes from a
hand-wrapped socket: loopback for the connection, `trustsquare.co` for the SNI.

Honest correction: this morning's settle-loop diagnosis (CSP-SCRIPT-SRC-6) was a real defect
and is still fixed, but it was **not** the operative cause. It was a second bug behind the
first. CLASS: a call signature is only proven by CALLING it — `prove_csp_settle.py` now points
the real function at a dead port and demands a *connection* error, because a TypeError there
means the code cannot work anywhere, ever. 15/15.

### THE LESSON OF THE DAY — prose counted as code, four times in one session
1. `033` — an nginx comment containing `script-src` made the only stale file test as fixed.
2. `RG-0189` — a `REM` line explaining why an `echo %NAME%` had been *removed* was read as an echo.
3. `prove_csp_settle.py` — a comment quoting the deleted `server_hostname` call matched as code.
4. `test_pg_readiness.py` — a comment explaining a *removed* `datetime('now')` counted as a use.

Every one reported correct code as broken. Fixed at source in each: RG-0189 and the pg ratchet
now strip comments before matching (`tokenize`, so a `#` inside a SQL string literal is safe).
The ratchet fix auto-tightened `insert_or` 13 → 12 — it had been miscounting comments elsewhere too.

### Four guards cleared, all red for 8 consecutive scans (RG-0114 escalated correctly)
- **maintenance-agent** — `test_ack_always_sends_except_spam` pinned the spelling `MAINT-B1 ACK`;
  ONE-REPLY-1 restructured the block on 24 Aug for a better reason and the comment became
  `MAINT-B1 ack`. The acknowledgment behaviour was never lost for a moment. Rewritten to assert
  the five properties (two mutually exclusive branches, reference on both, spam never, kill
  switch, Resend-first path). Second instance in that file of the fault its own neighbour documents.
- **tester-intake** — `WAVE_PLAN_LAUNCH_2026.html` and `orchestrator.html` had no report widget.
  Added rather than argued about, since a script tag is cheaper than a category debate.
- **pg-readiness** — a release at 16:31 added `datetime('now','-1 day')`; rewritten as a bound
  Python-computed cutoff, matching the pattern already used elsewhere in the file.

### RG-0188 PROMOTED TO LOCKED
David generated a read+write Hetzner Cloud API token and entered it via the repaired
`add_secret.bat`. PROBED, not assumed: `hetzner_fw_selfheal.py --check` reached the Hetzner API,
read firewall 11414216, reported `197.184.106.176 already allowlisted (4 SSH sources)`. Nine days
of SSH-LOCKOUT-1 being detectable but not curable are over. Cloudflare half stays INFO — that
gate retires at launch and should not hold a LOCKED assertion hostage.

**Ledger: 169 ok / 17 open / 1 red.** The red is RG-0125, and it can only clear when a deploy
runs 033 again — it reads the last deploy report. Rulings 57/57.
