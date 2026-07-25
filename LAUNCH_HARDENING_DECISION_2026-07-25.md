# Launch Hardening — Decision & Program
Date: 25 Jul 2026 · Status: APPROVED (David: "fix it fully, before launch, end of August")
Owner: Claude (maintainer) · Steered by: David

## 1. Why we kept battling (root cause, not symptom)
Two separate causes got tangled and made a 10-minute bug feel like a half-day:

**(a) Feedback-loop blindness.** The AI maintainer has no route to the live server —
the cloud sandbox can't SSH to Hetzner, the device bridge has no network, and the deploy
is a Windows .bat only a human can run. So every wrong assumption only surfaced AFTER a
human-run deploy. That is the biggest time sink, and it is a tooling gap, not a code fault.

**(b) No enforced data contract.** `listings.category` is free text with inconsistent
casing (adventures/local_market lowercase; Cars/Property/Tutors/Collectors/Services Title
Case). Country was DERIVED from geo_cities, not stored. Columns accreted via ad-hoc
migrations. The tell: the read side already defends everywhere with `LOWER(category)` —
the team knew it was inconsistent and papered over it on reads instead of normalising on
writes. Any new code (mine) or any new listing SOURCE (seller form, agency import, API)
trips over it. This is the defect class that will bite hardest when listings arrive
"from everywhere" post-launch.

## 2. The program (four workstreams, sequenced so each de-risks the next)

### Phase 1 — Observability (the eyes)   [risk: low · effort: low]
- DONE tonight: `scripts/diag_super.py` — read-only snapshot (trust/category/country +
  mismatch flags), wired into deploy as `[3g-diag]`. Writes nothing.
- Next: a small authenticated, read-only `/admin/diag` JSON endpoint the maintainer can
  query any time over HTTPS. This is the wedge that ends the blindness.

### Phase 2 — Data contract   [risk: medium · effort: ~1 week · DB-agnostic]
- One `normalize_listing()` gate EVERY write path funnels through: canonical category
  (single enforced spelling), country set + stored, required fields validated.
- One-time cleanup of existing mixed-casing category data.
- Enforce it (CHECK constraint / category lookup) so drift cannot recur from any source.

### Phase 3 — Automated deploy   [risk: medium · effort: few days]
- `git push` -> CI/CD (GitHub Actions or a self-hosted runner on the box) runs the deploy
  and posts results. Removes "a human runs the .bat" as the bottleneck.
- While here: fix the deploy .bat's false `[OK]`-on-failure (it reads exit codes wrong
  inside if-blocks and hid failures today).

### Phase 4 — Postgres   [risk: high (cutover) · effort: 1-2 weeks]
- Migrate SQLite -> Postgres: write concurrency for continuous multi-source ingestion,
  an ENFORCEABLE category type (gives the contract teeth), and a read replica for safe
  observability.
- GO/NO-GO GATE (~mid-Aug): if not rock-solid, defer ONLY the DB cutover to shortly
  post-launch — SQLite hardened holds the launch; every other phase is already delivered.
  This gate is the pressure valve that protects the launch date.

## 3. Current listing bugs (folded into Phase 1/2 — status)
- Missing 15 category listings (case mismatch): FIXED — case-insensitive category match. (verified locally)
- Currency/flag/map wrong by country: FIXED — `listings.country` column added + backfilled from geo. (verified locally)
- Trust 90->45 flicker: FIXED — exemplar trust aligned to its seller's own trust (US/GB/AU). (verified locally)
  NB: ZA carries the SAME latent mismatch (diag confirms); left UNTOUCHED pending live diag review.
- Adventures page shows the VIEWER's country currency (rands) not each listing's own: OPEN —
  a frontend change to the Adventures render; do it with verification once the diag endpoint is live.

## 4. Calendar (to end-August)
- Wk1: finish Phase 1 (live diag endpoint) + start Phase 2 (normalize_listing + category cleanup).
- Wk2: finish Phase 2 + Phase 3 (automated deploy).
- Wk3: Phase 4 Postgres build + test on a copy.
- Wk4: Phase 4 cutover (or gate-defer) + hardening.
- Wk5: buffer + launch rehearsal.

## 5. Principle going forward
No more blind patches. Build the instrument, fix against facts, verify. Tonight's bug was
the cheap canary that justified this whole program — a data-integrity fault flushed out
with 24 rows we control, not 10,000 at launch we don't.
