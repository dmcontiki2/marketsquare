## 2026-08-27 — Open-items sweep: two live defects, one PII-class leak, and an assertion that was aiming at the wrong door

**OPEN-ITEMS-27AUG** · last ship day before soft-public (Fri 29 Aug, RUL-001)

Ledger opened at **0 REGRESSED · 16 open** and closed at **0 REGRESSED · 14 open**, with three
entries promoted to LOCKED. What follows is what was actually wrong, not what was tidied.

### WAVE-HALFSTALL-1 — every category refused to fill past HALF its target (RG-0192 → LOCKED)

`pipeline/run.py` calls each scraper with `max_results=max(CAP_PER_CATEGORY - already_in_db, 0)`
— the number **still needed**. `google_maps.py`'s DB pre-check then compared the **absolute** count
already in the database against that same argument:

```
CAP 20 · DB holds 11 · remaining = 9 · 11 >= 9  ->  "already has 11/9" -> return []
```

So a category was refused the moment it passed half its target, **silently, and reported as a cost
saving**. The Johannesburg wave finished 184/270 with zero categories brought to quota, and raising
the cap 20→30 could not help because the faulty gate scales with the target.

Fixed by making the contract one thing at both ends: `max_results` means *how many more to collect*,
which is how every other line in that file already read it. The zero-cost short-circuit is preserved
and now correct — it fires on `max_results <= 0`. The DB count is still logged, but **reported, never
enforced**. The whole source layer was then read rather than assumed (the scope's own instruction):
`openstreetmap`, `duckduckgo`, `bing`, `teachers_trainers`, `adventures_accommodation` and
`adventures_experiences` all compare newly-collected against the remaining budget and are correct.
google_maps held the only absolute-count gate in the layer. **Wave 1 fires tomorrow.**

### BIT-LEVERS-REAL-1 — three circuit breakers were placebos (RG-0143 → LOCKED)

The BIT Mitigator was allowed to flip `ai_example_enabled`, `auth_fail_closed` and
`tuppence_burn_enabled`. All three existed as schema columns, an admin write model and a `/flags`
exposure tuple — **and nowhere else**. Flipping one changed a row, reported the S1 as mitigated, and
left the app behaving exactly as before.

That is worse than having no breaker, because a placebo lever *consumes the incident*: the operator
believes the bleeding stopped and stops escalating. The sharpest case is `tuppence_burn_enabled`,
whose declared user message promises **"you will not be charged in the meantime"** while the charge
went through anyway — and it is the exact lever a human would pull during a double-charge incident.

Each is now read where its safe value has to bite. `tuppence_burn_enabled` off means what it says:
the introduction is still **delivered**, any hold is **returned in full**, no Tuppence is deducted,
and a zero-amount `intro_waived` row records why. `tuppence_charged` is still set by the same
conditional UPDATE, so the once-only race guard (INTRO-CHARGE-ONCE-1) is untouched. All reads are
fail-safe toward today's behaviour — wiring them up cannot change how the app runs until somebody
deliberately flips a switch. `prove_intro_hold.py` (22 checks) and `prove_intro_charge_once.py`
(16 checks) both still pass, and both assert the guarded SQL is the text actually in `bea_main.py`.

### POSTURE-REDACT-1 — the site told strangers which defences were down (RG-0144)

`GET /dashboard/summary`, probed anonymously two days before public launch, served:

> pre-launch: Cloudflare WAF allowlist DISABLED (WAF-OPEN-1), origin gate GATE-ENFORCE-1 the only guard

The route's own docstring explains how it happened — *"data is not sensitive; security layer is the
obscure URL"*. True when the summary was project prose; false the day the prose began describing
defences, and nothing re-read the claim.

Redacted at the source rather than 401-ing the route, deliberately: both operator dashboards fetch
it with no credential, and a fix that breaks the console gets reverted under pressure. The scrub is
by pattern and **recurses through the whole payload**, so a field added next month is caught by
machinery rather than by someone remembering not to write about defences in STATUS.md. An
authenticated caller still gets the unredacted text. Proven by `scripts/prove_posture_redaction.py`
(16 checks, using the real 27 Aug leak as its fixture): 6 posture patterns → 0, all 18 fields
retained, clean text returned byte-identical. **Written and proven; ships on the next deploy** —
RG-0144 now distinguishes "not written" from "not shipped", which it previously could not.

### GATE-DRIFT-1 — the assertion was counting a different door (RG-0075 → LOCKED, RG-0196 opened)

Diffing the five "duplicate" gate copies instead of counting them found two things:

1. **`marketsquare.html` is not a copy.** Its `adminGateSubmit` posts to `/review/login` — it is the
   public **reviewer** gate, sharing only the identifier. Counting it inflated the fault from two
   variants to five and pointed the remedy at merging two security doors that must stay separate.
   Real state: three files, two variants.
2. **The drift was live and it was hurting David.** `dashboard.html` and `marketsquare_admin.html`
   were **eight days** behind on GATE-NOLOCK-1 (19 Aug), on *both* the login and change-PIN paths.
   Both still said *"Locked by the pre-launch gate… enter the reviewer code"* on a 401 — a step
   impossible since `migrations/025` exempted those routes. **A correct password was being reported
   as a wrong reviewer code, on the copy RG-0076's own ref records as the one David actually opens.**

Synced; all three now carry the same two corrected messages. RG-0075 was **retitled to assert drift**
— the property that causes harm and is checkable today — because a title claiming "ONE source, not
five copies" while the assertion only measured drift is the same wording-vs-behaviour mistake this
file has now made four times. Consolidation moved to **RG-0196**, kept OPEN and honestly blocked:
`dashboard.html` is opened over `file://`, where `/static/admin_gate.js` cannot load, so the obvious
fix breaks the very consumer that keeps missing gate fixes. That is a post-launch change to the admin
entry path with lockout risk (RUL-027).

### RG-0178 promoted — script-src is live at the edge

PROBED, not taken from the migration reporting ok: `GET /` and `GET /terms` both return
`default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com`.
This also **disproves the Cloudflare-edge-emitter hypothesis** the 26 Aug sweep recorded — the emitter
was nginx all along and 033 had been measuring the port-80 301 redirect. That hypothesis is struck
from the record rather than left to become the next session's wrong turn.

### RG-0180 advanced, deliberately not shipped

The inventory it was blocked on is done: **every** `fetch()` in `ms.js` resolves same-origin, and
`BEA_URL` is the literal `https://trustsquare.co`. There is not one absolute cross-origin
fetch/XHR/WebSocket/EventSource/sendBeacon target in the source. The policy to ship is recorded in
the entry, along with the safe way to ship it (Report-Only first, then enforce). **Not shipped
today**: the entry's own caution is right, it needs a new migration, and the chain was only just
unjammed — adding one on the last ship day is the DEFER-1 risk this project has already paid for twice.

### Board

**189 entries · 175 holding · 0 REGRESSED · 14 open · 0 ready to lock · exit 0.**
`rulings_check.py` 58/58. `eula_sync.py --check` in sync (117,749 B). All 8 `prove_*` harnesses pass.
