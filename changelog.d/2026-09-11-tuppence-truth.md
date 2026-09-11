## 2026-09-11 — TUPPENCE-TRUTH-1: the app stops inventing a wallet balance · DRIFT-PIPE-1: the unattended deploy lane has never shipped

### What was wrong

Every visitor to trustsquare.co was shown a wallet holding **50 Tuppence**. Nobody granted it.
At the rate in our own terms (1T = USD $2.00 fixed) the app was telling a cold stranger they
held $100 of stored value before they had done anything.

Origin: Session 74, 22 May 2026, a Claude session. Its own CHANGELOG entry (line 17093) reads
*"`tuppence` JS variable init: 5 → 50 (marked with 🧪 TEST comment for launch rollback) … grep
🧪 TEST to find all rollback points before launch."* The grep was never run. It shipped on
1 September and stood for ten days. Not David's change and never David's instruction — the
commit carries his name only because the commit lane signs with his credentials.

**No outreach email ever promised a starting balance.** All 18 live templates were checked: the
string "50" does not appear in any of them, nor "start with", "starting balance", "already in
your wallet", or any welcome credit. The letters mention Tuppence only as the 1T introduction
fee a buyer pays and the 20% bonus on a paid plan. The false number existed only in the app.

### Fixed

- `ms.js:676` `let tuppence=50` → `0`. The client does not invent a balance.
- `ms.js:12723` no-account wallet `'50'` → `'—'`.
- `marketsquare.html` `tn-balance-display` 50 → 0, `ms-wallet-balance` 50 → 0, `nav-tn-badge`
  5 → 0 (the badge used to render 5 and get overwritten with 50 a moment later).
- `ms.js:1026` was `if (data.balance > tuppence)` — the server could only ever RAISE the number,
  so a client default acted as a floor the ledger could not correct. **That is why a test value
  survived being wrong for ten days.** Now the ledger is authoritative in both directions.
- Both remaining `🧪 TEST` rollback markers are gone from the shipped files.

`node --check` clean. `marketsquare.html` edited via the str.replace driver only (truncation
rule): 414,425 → 414,423 bytes. **VERIFIED LIVE** in a clean browser profile (localStorage
length 2, `ms_superuser` null): cache-buster 626, served `ms.js` carries `let tuppence=0`, and
all three wallet surfaces render **0**.

### DRIFT-PIPE-1 — found while shipping the above, and bigger

The deploy would not go out. `nightly_tsl.bat` builds
`DRIFTLINE = "DEPLOY DRIFT: 3 file(s) local-ahead of live - ..."` and uses `%DRIFTLINE%` inside
`if ( … )` blocks. **cmd parses an entire bracket block before executing any of it and expands
`%VAR%` at that moment**, so the `(s)` closed the block early and the tick died with
`local-ahead was unexpected at this time`.

It only ever fired when DRIFTLINE contained brackets — that is, **only when there was something
to ship**. An in-sync tick prints no brackets and passed happily. The evidence is in the lane's
own log: every entry from 6 Sep onward reads `IN SYNC`, and in the whole of
`autodeploy_agent_log.txt` there is exactly **one** MarketSquare `SHIPPED` line (3 Sep) against
two parse deaths. Deploys have been reaching the server on the SSH relay instead; that relay was
closed today, which is the only reason this surfaced.

Fixed with `setlocal EnableDelayedExpansion` and `!DRIFTLINE!` at every use site, so the
brackets are read at run time as text. **PROVEN, not asserted:** `Fri 09/11/2026 13:51:30
SHIPPED rc=0` — the first time that lane has shipped MarketSquare unattended since 3 Sep — and
the change is live on the server.

### Two things left flagged, not changed

- `marketsquare.html:2933` and `:3561` render a button labelled **"🧪 Skip for testing"** to real
  sellers, to dismiss the banking nudge. Same class as the above; it is a flow decision, so it
  is named here rather than quietly altered.
- The release script ends in `pause` — `Press any key to continue . . .` in an unattended run.
  It survives only because stdin redirection makes it fail through (`ERROR: Input redirection is
  not supported`). It is a human-in-the-loop landmine that happens to be disarmed by accident.

### The lesson, and why no audit caught it

The 21 Aug launch-readiness forensic audit was real and thorough — three cycles, a second
vendor, a HOLD verdict. It found a non-idempotent intro charge that could double-debit a wallet
and a pre-auth balance oracle. It never found this, and could not have: its ten dimensions are
all properties of the SYSTEM — viability, economics, server capability, robustness, reliability,
maintainability, scalability, hardening, hack-proofness. None of them asks whether what the
screen tells a stranger is TRUE. The code here was correct throughout: the variable initialised,
the badge repainted, nothing threw, no endpoint misbehaved. Static analysis is clean on that
line. Three cycles audited the till, the ledger and the locks; none read the price tag.

A note is not a gate. `🧪 TEST — reset before launch` was correct, inert, and cost ten days.
