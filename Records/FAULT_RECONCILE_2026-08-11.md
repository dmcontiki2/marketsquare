# Fault reconciliation — 11 Aug 2026 (amber sweep, attended)

Queue before: 6 new / 1 awaiting-retest / 20 verified / 2 dup / 1 closed. After: 2 new /
1 awaiting-retest / 21 verified / 2 dup / 4 closed. Every transition on named evidence:

- **TS-0030 → verified.** Live probe this session: GET /listings → listing 335 serves 8 photos
  publicly. Silenced-error fix shipped release 8ff0b85; cache-buster bump covers staleness.
- **TS-0027 → closed.** Rentals/For-Sale toggle = Path B design change → design backlog
  (per the morning loop's own triage note; guidelines gate applies).
- **TS-0021 → closed.** AI-vendor value/audit strategy question → David (standing rule).
  Unattributed 'headline' console tail stays under RG-0054 watch.
- **TS-0006 → closed.** Duplicate-photo aggressiveness = Path B product decision → backlog.
  Incidental l.trust crash fixed separately (CV-GUARD-1 / RG-0054, morning loop).
- **TS-0022 → stays awaiting-retest, note rewritten reader-facing.** Class fix live
  (RG-0047, 8ff0b85); her 9 pre-fix covers (328,327,333,341,330,324,342,325,334) need
  seller replacement — the retest letter IS the replacement request; drafted, awaiting
  David's send. Her re-uploads each pass the new gate; recur≥3 chip clears when verified.
- **TS-0024 stays new (honest).** Single-vendor gate structurally closed (RG-0032) but the
  outstanding evidence is one end-to-end property-coach run — tomorrow's loop or attended.
- **TS-0018 stays new (needs David).** "If we don't use this, can we remove it?" — referent
  unknown; one sentence from David naming the element clears it.

Chips after refresh: majors 6→2, queue 6→2, closed 21→25. Still amber by DESIGN/pending:
retest 1 (Maroushka's re-uploads), recur≥3 1 (same row), tp_tours (David's resubmit moment,
OPEN_LOOPS D10), BIT UNKNOWN ×2 (clears when the next deploy lands migrations/013's server
BIT timer — also runs 011 Tier-2), top bin MISC ×26 (mostly honest: SPA reports carry the
root URL; real fix = widget sends the active screen — queued for a session when bea_main.py
is free; NOT touched today to avoid colliding with the adverts session).
