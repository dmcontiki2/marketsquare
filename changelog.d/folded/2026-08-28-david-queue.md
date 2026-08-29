## 2026-08-28 — DAVID-QUEUE-1: the hand-off queue that re-verifies itself

**DAVID-QUEUE-1** · built after David asked for his open actions served one at a time while he works

David is working from home today and wants the remaining open actions one at a time, to pick up in
gaps. The list itself is the easy part. The constraint worth designing for is the one that has
actually been costing him: **a hand-off list going stale across a session break.**

The evidence that this was the right thing to design against came from the same morning. The
Google consent screen and the domain registrar had **both sat in the David-only column for six
days across five consecutive sweeps — and neither was David's.** The consent screen took one
navigation to read ("In production", verification not required). The registrar took one WHOIS
referral (Cloudflare Inc, expiry 2026-12-30). Five sweeps copied both forward as his errands
without once opening the page. A queue reconciled only by a human reproduces exactly that.

So `DAVID_QUEUE.md` is read by `scripts/david_queue.py`, which **re-runs each item's stated
verification** rather than trusting the file's own STATE column:

- `LEDGER:<id>` — closes when that regression-ledger entry stops failing (strongest)
- `FIELD:<name>` — closes when that field in the third-party register is filled
- `DAVID` — **no instrument can see it**; closes on his word, with the date recorded

The three grades print unequally on purpose. A David-confirmed "done" is a weaker fact than a
probed one, and flattening them together is how the evidence ladder gets quietly abandoned.

Twelve items, ordered by dependency then by risk reduction per minute of his attention — D3
(the dead RED-alert Resend key) is deliberately ahead of D4 (the uptime watcher) because the
runbook says the watcher must take the fresh key, not the burnt one.

**Not reused: `AWAITING_DAVID.md`**, which was marked superseded in July. Reusing it would have
resurrected a dead file; the reuse-before-recreate rule was checked first and correctly said no.

Asserted by ledger **RG-0199** (OPEN by design — an empty queue is the only passing state).
`--check` mode exists so the ledger can test the instrument without an open queue reading as a
broken proof.

**Also this run:** the register's dated header was corrected — the 27 Aug sweep's "2 days to soft
launch" had silently become wrong overnight, which is the undated-status defect the file exists to
catch. And `SESSION_COUNTER.json` was re-derived (180 → 181) after RG-0154 went red on this
session's own changelog fragments — the mechanism working exactly as intended.
