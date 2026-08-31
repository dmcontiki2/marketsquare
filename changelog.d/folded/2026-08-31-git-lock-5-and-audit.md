## 2026-08-31 — GIT-LOCK-5: git_unlock.py swept only one repo while reporting "nothing to sweep"; plus the answer to "what else isn't working"

David, after the GOV-DOMAIN-1 finding: *"We cant stop everything because i thought we were well
protected but the design was not implemented, and you reported it as working, now today it isn't
working. What else is not working which has been reported as working?"*

Answer by measurement, not reassurance. Full regression-ledger run: **214 entries · 196 holding ·
1 REGRESSED · 16 open · 0 unverified.**

### The one live regression — and it is exactly the pattern he named
**RG-0197 was RED**: `CityLauncher/.git/index.lock` and `HEAD.lock`, both 0-byte, **stranded 134
minutes** — the next commit in the wave repo would have failed. Running the designated healer
returned:

    git_unlock.py: no stale locks, nothing to sweep

**The tool reported clean over a live fault.** Cause: `REPO` was hard-coded to MarketSquare, so
`GITDIR` only ever pointed at MarketSquare's `.git` — while the script's own usage line says "run
before any sandbox git write" and RG-0197 asserts it "covers EVERY repo a wave or a deploy fires
from". CityLauncher, the repo the **wave lane** commits from, was invisible to it.

**GIT-LOCK-5:** `_repos()` now sweeps every sibling repo beside MarketSquare, and every line of
output carries its repo label. Verified: both CityLauncher locks healed by rename, locks clear,
RG-0197 green — *"both repos carry the self-heal … and neither holds a stranded lock"*. No new
ledger entry: the assertion was right and the code was wrong, which is the ledger working.

### A defect of my own, from last night
**RG-0224 (Squire) lacked the anti-promotion guard its sibling RG-0221 carries.** Both are
spec-only entries for unbuilt features, so both print "now passing → change state to LOCKED" —
and promoting RG-0224 would have locked the spec-only assertion and **retired its nine
shipped-code properties** before a line of Squire exists. RG-0221 already carried
LEDGER-PENDING-BUILD-1; RG-0224 now does too.

### The structural answer
The ledger only knows what somebody thought to assert. "196 holding" means *196 assertions pass*,
not *196 things work*. Both of today's email holes prove it: the July note said "prefer their
contact forms" for three flagged addresses and **no assertion existed** — the moment one was
written (PRIV-OFFICER-1) the true count was five, and the moment a second axis was written
(GOV-DOMAIN-1) it was eight. Nothing was reported falsely; the surface was **unasserted**, and
unasserted surface is indistinguishable from working surface until someone probes it.

### Also found while probing
`GET https://trustsquare.co/health` now returns **403**. The CLAUDE.md note from 25 Jul (as
superseded 5 Aug by GATE-ENFORCE-1) states that `/health` alone still answers openly. It does not.
Anonymous self-verification is now fully closed; in-gate checks must drive David's browser. The
canon note needs correcting at the next attended pass — an undated/stale capability claim is the
same defect class this entry is about.

Files: `scripts/git_unlock.py` (GIT-LOCK-5) · `scripts/regression_ledger.py` (RG-0224 guard) ·
run captured at `outputs/ledger_31aug.txt`.
