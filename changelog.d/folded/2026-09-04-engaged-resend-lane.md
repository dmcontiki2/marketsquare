## 2026-09-04 — ENGAGED-RESEND-1: the apology lane, and the stale-roster trap

**David granted new sending authority, in his own words:** *"i think we should at least
resend the ones that did open their emails?"* Added to `host_queue/ALLOWLIST.txt` with
those words attached, as RUL-095 requires. Read "at least" as a floor, so the roster is
status **opened OR clicked**, not opened alone — the clickers went one step further and
met the browser password box, and are owed the apology most. Not the 338 who only
received it; not the bounced, opted-out or rejected.

**RG-0265 LOCKED — the trap this lane nearly walked into.** Building it, the local
prospects.db showed **18 openers where the live server showed 133** (103 opened + 30
clicked). Engagement is recorded server-side, because that is where the tracking pixel
and the click redirect land. Running the existing script as it stood would have quietly
mailed the wrong 18 people, printed a success line and returned 0 — the same failure
shape as WAIT-REDIR-1 earlier the same day: a run that completes, exits clean, and did
not do the thing. The order of operations IS the fix, so it is asserted rather than
remembered: `resend_broken_link_now.bat` runs `pull_from_server.py` first and exits
non-zero if the pull fails, then dry-runs the roster, then sends.

Two guards added for unattended running: the default selection widened to the engaged
set (`status IN ('opened','clicked')`), and **ROSTER-FENCE-1** — `--send` refuses
outright if the roster exceeds `--max-roster` (250). A refusal, never a truncation: half
a wrong wave is still a wrong wave. The bat carries no `pause` and no `timeout /t`, per
RG-0262. Everything else is inherited unchanged from emailer.py: suppression register,
junk / government / privacy-officer filters, opt-out link, per-row abort on any link
still pointing at /admin.html, plus the script's own JOURNEY-1 gate that walks the
prospect path before it will send at all.

RG-0265's own assertion was wrong on first run and fixed in the same session: it matched
the bat's REM comment describing the ordering instead of the command performing it, and
cried wolf. It now reads the command list only.
