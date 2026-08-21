## 2026-08-21 — TUPPENCE-DORMANCY-1: the sweep that makes EULA §6.3's expiry promise true

David: "I think we should build the sweep to comply?" Built.

EULA §6.3 has promised since v1.13 that unused Tuppence expires after 24 consecutive months
of inactivity AND that we email the holder not less than 30 days beforehand. **Nothing on
disk implemented either half** — we published a notice commitment we could not keep. That
promise now leans harder on the 24-month clock because the 21 Aug termination reconciliation
uses the same window for retention.

**`scripts/tuppence_dormancy.py`** (289 lines, stdlib only, runs anywhere like the ledger).

Design — the notice is a HARD PRECONDITION, not a courtesy:
- Nothing is ever expired unless a warning was actually sent AND is at least 30 days old.
  No warning on record → HOLD, warn first, expiry deferred. Warning too young → WAIT.
  The failure mode is "expiry is late", never "money vanished without warning".
- ACTIVITY is the LATEST of users.last_seen, users.created_at, any transactions row, any
  intro_requests row as buyer, any listing as seller. A superset is deliberate — every extra
  signal makes the user look MORE active, which can only delay expiry. Err toward the user.
- RE-ACTIVATION VOIDS A WARNING: the notice is bound to the activity timestamp it was issued
  against, so any activity moves the anchor and restarts the 24-month clock from scratch.
- DRY-RUN BY DEFAULT; `--apply` required to write. Refuses to run with `--apply` when
  RESEND_API_KEY is absent — expiry may never ride on a warning that could not be sent.
- Expiry is ONE offsetting `dormancy_expiry` transactions row, mirroring the existing
  `grant_expiry` pattern: the wallet stays a pure SUM(amount), no destructive UPDATE, full
  audit trail. Idempotent; `--limit` caps blast radius; `--as-of` allows future-dating for test.
- New table `tuppence_dormancy_notices` (additive) records every warning so an expiry can
  PROVE a notice preceded it.

Verified against a synthetic DB (5 account shapes): a recently-transacting user is untouched;
an introduction 100 days ago counts as activity and defers expiry; a zero balance is skipped;
a 26-month-dormant account with no warning is HELD and warned instead of expired; a 5-day-old
warning does NOT permit expiry; a 40-day-old warning DOES; and a dry run leaves the wallet
byte-identical.

**Regression ledger RG-0129 (LOCKED)** asserts BOTH halves of the class so neither can rot:
the sweep must keep existing with the notice as a hard precondition (24-month constant,
30-day notice, notices table, dry-run default, the age check, the no-warning refusal), the
EULA must keep saying retained-not-forfeited with fraud-only forfeiture, and the no-cash-out
rule must never be softened (the load-bearing Banks Act protection). **Tripwire proven** —
seven deliberate reversions were each injected and every one turned the entry red; the intact
state is green.

OPERATIONAL NOTE — nothing will fire for a long time, and that is correct. The oldest accounts
date from April 2026, so no account can reach 24 months of inactivity before roughly April
2028. The sweep will report zero until then. The promise exists NOW, so the machinery must
exist now; a compliance mechanism that only appears when first needed is one that is never
tested. Run it monthly (dry-run costs nothing) so it is exercised long before it matters.

NOT SCHEDULED YET — needs a monthly task, and it must run ON THE BOX (the live DB is not
readable from a session). Suggested: `python3 scripts/tuppence_dormancy.py --apply` monthly.

NOT BUILT (separate, and not asked for): the §14.1/§14.3 restore-on-re-registration path.
There is still no user-account-termination endpoint at all, so there is nothing yet to hook
retention into. Filed rather than half-built.

Cost model impact: none. Warning emails ride existing Resend infrastructure and, on today's
account ages, the expected volume is zero for ~20 months.
