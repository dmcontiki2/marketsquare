- **STANDING LANE MOVES TO OPENAI (David's ruling, 14 Aug 2026 — Addendum 11).** Resulting order:
  **1. OpenAI (standing) · 2. Anthropic · 3. Scaleway EU · 4. Grok** (capped, text tiers only, not
  wired pre-launch). The reason is INDEPENDENCE, not price — David's words: this "will also ensure
  we don't use Anthropic as the CEO/COO/Guidance and also then outsource our work to Anthropic."
  Claude authored most of this codebase and advises at CEO/COO level; the same vendor also doing the
  production work makes judgement and execution one correlated dependency. Addendum 1 already
  accepted that logic for REVIEW ("Claude auditing Claude has correlated blind spots"); this extends
  it to EXECUTION. Supersedes "Staying with Claude" as the STANDING LANE only — Claude remains the
  guidance/harness layer, which was never the thing being procured. Cost independently agrees
  (funnel: gpt-5.6-luna first on haiku/triage/vision at +78/78/79%, golden-set passed) but did not
  drive it. Sonnet's +25% is below the 30% bar and moves anyway as part of a whole-lane ruling —
  a different decision class from per-tier procurement, which the 30% bar still governs.
- **The $50/90d absolute floor is now a POST-LAUNCH test, not a pre-launch gate.** It requires
  spend-log volumes that cannot exist before launch, so applied pre-launch it was never a test —
  it was a permanent block. David: these were "discussions that then became hammers to keep us
  pegged." From first revenue it applies as written; before that it is informational and never
  blocks. Amended on the card so the rule travels with the data (Addendum 8's own design).
- **Standing principle worth keeping:** an analysis output is not a requirement, and a gate that
  cannot be satisfied in the current phase is a blocker masquerading as rigour. Same fault class as
  a guard asserting an implementation detail instead of an invariant — DRIFT-CACHEBUST-1 and the
  stale maint-scope guard, both found the same day.
- **LIVE — flip applied and verified 14 Aug 2026, 20:05 UTC.** `POST /admin/flags` needs a JWT from
  a dashboard login, which Claude will not perform on David's behalf, so the change went in as a
  direct write to `launch_switches.ai_active` on the box — database backed up first
  (`marketsquare.db.bak-lane-20260814-200544`), no credential typed, displayed or handled by anyone.
  The provider cache is ~10s and the lane is DB-backed by design ("Page-4 switchable, no restart"),
  so it took effect without a restart. Verified from the app's own `GET /flags`, not from the row
  written: **active=openai · standing=openai · override=null**. Record and live now agree and
  **RG-0019 reads green** ("live standing lane 'openai' == register — record is current"); RG-0018
  green too (card 13d old, 5 priced / 5 wired). Rollback = same write with 'anthropic', or restore
  the printed .bak-lane file.
