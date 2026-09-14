## 2026-09-14 — The Maintenance agent was armed and 401'ing for three weeks

**What was broken.** The agent woke three times a day, could not read its own fault queue,
and did nothing. Every run ended on `intake FAILED (HTTP Error 401) -- nothing read; failing
safe, doing nothing.` The ops dashboard meanwhile said the agent was disarmed and in shadow,
which was also untrue: the timer was enabled, active, and passing `--live` the whole time.
Two separate instruments, both wrong, in opposite directions.

**Root cause.** One secret with two live values. The app runs on `MS_MAINT_KEY` from
`/etc/marketsquare/secrets.env`; the agent falls back to `/var/www/marketsquare/.env`; the
22 Aug rotation updated one file and not the other, and the agent's own first-choice key
file was missing entirely. Reproduced on localhost as `{"detail":"Admin credentials
required."}` — not Cloudflare, not the origin gate — and proven by fingerprint
(`4b5a53175fa4` vs `8997edd37072`) plus the same request returning 200 with the app's value.

**Third victim, found on the way.** `LAUNCH_CODE_SECRET` had THREE values in play.
CityLauncher signed launch codes with a key the live app does not verify with, while
redemption was enabled. Nothing was ever issued (`launch_codes` and `launch_redeem_attempts`
both 0 rows), so the cost was nil — a landmine, not a wound.

**Fixed.**
- `.secrets/ms_maint_key.txt` written 0600 from the app's own running value; intake proven
  clean on a shadow run and a systemd `--live` run.
- **Both env files aligned** so no shared name holds two values. The first attempt at this
  fix wrote only the agent's key file — a patch on one consumer — and the new probe, written
  minutes later, immediately reported the two files still diverged. The instrument caught its
  own author taking the cheaper half.
- `CityLauncher/.env` aligned to the key the app verifies with.
- `MAINT_PHASE` moved `prelaunch` → `postlaunch`, thirteen days after the runbook said to.
- `fault_report` switched ON (David's tick): `/flags` reads true and `POST /app/fault`
  answers 422 instead of fail-closing 503.
- The daily stand-up scheduled task re-enabled (David's tick), next fire 19:03Z.

**Asserted, so it cannot come back quietly.** New ledger entry RG-0362 with a harness,
`scripts/secret_divergence_probe.py`: no shared name holds two values; the agent's key file
matches the running app; no intake failure since the key file was installed; CityLauncher
signs with the key the app verifies with. Fingerprints only — no secret value is ever printed
or transported.

**The lesson, and it is not a new one.** This hazard was ALREADY NAMED in the ledger —
*"files that hold more than one live copy (MS_MAINT_KEY, LAUNCH_CODE_SECRET x4 files)"* and
*"a THIRD copy nobody knew about"* — and nothing asserted it, so it happened anyway. A named
hazard with no assertion behind it is not a control.

## 2026-09-14 — The status compiler was jammed by a note describing the status compiler

`status_compile.py` refused for three days with *"'## Current Session' appears 3 times in
STATUS.md - expected exactly 1."* There is only ONE such heading. The other two matches were
PROSE — the 11 Sep maintenance note that explains this very machinery quotes the heading name
in backticks twice. `ANCHOR` was matched as a plain substring, so a document describing the
mechanism jammed the mechanism.

Seven fragments piled up behind the refusal while the session counter and the dashboard's
session badge drifted a sitting behind the evidence on disk (the regression ledger's RG-0154,
red on today's board).

Fixed at the class: `_heading_positions()` / `_count_headings()` / `_find_heading()` count a
match only where it STARTS A LINE. Prose quoting a heading can never be mistaken for one
again. The seven fragments then folded cleanly (`folded 7, skipped 0 - verify OK`) and the
session counter reads OK.
