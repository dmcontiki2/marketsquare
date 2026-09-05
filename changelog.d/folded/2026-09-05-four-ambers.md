## 2026-09-05 — the four ambers cleared, each at the class (David: "can you please fix these ambers")

**GATE-ONESOURCE-1 — the admin gate has ONE source (RG-0196 LOCKED, deferred since 27 Aug).**
`shared/admin_gate.js` is the source; `scripts/sync_admin_gate.py` inlines it verbatim into
`dashboard.server.html`, `marketsquare_admin.html` and the local `dashboard.html` between
`ADMIN-GATE-SRC` markers. INLINED rather than `<script src>` because `dashboard.html` is opened over
`file://`, where origin *null* cannot load `/static/*.js` — the obvious fix would have broken the one
copy David actually opens (RG-0076). Nothing about how any page is served changed, so no new lockout
surface (RUL-027). **The diff proved the deferral had a cost:** the copies had drifted a THIRD time —
DEVICE-ENROL-1 (3 Sep) had reached two of three and not `dashboard.html`, which was still calling a bare
`showGate()`. RG-0075 passed throughout, because it checks the two messages it knows about; drift does
not announce which line it will pick next. RG-0075 keeps the drift check independently, so a broken
generator cannot satisfy both halves at once. PROBED on the live box: `dashboard.html` and `admin.html`
both carry a gate block hashing `daddd506`, byte-identical to the source; every `<script>` block in all
three files re-parsed clean under `node --check`.

**FEA-BASELINE-AUTO-1 — the DEPLOY re-baselines the integrity sensor, not a human (new RG-0281, DW-090).**
Fourth instance of one class (DW-061 21 Aug, DW-064 26 Aug, DW-088 1 Sep, DW-090 today): every deploy
legitimately changes the three files `fea_integrity_check.py` fingerprints, so every deploy left it in
`status: alert` until somebody ran `--update-baseline` by hand — each refresh lasting exactly one deploy,
once running to eight silent ones. `ops/autodeploy/post_deploy.sh` now does it, **gated** on each live file
being byte-identical to the source that deploy placed (`?v=` cache-busters normalised, since the deploy
engine rewrites those in place after placement). Any mismatch and the step REFUSES and lets the alert
stand — that mismatch IS the tamper case. **Proven by the first deploy that rode it:**
`/static/post_deploy_status.json` carries `fea_baseline: ok — refreshed after clean deploy (3/3 files
match source)` at 11:13:49Z, and the on-box check reads `status: ok, alerts: []` straight after a deploy
that changed all three files.

**OPTOUT-PROBE-ISOLATE-1 — RG-0241 measures its own row, not a shared total (DW-093 residual).**
The entry read `/optout/status`'s global row count before and after its own probe, so it could not tell its
own write from anybody else's; on 4 Sep a concurrent session made it report REGRESSION about a bug that was
not there. `/optout/status?email=` now answers for ONE address, and **refuses real addresses with HTTP 400**
so it can never become an oracle for whether a person is suppressed. A tripwire that fires on concurrency
gets muted, and the next true red is muted with it.

**DW-095 — cost sweep exits 0 with zero warnings**, on the class fix landed earlier the same day (RG-0275):
`claude-relay` is the git branch the deploy pushes to and cannot cost a cent. The loop mattered because
recording the finding wrote the string into the register and the coverage map, which the next sweep scanned
— 5 → 13 warnings while the item stayed open.

**Board:** DEFENCE_COVERAGE_MAP.html now reads **65 green · 0 blue · 0 amber · 0 red · 10 grey** (75 cards)
— fully green for the first time. Narrowly: every card is armed AND asserted today; the ten greys are
accepted postures with stated reasons. Register: 1 item open (DW-087, the Monday static-scan lane, LOW).
