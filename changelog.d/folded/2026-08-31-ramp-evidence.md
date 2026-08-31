## 2026-08-31 — RAMP-EVIDENCE-1: the outreach ramp was growing on the absence of evidence (RG-0225)

David flipped the Resend $20/50k tier (D6, RUL-061) and asked what it unlocks for beating the
contagion model. Checking rather than answering found the honest reply — **the mail quota was never
the binding constraint** — and, underneath it, a live defect in the thing that IS the constraint.

**The defect.** RAMP-1 (RG-0213) doubles a city's wave batch when the last wave's bounce rate is
≤ 2%. That rate is computed from `prospects.bounced_at` in the **local** CityLauncher database, and
the local database only learns about a bounce when `pull_from_server.py` runs. That script's own
docstring says *"Run BEFORE composing any wave"* — but **nothing enforced it, `wave_runner` never
called it, and nothing recorded whether it had ever happened.** Probed: the local store holds 110
`sent` events and **no other event of any kind**, while the webhook receiver that maps
`email.bounced → bounced` lives server-side in `CityLauncher/api/server.py`. Both armed cities were
therefore scoring a clean streak off zero bounces that had never been looked for, and RAMP-1 would
have doubled 12 → 24 → 48 → 96 on **ignorance**. Same family as RG-0133 (no instrument wears a
health colour nothing measures) and RG-0202 (a verify half must answer for the thing it gates).

**Fixed the same session, CTO call under RUL-037:**

- `pull_from_server.py` now writes a dated witness, `data/last_pull.json` (pulled_at, verdicts seen,
  what was applied).
- `wave_runner.py` gained `evidence_state(city)`: a wave may only count toward the clean streak if
  the verdicts were pulled **after** it was sent. Never pulled, or pulled before the last send →
  hold at base and say so. **Deliberate boundary: stale evidence never blocks a send** — the
  stop-loss gate owns blocking; this owns *growing*. Failing closed means holding at 12.
- `--plan` now prints the evidence line per city, and flags any city pinned by an explicit
  `batch_size`.
- Removed the explicit `batch_size: 12` pins on **Pretoria** and **Johannesburg**. They equalled the
  base so they changed nothing on day one — but an explicit per-city size **overrides** `ramp_state`,
  so those two cities could never have earned a doubling however clean they ran. The ramp David
  ratified on 30 Aug was inert on the only two armed cities. National's documented 30 stays
  (RG-0213's named exception).
- **RG-0225 LOCKED**, behaviourally proven: never-pulled and stale-pull both refuse to grow, a pull
  after the last send allows it, and a city with no waves yet sits at base without complaint. The
  policy half asserts that no *armed* city may re-acquire a `batch_size` pin.

**Net effect right now:** both armed cities read `STALE — ramp held at base`. The moment
`sync_to_server.bat` runs and the 29–30 Aug waves prove genuinely clean, Pretoria earns 24
automatically. Earned, not configured — as ratified.

**Also recorded (probed, not blocking):** Johannesburg's sendable agency pool is **empty** (47
emailed, 0 left); Pretoria holds 201. Pool depth, not send rate, is what binds — which is the
model's own `scrapeWk` lever.

Files: `../CityLauncher/pull_from_server.py` · `../CityLauncher/emailer/wave_runner.py` ·
`../CityLauncher/emailer/waves_policy.json` · `scripts/regression_ledger.py`.
