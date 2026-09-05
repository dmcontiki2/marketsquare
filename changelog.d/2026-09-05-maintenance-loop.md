## 2026-09-05 — Maintenance loop: SSH lockout healed AND scheduled; two instruments stopped lying

**Fault queue: EMPTY.** Shadow agent run 2026-09-05T05:45:58Z — 0 new faults, 0 acted;
35 rows total (26 verified, 7 closed, 2 duplicate). Heartbeat posted and read back from
`/dashboard/maint` (`received_at 2026-09-05T05:46:16Z`). No escalations in 24h, so
`escalation_brief.py` wrote no brief. The session's work therefore came from the ledger red
and the watch register, which is what those instruments are for.

**RG-0099 red — SSH-LOCKOUT-1 recurred, healed, then FIXED AS A CLASS (FW-SELFHEAL-SCHEDULED-1).**
Port 22 at the origin timed out on 3/3 probes while a control host answered, so the vantage was
fine and the origin was not: the Hetzner SSH allowlist still held `197.185.137.157/32` from a
router reset while the live egress was `197.184.107.115`. `hetzner_fw_selfheal.py` set the rule to
the live IP and pruned the dead one (NO-STALE-IP-1). PROBED after: TCP :22 open 3/3,
`ssh root@178.104.73.239` returned `ubuntu-4gb-nbg1-1` / uptime 2d 12:58, RG-0099 and RG-0188 both
HOLDING. **The recurrence engine was that nothing ran the cure** — it has existed since 17 Aug and
RG-0188 proved it executable, but a grep across every `.bat` found ZERO schedulers, so all three
reds (26 Aug, 2 Sep, 5 Sep) waited for a human to notice. The healer now runs on every tick of
`autodeploy_agent.bat` (20 min, on the host that owns the egress the allowlist must name),
deliberately ABOVE its no-request early exit so quiet days are covered, with its exit code
discarded so a Hetzner API hiccup can never block a deploy. It can only ever name the IP of the
machine that ran it, so it cannot lock anyone out — it is the anti-lockout.
**New ledger entry RG-0274 (LOCKED)** asserts the wiring and its ordering. Closes DW-096.

**RG-0138's liveness half was a READ wearing a PROBE's colour (WATCHER-LIVE-PROBE-1).**
The external uptime Worker — the last watcher standing when SSH is down — proved itself alive by a
`LAST_HEARTBEAT:` date SOMEONE TYPED into a markdown file, failing only when that date was over 7
days old. Today the age was exactly 7, so **6 Sep would have read REGRESSION by arithmetic alone in
an unchanged world**. It now GETs the Worker's public endpoint (URL taken from the deploy marker,
not hardcoded), requires a real check result with KV bound and a timestamp under 15 minutes old,
and raises `ProbeOffline` → UNVERIFIED (never RED) when this machine cannot reach it. Evidence this
run: `ran a real check at 2026-09-05 05:53:02 UTC (site ok=True, 200 in 187ms), KV bound`. The typed
date survives as INFO only — it records the day a heartbeat MAIL was witnessed, which is the ALERT
half (DW-097), not liveness. Strictly stronger than the date read, never weaker. Closes DW-098.

**The cost sweep was manufacturing its own findings (RELAY-NOT-A-MODEL-1).**
`cost_compliance_sweep.py --quiet` exited 1 with 13 WARN lines, up from 5 the day before, all of
them `unknown model family claude-relay`. `claude-relay` is the GIT BRANCH `request_deploy.py`
pushes to (`HEAD:refs/heads/claude-relay`) — never a model family, never billable. Left
unclassified it WARNed, and recording each WARN wrote the literal string into
`DAILY_WATCH/OPEN_ITEMS.json`, the coverage map and the ledger, so the next sweep found it there
too: a feedback loop, not drift. Classified alongside `mem` in `KNOWN_NON_MODELS`, exactly the
DW-047 (`claude-fable-5`) precedent — the name is classified, the check is NOT muted, and a genuine
unknown family still WARNs. Evidence: exit 1 → exit 0 the same minute, 0 CRITICAL, every real call
site still ceiling ✓ spend-log ✓. **New ledger entry RG-0275 (LOCKED)** asserts the classification
and reads back the newest sweep report. Closes DW-095.

**Board:** 268 entries · 249 holding · 0 REGRESSED · 18 open · 0 ready to lock · 0 UNVERIFIED.
`rulings_check.py` 94 rulings, 0 FAIL, 6 WARN (RUL-093/094/095/098/099/100 carry no reflection
assertions — notes, not guarantees).

**Two honest notes.** (1) The full board reported RG-0229 (opt-out lane) REGRESSED once during the
post-work run, with self-contradictory text — `0 of 5 gates failing` alongside `RESULT: 5/5 gates
pass`. Re-probed in isolation four times: HOLDING every time, `all five gates pass`. Treated as a
false red of the DW-093 class (a stdout capture read under load), not a rotted fix; the assertion
itself was not touched. (2) This session ran the ledger through a scratch chunked driver in `/tmp`,
because the Cowork sandbox caps one bash call at ~180 s and reaps background processes at the call
boundary (BRAIN-DEPS-2), while a full board takes longer than the cap. The driver calls the
ledger's own `run()` on slices — no assertion logic is re-implemented and no repo file was involved.

**DW-097 stays OPEN and is the one thing worth David's eye:** the daily watch's alert email is sent
by SSH-ing to the origin, so on a day the origin is unreachable — exactly today — the alarm cannot
be raised. The watch's RED verdict reached nobody by mail. The fix (an alert path on the Cloudflare
Worker, which has its own egress and its own Resend key) needs a Worker deploy and is not a
sandbox-reachable act; it is tracked in the watch register.
