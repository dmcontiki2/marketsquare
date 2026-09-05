## 2026-09-05 — a permission-backed request vanished without a word (REQ-COLLIDE-1)

Queued two commits a second apart, listed the queue, and found ONE file. `host_queue/*.req`
names were built from the ARGUMENT'S FILENAME, so `MarketSquare\commit.bat` and
`CityLauncher\commit.bat` both became `<timestamp>_run_bat_commit` — and the second
**silently overwrote the first**. No error, no result file, and `request_host_action.py` had
already printed "queued" to the caller. A permission-backed instruction simply ceased to exist.

Same shape as the 2 Aug CHANGELOG collision — two writers, last one wins, nothing raised.
There the cure was one file per fragment; here it is a name that cannot collide: the slug
carries the whole path (`marketsquare-commit` vs `citylauncher-commit`), the timestamp carries
milliseconds, and an existing name is never reused. Locked as RG-0280.

Found only because the queue was listed by eye straight after. Worth saying plainly: this
class is invisible unless something checks, which is the argument for the ledger in general.

### Three of my own assertions were wrong before they were right

Recorded because the pattern matters more than the fixes:

- **RG-0276** counted `call :fire "%%C"` — the batch loop variable — as a hardcoded city, and
  so declared the fix I had just made to be broken.
- **RG-0278** demanded every category KEY be drawable, when `TEMPLATES` deliberately carries
  several spellings per letter. The unit is the letter, not the key.
- **RG-0280's** first draft shelled out to the real `request_host_action.py` — which broke
  RG-0187's harness rule AND wrote two live requests into the production queue. An assertion
  must never cause the thing it asserts about. Rewritten pure: it exercises the naming rule
  in-process and writes nothing.

Twice today an existing assertion caught a new one being sloppy (LEDGER-DUP-1 on a duplicate
id, twice — a concurrent session was adding entries at the same time). That is the machinery
working on its author.

### Housekeeping found on the way

- `deploy_uptime_worker.bat`, arriving from a concurrent session, had **LF line endings** —
  cmd.exe misparses those. Normalised to CRLF, content byte-identical.
- It was then flagged for having no waiting prompt, but it is on the host-queue allowlist and
  runs with nobody present, where a prompt would hang the agent forever. Added it and the five
  other allowlisted scripts to the checker's UNATTENDED set (UNATTENDED-ALLOWLIST-1).
- `rulings_check.py` failed RUL-084 because it verified the ruling by looking for the literal
  string "Cape Town" **inside launch_day_wave.bat** — checking a ruling against the hardcoded
  list that was the fault. Assertion corrected to check where the truth now lives: the city is
  armed in the policy, and the bat derives its list. Not a weakening; the same fact, checked in
  the right place, plus the derivation.

Ledger green, 18 open unchanged. Rulings: 0 fail. The number is still **0**.
