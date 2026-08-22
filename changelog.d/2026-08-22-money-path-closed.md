## 2026-08-22 — the money path closed: charged exactly once, and the EULA's hold made real

David: *"Why cant we close it now then?"* and *"lets go for clear"*. Both were code fixes, and
code fixes do not wait on anything reserved to him. Two LOCKED entries, both proven by replay
against throwaway replicas — no production data, no production box.

### INTRO-CHARGE-ONCE-1 (RG-0142 → LOCKED)

The 22 Aug forensic audit EXECUTED the attack: four accepts on one introduction produced four
`intro_deduct` rows and a balance of **-3T**. `accept_intro` tested neither the introduction's
status nor `tuppence_charged` before charging, read no balance, and its read-check-write was
not one transaction.

Now one immediate transaction: re-read under the lock → **409** on a settled or already-charged
introduction → **402** below 1T → then a **conditional UPDATE whose rowcount is the single
source of truth**. Two concurrent accepts cannot both win, which an `if` statement can never
guarantee. `decline_intro` refuses to decline a charged introduction, so the "paid for, recorded
declined, no refund" state is unreachable.

**Hardening found on the way:** `get_db()` uses sqlite3's default isolation level, so a bare
`BEGIN IMMEDIATE` raises when a transaction is already open. Safe today (only SELECTs precede
it) but one refactor from 500-ing every accept — it is now attempted and tolerated, because the
guarantee lives in the UPDATE, not the lock.

`scripts/prove_intro_charge_once.py`, 16 checks: four accepts leave ONE money row and a 0T
wallet; a 0T buyer is refused 402 with nothing written; decline-after-accept refused. It also
asserts the guarded SQL is the text actually in `bea_main.py`, so it cannot pass against drifted
source.

### INTRO-HOLD-1 (RG-0145 → LOCKED)

The shipped EULA promises in four clauses that 1T is **committed (held)** at request, **burned**
only on delivery, and **released in full** on decline, expiry or withdrawal. The ECT Act s44
cooling-off argument rests on it: *"Until delivery, the Tuppence is only held, not spent."*
**No hold existed.** Users had agreed to a mechanism that was not implemented — a
misrepresentation rather than a bug.

The wording was NOT changed: it is legally load-bearing and RUL-020 released the EULA as final.
The code now keeps it. `create_intro` refuses below 1T (**402**) and writes a real `-1`
`intro_hold` row, so the buyer sees the commitment in their balance immediately. `accept_intro`
**burns** that hold with a zero-amount `intro_burn` audit row rather than deducting again — the
ledger stays append-only. `decline_intro` and the expiry sweep both call `_release_intro_hold`,
a conditional UPDATE on `hold_released_at IS NULL`: releasing twice would **mint** Tuppence, so
the rowcount is the only authority.

**The expiry release matters twice over** — that sweep's email already told the buyer *"You were
not charged"*, which only became true once the hold was returned.

Schema: `migrations/030_intro_hold.py`. Intros created before it carry `held=0` and take the
legacy charge-on-accept path; **no money is retro-held from live wallets.**

`scripts/prove_intro_hold.py`, 22 checks: 3T → hold → 2T; delivery burns it with exactly one
negative row; decline returns it to 3T; expiry likewise; a second release is impossible; a 0T
buyer is refused rather than going negative.

**Both need the deploy to reach customers, and migrations 029 + 030 ride with it.**
