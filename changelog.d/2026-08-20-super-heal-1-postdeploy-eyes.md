## 2026-08-20 — SUPER-HEAL-1 + POSTDEPLOY-EYES-1: why the deploy didn't bring the supers back, and why that class ends here

David deployed, the supers stayed gone, and his verdict was the right one: *"This is our old
recurring, lets work 4 hours on it problem all over."* Two separate faults, both now fixed at the
class, not the instance.

**Fault 1 — the every-deploy self-heal only healed ABSENCE, never STATE.**
`seed_super_global.py` is the idempotent step post_deploy runs on every single deploy, and its own
contract says it *"skips any listing whose exact title already exists."* A super that exists but
has been **hidden** (`listing_status` faded/archived) therefore looked perfectly healthy to it —
so redeploying could never bring one back, no matter how many times David clicked. The only thing
that could heal state was the one-shot migration 027, sitting behind a chain that has jammed
before and silently (023 blocked 024–026 from 18 Aug for three days).

*Fix:* `heal_hidden_supers()` in `seed_super_global.py`, running on **every** deploy, before the
in-sync early exit (a hidden super now counts as work, so the "nothing to do" shortcut can never
skip it). Unit-proven against a synthetic DB: heals faded and archived supers and showcase rows,
clears stale fade stamps, **leaves a real seller's faded listing alone**, idempotent on re-run,
and a no-op on a schema without the flags. Migration 027 stays as the belt to these braces.

**Fault 2 — nobody could see what a deploy's post-steps actually did.**
This is the real reason these become four-hour mornings. After the deploy there was no way, short
of SSH, to answer: did the seed run? did the migration chain jam? on which migration? The failure
was invisible, so the session guessed — and guessing is what burns the hours.

*Fix:* `post_deploy.sh` now records every step's outcome and writes
`$LIVE/static/post_deploy_status.json` **on EXIT via a trap**, so even an aborted run leaves its
story behind. Readable over plain HTTP with no credential (`/static/post_deploy_status.json`), so
any session — or David on his phone — can see it. A failed migration names itself and says
`CHAIN JAMMED HERE`. Exercised locally against a deliberately failing migration: it correctly
reported `migration:099_bad.py failed` and that everything behind it was skipped.

**Ledger.** RG-0124 added (OPEN — deliberately FAILS while the artefact is absent, because
"absent" IS the blind state it exists to end; flips READY TO LOCK on the deploy that carries it).
RG-0123 extended: its source half now asserts the seed heals STATE, so a future session cannot
quietly return `seed_super_global.py` to healing absence only — which is precisely this recurrence.

**What David does:** one more deploy. The supers come back through the seed lane this time, which
cannot be jammed by a stuck migration.
