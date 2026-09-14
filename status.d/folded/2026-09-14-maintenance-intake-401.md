# MAINT-KEY-DRIFT-1 — the Maintenance agent was armed and 401'ing on every run
**14 Sep 2026 · attended (David: "We need it armed because we are live")**

Written as a NEW fragment, not an edit of the large registers (standing Edit/Write ban on
this mount). Fold into FAULT_REGISTER.md / OPEN_LOOPS.md from a session with a working shell.

## What the instruments said vs what was true
`/dashboard/maint` reported `armed:false live:false` and "SHADOW (kill switch OFF)".
**Both were stale.** On the box: `maintenance-agent.timer` enabled + active, drop-in carried
`MAINTENANCE_AGENT_ENABLED=1`, and `ExecStart` passes `--live`. The agent has been running
LIVE 3x/day (05:20 / 11:20 / 17:20 UTC) the whole time. The dashboard was showing a stale
heartbeat from an ad-hoc shadow invocation, not the systemd one. Same defect class as the
22-day-old dashboard section (RG-0354) and the wave-hygiene witness (RG-0353): an instrument
asserting a state nothing was producing.

## The actual fault — ROOT CAUSE PROVEN
Every live run ended at the first step:
`[maint] intake FAILED (HTTP Error 401: Unauthorized) -- nothing read; failing safe, doing nothing.`

Not the origin gate (GATE-COOKIE-1) and not Cloudflare (UA-EDGE-1). The 401 came from the
app itself, reproducible on **localhost**: `{"detail":"Admin credentials required."}`.

`_require_maint` accepts `X-Maint-Key` when it matches `MS_MAINT_KEY`, else falls through to
`_require_admin_or_key`, which 401s. The agent's key did not match the app's:

| source | who reads it | MS_MAINT_KEY fingerprint |
|---|---|---|
| `/etc/marketsquare/secrets.env` | the running app | `8997edd37072` |
| `/var/www/marketsquare/.env`    | the agent's fallback | `4b5a53175fa4` |

`.secrets/ms_maint_key.txt` — the agent's FIRST-choice source — was **missing**, so it fell
through to the stale `.env`. Proof of cause: the same request with the running value returns
**200 `[]`**.

The divergence is almost certainly the 22 Aug rotation (20 credentials, RG-0146): the app's
copy was rotated, the legacy `.env` the agent lane still reads was not.

## Fixed this session (both verified on the box)
1. **`.secrets/ms_maint_key.txt` written (0600)** from the running process's own value —
   the agent's designated first source, so it can no longer fall through to the stale file.
   Verified: shadow run and systemd `--live` run both read the queue, no 401.
2. **`MAINT_PHASE` prelaunch -> postlaunch.** The runbook says change it after 1 Sep; it was
   still `prelaunch` on day 13 of being live, i.e. running under the LOOSER guard.
   `armed.conf` rewritten, `daemon-reload` done.

Verified run, 14 Sep 03:42:36Z:
`mode=LIVE phase=postlaunch trust-core=GUARDED rate<=3/h ... (0 seen, 0 acted)`

`0 seen` is now TRUE rather than blind: `GET /admin/faults?status=new` returns `[]` because
the queue is genuinely empty — see the next item for why it must be.

## STILL OPEN — named, not parked
- **[D] `fault_report` is OFF** (`/flags -> fault_report:false`). The armed agent's only
  in-app intake does not exist; the REPORT tab is hidden and the lane fail-closes. An armed
  agent with no queue is an expensive no-op. David's flag.
- **[D] `LAUNCH_CODE_SECRET` has the SAME divergence** between the two files (fingerprints
  differ). Second victim of one root cause. Whichever component reads the stale copy will
  mis-handle launch-code redemption. Needs David's call on which file is authoritative.
- **[C] The brain-keyed chip lies.** `keyed = [n for n in names if os.environ.get(n)]`
  (maintenance_agent.py ~L765) reads `os.environ` ONLY, while the brain itself resolves keys
  through `ai_provider.envkey()`, which also reads `/var/www/marketsquare/.env`. On the box
  OPENAI / GEMINI / FAILOVER all resolve via envkey but none are exported to systemd, so the
  agent reports KEYLESS while being able to think. One-line class fix (use `envkey`), NOT
  made this session: the nightly ship auto-commits, so an unrequested source edit would
  deploy itself tonight.
- **[C] Class fix for the root cause:** one authoritative secret file, or the agent reading
  `/etc/marketsquare/secrets.env`. Until then any future rotation re-breaks this the same way.

## THIRD VICTIM — found and closed, same session
`LAUNCH_CODE_SECRET` had **three** live values, not two:

| holder | role | fingerprint |
|---|---|---|
| `/etc/marketsquare/secrets.env` → app process | **verifies** codes | `da36086d6891` |
| `/var/www/marketsquare/.env` | stale copy | `b8aab96a9aff` |
| `CityLauncher/.env` | **issues** codes | `b8aab96a9aff` |

CityLauncher was signing with one HMAC key and the live app verifying with another, while
`LAUNCH_REDEMPTION_ENABLED=1`. Every launch-special code issued would have been rejected.

Cost so far: **nil** — `launch_codes` 0 rows, `launch_redeem_attempts` 0 rows. Nothing was
ever issued, so no customer was turned away. It was a landmine, not a live wound.

**FIXED:** `CityLauncher/.env` aligned to the app's value (backup written alongside as
`.env.bak-launchsecret-<ts>`). Both now `da36086d6891`. No app-side change; the rotated
value stays authoritative.

## The standing lesson
`scripts/regression_ledger.py` ALREADY names this hazard — "files that hold more than one
live copy (MS_MAINT_KEY, LAUNCH_CODE_SECRET x4 files)" and "a THIRD copy nobody knew about".
The ledger described the trap and nothing enforced it, so MS_MAINT_KEY drifted at the 22 Aug
rotation and silently disarmed the Maintenance lane for three weeks. A named hazard with no
enforcing assertion is not a control. The class fix is one authoritative secret file with
every consumer reading it — until that exists, the next rotation breaks this again.

## Closed with David's word, same session
- **`fault_report` ON.** `POST /admin/flags {"fault_report":true}` with a minted admin token
  (the route is JWT-only; `X-Admin-Key` 401s there) + an audit reason. Verified on the public
  edge: `/flags -> fault_report:true`, and `POST /app/fault` now answers **422 (validation)**
  where it previously fail-closed with **503**. The lane is open.
  *Not yet eyeballed:* the REPORT tab itself renders behind sign-in, so this is verified at
  the API layer only — the 9 Aug "done means RENDERED" rule is not satisfied until someone
  signed in looks at the tab.
- **Daily Agent Stand-up re-enabled**, `0 19 * * *`, next fire 2026-09-14T19:03:58Z,
  model `claude-opus-5` confirmed stored. Pulse resumes tonight.
