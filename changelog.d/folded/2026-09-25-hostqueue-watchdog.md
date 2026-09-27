## 2026-09-25 — Claude's hands stopped for 7½ hours and nothing noticed (HOSTQUEUE-WATCHDOG-1)

`autodeploy_agent.bat` on David's PC — the executor behind HOST-QUEUE-1 (RUL-095) and the deploy
path (RUL-092) — last completed an action at **13:15:06Z**. At the 20:38Z stand-up it had not
ticked for **7h31m** against a ~20-minute cadence.

- **What it cost, measured not assumed:** `git log origin/main..HEAD` = **5 commits stranded**,
  none of them on the mirror and therefore none deployable — among them `eef4097 INSPECT-FIX-1`,
  the 25 Sep inspection's critical fixes (introductions unlocked where the server accepts, seller
  text can no longer carry code, the Local Market deep link no longer charges the buyer, Plans
  upgrades apply, Quick cars publish). The origin pulls from the mirror on its own timer, so the
  one broken link in the chain was local → mirror, which needs that PC's credentials.
- **Why nothing caught it.** Every site-facing instrument read green all evening and was right to:
  the site was fine. STANDUP-WATCHDOG-1 watches the stand-up's own freshness; nothing watched the
  lane that carries work off this machine. A healthy site is not evidence that the way to change
  it is open.
- **Detector — `_hostqueue_lane()` in `scripts/maintenance_agent.py`, beside the stand-up lane.**
  Two signals, because 25 Sep tripped only the second: (1) a permission-backed `.req` queued past
  **two whole ticks** — one missed tick is ordinary, two is an executor that is not running;
  (2) **commits ahead of the mirror for more than a tick**, which is the harm itself and happens
  with nothing queued at all. Either reads STALLED and names the oldest item.
  Deliberately *not* "have results appeared lately": the agent only writes a result when there is
  work, so quiet is normal and would have produced a false alarm every idle night.
- Local-only by construction — `host_queue/` is gitignored, so the lane skips on the origin
  (BACKUP-ORIGIN-SKIP-1's precedent) rather than reporting a confident verdict from a vantage that
  cannot see the queue. Never raises; an unreadable queue reports UNKNOWN, never OK (RG-0187).
- `scripts/test_hostqueue_watchdog1.py` is **red on the pre-fix source** and pins both signals plus
  the three ordinary states that must NOT report trouble.

**Not fixed from here:** starting the agent needs that PC. The queued push
(`20260925-203849-091_git_push_marketsquare.req`) runs by itself on the next tick, so this
self-heals the moment the machine is awake — and from now on it says so instead of going quiet.
