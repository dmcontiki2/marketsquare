## 2026-08-21 — Five open actions RESOLVED under David's standing instruction ("fix the ones already directionally agreed; I keep the veto")

David: *"I am stuck in the details here... assume the task of resolving the open actions where the
required approval already directionally agrees with our requirements and goals, fix those ones and
just report the solutions to me; this will then allow me a veto at that point."* Register went from
**7 open to 2**. Every closure below re-ran its originating check.

**DW-027 — the ruling had already been given, and built, on 7 Aug.** The row waited 14 days for
"above a blurred-fraction threshold, refuse the photo — behind a launch switch defaulting OFF".
On disk since 7 Aug: `_ANON_MAX_BLUR_FRAC = 0.18`, measured by `_anon_blur_fraction()` BEFORE the
next layer is painted (the point a photo turns to porridge), at four call sites, each returning
`needs-replacement` instead of an image. The switch `launch_switches.photo_replace_request`
defaults **ON, not OFF** — David's ruling, with the code commented to say a missing key must read
ON or it "would silently restore the very behaviour Maroushka reported three times". RG-0047 LOCKED
and holding. Today PHOTO-REJECT-1 (RUL-033) is stricter still. The row was stale, not unanswered.

**DW-028 — the premise was retired, not satisfied.** It asked David to provision an ops API_KEY so
the gzip probe could read `/ops/selfcheck`. That was never a gzip problem, it was an instrument
problem: the entry judged a key-gated stand-in because the armed gate 401'd `/wonders`; the gate
came down (RUL-029/034) and the stand-in stayed gated, so RG-0101 sat OPEN reporting a 401 on the
PROXY while the property had been live since 18 Aug. Probe repointed onto `/wonders` itself through
the ledger's `ts_review` cookie — **160,022 B on the wire**. No click needed.

**DW-010 / CC-002 — FORMALLY DEFERRED to the first post-launch week (from Mon 8 Sep).** The row
offered "land or formally defer" and had read 68d → 71d → 72d while nobody chose. CC-002 is not one
decision but ~10 open pricing/product questions in `AWAITING_DAVID.md`, several touching the EULA
and one touching a **live Paystack SKU** carrying an explicit "do NOT deploy a removal unattended"
warning. RUL-001 puts soft-public 8 days out. Deferring is launch-aligned; landing is not. Moved to
SCHEDULED so `cc_age_check.py` stops reporting an untaken decision as a threshold breach every
Monday. **Veto point:** if one CC-002 item must land pre-launch, name it and it lands alone.

**DW-044 — cost sweep now reports `0 critical`** (was 2). Took the row's second offered path,
"strike the opus rate row and record AdvertAgent as out of perimeter", because the first is not a
tidy-up: AdvertAgent calls Anthropic directly to use the **web-search tool the seam does not
carry**. (a) premium-tier rate row struck — nothing ever called it, all ten live functions run
sonnet, it existed only to be found; (b) `calc_cost()` stops pricing an unknown model *silently* at
the Sonnet fallback and logs `[AA-COST] UNPRICED MODEL` — silent fallback costing is how a premium
model runs for weeks looking cheap; (c) both baseline artefacts rewritten to state the perimeter as
a DECISION with its reason, replacing text that described the fault and which the sweep was
flagging as an opus call site — its own bug report tripping its own detector, the DW-043/DW-047
loop again. **No model was chosen on David's behalf**; the ten sonnet sites, the absent downscale
ladder and max_searches 20 remain his by the model-selection standing rule.

**DW-054 — RG-0128 written and LOCKED: the AI breaker fails OVER, not merely open.** Ten Anthropic
incidents 12-19 Aug, eight consecutive days without a clear one, and a failover nobody had ever
seen work. NOT proven by live fault injection — that means spending on a real call or breaking the
live lane 8 days before launch. `scripts/prove_ai_failover.py` stubs **only the vendor sockets** and
exercises the real `complete()`, the real cost-approved fallback ranking, the real breaker
recording. **13/13**: 5xx, 401 and 429 each move to the next lane and return THAT lane's answer;
all-lanes-down fails honestly reporting the REQUESTED lane's error, not the last tried; `probe=True`
and `allow_fallback=False` respected. **RESIDUAL, deliberately not swept up:** this proves the
DECISION layer. Whether failover has anywhere to GO depends on ≥2 lanes holding keys on the box,
readable only at OPS-key-gated `/ops/selfcheck` — so RG-0128's live half reports **INFO, not a
pass**, and says so in words. `OPENAI_API_KEY` is on record unprovisioned (RG-0016), so a
single-lane production chain is entirely possible.

**Ledger: exit 0 — 121 entries · 119 holding · 0 REGRESSED · 2 open · 0 ready to lock.** The two
open are honest: RG-0075 (admin-gate script duplicated across 5 files) and RG-0121 (canary dark by
design). RG-0101 was promoted by a concurrent session during this work.

**NOT done, and named rather than quietly dropped:**
- **DW-057/DW-029 (rotation) stays David's click.** I considered scripting the systemd-unit half to
  make it one double-click. I did not: I cannot test it against the box, and an untested script
  that rewrites the live service unit 8 days before launch is worse than the manual edit. Handling
  the credential values is out of bounds regardless.
- **AdvertAgent inside the seam** — a real refactor around an Anthropic-shaped tool, David's call.

**Process note, recorded because it nearly bit.** A concurrent session was editing
`scripts/regression_ledger.py` during this work (it shipped EULA v1.14 and had independently fixed
RG-0101 the same way I was about to). My guarded write pattern — exact-anchor + `assert count == 1`
before replacing — refused rather than duplicating, which is the only reason there is no collision
to unpick. The re-read-before-write rule earned its keep today; it is not ceremony.
