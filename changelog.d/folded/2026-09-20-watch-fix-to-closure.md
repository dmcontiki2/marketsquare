## 2026-09-20 — Daily watch: four open items fixed to closure, and the blindness that hid a real fault

David, on reading the morning's GREEN watch report: *"please fix all of them to closure"*. Four of
the five were Claude's; the fifth is two sign-offs that are his. Every fix is ASSERTED, not just made.

**DW-138 — RG-0238 promoted OPEN → LOCKED, and widened.** The rule that no listing surface may call a
PERSON safe was passing but still filed as a known-broken item, so a real breach would have read as
business as usual. Promoted, and strengthened rather than merely re-stated: **7 surfaces** instead of 2
(both composer doors, both legal surfaces, plus `bea_main.py` where badge text now originates —
*with comments stripped first*, because that file carries the word "vetted" in a design comment and a
guard pinned to a spelling would have gone red against correct code). The **absence-of-record** half of
its own scope — banned in words since 1 Sep, never implemented — is now checked. Proven to bite on four
injections; the same word in a comment correctly does not fire.

**DW-137 — SAFE-READ-1 (`scripts/safe_read.py`, RG-0421).** A read of a just-written file on this FUSE
mount can come back short with no error (19 Sep: 29,737 bytes of a 318,127-byte file). That is dangerous
because a `cp` backup is the only undo here, so a session that reads back short "restores" from a file it
misread — the recovery step becomes the data loss. `settled_read` re-reads until two consecutive reads
agree and raises rather than returning a short read; `verify_after_write` compares against the writer's
own bytes; `safe_backup` proves the copy. Wired into `changelog_compile.py` and `status_compile.py`,
which were both verifying folds on a single immediate read. A concurrent session hit the same fault
through `inspect.getsource()` within the hour and its RG-0423 now reads through the same helper.

**DW-136 — DEPLOY-GATE-ALL-1 (`.git/hooks/pre-push`, RG-0422).** On 18 Sep a deploy rode while the board
read REGRESSION, via the raw `git push origin HEAD:deploy` lane the runbook documents. A pre-push hook now
fires on `refs/heads/deploy` only, runs `predeploy_check.py` with `PREDEPLOY_MODE=strict` set *before* the
scan, and refuses the push on DANGER. Proven on four legs: DANGER → exit 1 refused; `PREDEPLOY_MODE=warn`
→ allowed; pushing `main` → untouched; real tree → REVIEW, allowed. Installed by
`scripts/install_git_hooks.py` (idempotent, `--check`). Residual stated: hooks are local to a clone.

**DW-111 — JOURNAL-READ-1 (migration 045, RG-0424), and the lesson of the day.** This sat OPEN for
**nine days** as "a Resend lane failing every five minutes that no instrument here can see". Nine sessions
re-probed the same wall and wrote the same honest, useless sentence. One group membership
(`msdeploy` → `systemd-journal`) made the journal readable, and the question was answered in four minutes:
**there is no failing lane.** `_infra_resend()` posts an empty body to Resend on purpose — 422 means
*auth passed, nothing sent* — and the +1 dashboard polls it every five minutes. A second 422 class
(`POST /app/fault`, 228× in 24h, zero successes) looked like a six-day tester outage until the nginx
user-agent read `TrustSquare-RegressionLedger/1.0` — our own probe asserting the endpoint refuses
unauthenticated reports. **Both 422 classes were instruments succeeding.** The blindness was the defect,
not the thing it hid.

**DW-139 — NEW, live, and handed over rather than fixed.** Within minutes of the journal opening:
`POST /i18n/translate` returning **500 on ~87% of calls** (262 vs 39 in fifteen minutes),
`sqlite3.OperationalError: database is locked` at `main.py:25082` — the translate cache is written on the
request path. It belongs to the concurrent session that shipped I18N-TRANSLATE-1 at 17:10Z; editing
`bea_main.py` underneath them is the CHANGELOG-COLLISION-1 class, so it was recorded, not touched.

Coverage map: **86 green · 2 blue · 0 amber · 1 red · 11 grey** (was 82/3/3/0/11) — the amber column is
empty for the first time. Ledger: 411 entries · 388 holding · 0 ready to lock · 0 UNVERIFIED.
