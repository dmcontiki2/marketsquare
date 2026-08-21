## 2026-08-20 (evening) — The [C] lane closed: DW-051 shut, two missing assertions written, OPEN_LOOPS reconciled

Follow-on to DASH-FEED-1 in the same session. Everything below is evidenced by a full ledger run
against the live site, not by inspection.

**DW-051 CLOSED — the migration chain runs clean end to end.** The row wanted `.migrations_done`
to reach 027. POSTDEPLOY-EYES-1 now answers that with no credential:
`GET /static/post_deploy_status.json` at **2026-08-20T15:56:13Z** — seven steps, none failed:
seed ok · ladder_seed ok · **023 ok** ("applied: 0/104 listings changed; avg auto-links 4.7" — 0
because the attended run had already relinked 84/104) · **024 ok** · **025 ok** · **026 ok**
("gate is ALREADY down") · **027 ok** ("verified: 0 protected listings faded or archived").
The row's "tighten RG-0116" instruction is **superseded, not skipped**: RG-0116 asserts the import
CONTRACT in source and predates the deploy report; the chain's OUTCOME is RG-0125's, and
duplicating it would have been the collision LEDGER-DUP-1 exists to refuse.

**Three entries promoted OPEN -> LOCKED**, each on the run that proved it:
- **RG-0125** — the migration chain is not jammed. Clean through 027.
- **RG-0126** (new) — *the ledger can still tell an unstable RUN from a real regression.*
  Discharges DW-053's named residual, which had gone onto the coverage map as blue. Asserted as
  properties, not literals: the fingerprint exists, an UNSTABLE verdict exists, the exit-3 path
  exists, the watched set is >=5 files **and includes this file** — because the case that
  actually bit on 20 Aug was this file being rewritten underneath a running check.
- **RG-0127** (new) — *the ops dashboard reads the section the sessions actually write.*
  A winning `## Last Completed` heading older than **21 days** is now a FAIL. Window chosen
  deliberately: long enough that a quiet fortnight is not a false red, short enough that six
  weeks of silent rot is impossible. Live half asserts the three panels are non-empty; repo-vs-
  live drift is INFO, not FAIL, because editing STATUS.md before pushing is normal work and a
  tripwire that fires on normal work is the cry-wolf failure RG-0068 exists to prevent.

**Ledger after: exit 0 — 120 entries · 117 holding · 0 REGRESSED · 3 open · 0 READY TO LOCK ·
0 UNVERIFIED.** The three open are open honestly: RG-0075 (admin-gate script duplicated across
5 files), RG-0101 (unverifiable — its probe is 401'd, blocked on DW-028), RG-0121 (canary dark
by design until the Gemini eval).

**OPEN_LOOPS.md reconciled — the integrator had stopped integrating.** Last touched 14 Aug. **L2**
("git-on-FUSE stale .lock files, needs a real fix") had been class-fixed on **16 Aug** by
GIT-LOCK-3 and still sat in LIVE LOOPS four days later; closed with evidence (`git_unlock.bat` +
`scripts/git_unlock.py` both present; tonight's run reports `[  ok  ] RG-0015`, which tripwires
the class live at >60 minutes stranded). The file now carries a **"Last reconciled"** stamp so
the next reader can see its age instead of trusting it blindly.

**DW-057 promoted to BLOCKING NOW (B1).** Two exposures of the same production credentials —
DW-029 (7 Aug) and DW-057 (20 Aug, caused by the watch itself). The WAF allowlist is down, so the
site is publicly reachable while the old credentials are live. Going public on 29 Aug with burnt
payment and mail credentials is not a risk worth carrying, so it is no longer ranked as ordinary.
David's action: `ROTATE_SECRETS.bat`, then MS_API_KEY / MS_DEPLOY_TOKEN / FOUNDERS_ID_SALT in the
unit.

**Register now: 7 open (DW-010, 027, 028, 029, 044, 054, 057).** Five of the seven are David's
decision or click; two are Claude's and both are blocked on his (DW-028 wants the ops key, which
belongs inside the rotation).

**Not done, and named rather than quietly dropped:** DW-054 (prove the AI breaker fails OVER on a
vendor 5xx/auth failure) needs a controlled fault injection against the live provider lane — not
something to fire unattended nine days before launch. It stays open with that reason on the row.
