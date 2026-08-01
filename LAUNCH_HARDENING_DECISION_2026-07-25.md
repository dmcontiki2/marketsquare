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

**DELIVERED — 26 Jul 2026 (server-side git-pull auto-deploy).** Built the "self-hosted
runner on the box" option — a git-driven deploy the server runs itself, so no human runs
`deploy_marketsquare.bat`. Files in `ops/autodeploy/` + `activate_autodeploy.bat`,
`release.bat`, `deploy_web.py`; full guide in `ACTIVATION.md`.
- **Engine (`server_deploy.sh`).** Pulls the tracked ref, places files via an allowlist
  manifest (the same renames the `.bat` does — never deletes, so the live DB/`.env`/uploads
  are untouched), bumps the cache-buster monotonically, restarts `marketsquare`, reloads
  nginx, purges the CDN, health-checks `/health`, and **auto-rolls-back** (restores a
  pre-deploy file snapshot + the previous commit) if the app doesn't come up. Verified in a
  mocked-server harness: placement+renames, monotonic `?v=` bump, idempotent no-op on an
  unchanged ref, and the unhealthy→rollback path (exit 2, good files restored, bad SHA not
  recorded).
- **Trigger.** A `systemd` timer (`marketsquare-deploy.timer`) polls the mirror every 2 min
  and deploys only when the tracked `deploy` ref advances (explicit-intent default; a one-line
  switch to `MS_DEPLOY_REF=main` gives full GitOps). Plus an OPTIONAL authenticated
  `POST /admin/deploy` HTTPS hook (`deploy_router.py`, off unless `MS_DEPLOY_TOKEN` is set on
  the server) as the port-443 trigger for sessions that can't ssh or push.
- **One deploy engine.** The endpoint and the timer both call `server_deploy.sh` — one engine,
  one rollback story, consistent with `/ship` and `/TSL`.
- **Activation is one step:** double-click `activate_autodeploy.bat` once. After that, "go
  live" is `release.bat` (one push) or `deploy_web.py` from any session.
- **Honest access boundary (verified this build):** a *scheduled, unattended* cloud session
  cannot push to the mirror (sandbox git proxy returns 403; read/clone work) and has no server
  key, so its only route is HTTPS/443. It therefore cannot trigger a deploy on its own until
  David grants ONE channel: either enable the `/admin/deploy` token, or grant the session push
  access to the `deploy` ref. Until then the mechanism is fully hands-free for David
  (`release.bat`) but not yet for a human-absent scheduled run. This is a deliberate boundary,
  documented in `ACTIVATION.md`.
- **Still open:** the `.bat`'s false-`[OK]`-on-failure quirk is left unchanged (can't be tested
  from the cloud; fix in an attended session). The new engine handles exit codes correctly and
  gates on a real health check, so cloud-path deploys don't inherit that quirk.

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
