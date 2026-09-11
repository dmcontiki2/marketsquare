## 2026-09-10 — OS-SYSTEM-QUOTES-1: two fact-board checks were lying on Windows, and one told us not to deploy

Found by running the same two checks two ways in the same second (05:11:01 SAST), while the sandbox
is dead and the boards run host-side.

**The contradiction.** `boards_host.bat` ran the scripts directly on David's PC:
`session_counter.py --check` → *"OK: session 194, 39 sitting(s) since anchor"*, rc=0.
`dashboard_provenance.py --check` → *"0 unfed health chip(s), 0 orphaned id(s) … OK"*, rc=0.
One second later the ledger reported BOTH as regressions — same machine, same cwd, same interpreter.

**Cause.** Both entries invoked their script as
`os.system('"%s" "%s" --check >%s 2>&1' % (sys.executable, path, os.devnull))`.
On Windows `os.system` goes through `cmd.exe`, which strips the outer quote pair of a command that
*begins* with a quote — so the interpreter path and the script path ran together into a syntax error
and the return code was never 0, whatever the script found. On Linux the same line is correct, which
is why the sandbox never saw it; the host-side lane is one night old (SANDBOX-REPAIR-1).

**Why it mattered more than a wrong colour.** RG-0154 derives `counter_is_current` from the absence
of the "fallen behind the fragments" FAIL. The false FAIL flipped it, so *genuine deploy debt* — the
live badge serves Session 192 while the disk correctly says 194 — was voiced as a REGRESSION and the
board printed **"Do not deploy over this."** DEPLOY-DEBT-VOICE-1 (27 Aug) exists precisely to stop
the instrument arguing against its own remedy, and a quoting bug walked straight around it.

**Fix.** Both sites now use the ledger's own `_harness()` — a list-based `subprocess.run`, no shell
and no quoting — which also reports a harness that *could not run* as blind (INFO → UNVERIFIED)
rather than as a verdict, the RG-0187 contract. No `os.system` remains in the ledger; the single
surviving mention is the comment explaining this.

**Standing.** The real state of those two entries: the session counter is CURRENT on disk (194,
derived, re-derived by its own script this run) and the only outstanding item is deploy debt of two
sittings, which clears on the next ship. The dashboard provenance board is clean — 70 chips, 0 unfed.

Class, and the third instance in one night: a check that reports a failure the thing it checks does
not have. The other two were mine (RG-0349 matching its own comment; three LF-only scripts I wrote).
An instrument gets the same standard of proof as the product — run it two ways before believing a red.
