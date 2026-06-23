# TrustSquare Patent + Whitepaper Convergence Loop

A self-improving, multi-agent loop that hardens the TrustSquare provisional
patent spec and technical whitepaper against prior-art, compliance, and
litigation risk — then promotes them to a major-revision baseline once they stop
changing (Δ = 0).

## What's in here
```
patent-loop/
├── CLAUDE.md                  ← the loop spec (the brain). Read this first.
├── README.md                  ← you are here
├── working/
│   ├── patent.md              ← live working copy (v6.0) — the loop edits THIS
│   └── whitepaper.md          ← live working copy (v3.5) — the loop edits THIS
├── staging/                   ← Maker writes here; the Auditor reads ONLY this
├── audit/
│   ├── audit_feedback.json    ← Auditor → Maker corrective actions (per loop)
│   ├── audit_feedback.template.json
│   ├── search_history.log     ← every query, no reuse across loops
│   ├── loop_counter.txt
│   └── audit_trail.md         ← written on convergence (counsel hand-off)
└── archive/                   ← per-version snapshots for Δ comparison
    ├── patent.v6.0-input.md   ← frozen input baseline
    └── whitepaper.v3.5-input.md
```

## The three agents
1. **Maker** — multi-jurisdictional web search (SA/CIPC first, then WIPO/PCT,
   US, EU, APAC), then revises both docs to design around prior art and strip
   risk. Saves to `staging/`.
2. **Doctorate Auditor** — a fresh, adversarial sub-agent with NO access to the
   Maker's reasoning or search logs. Sees only the staged text. Runs the
   compliance checklist and tries to invalidate the docs. Emits
   `audit/audit_feedback.json`.
3. **Gatekeeper** — applies the feedback, bumps a minor version, measures the
   delta, and decides: loop again (Δ ≠ 0) or terminate (Δ = 0). On termination,
   promotes to a major baseline.

## The originals are never touched
The counsel-gated `.docx` files in `../` are **frozen**. The loop works only on
`.md` working copies. On convergence it produces *candidate* `.docx` files
stamped "AUTO-CONVERGED — NOT COUNSEL-APPROVED". Counsel still gates the real
filing (per `../../LEGAL_VERSIONS.md`).

## How to run it
From this directory, give the agent:

```
Read CLAUDE.md in this folder and execute the document optimisation loop on
working/patent.md and working/whitepaper.md. Search live sources each iteration,
audit adversarially, apply fixes, and do not stop until a zero-delta loop is
reached and the major baseline (patent v7.0 / whitepaper v4.0) is saved. Respect
every safety rail in CLAUDE.md — the .docx originals stay frozen and no citation
may be invented.
```

To run a single supervised iteration instead of the full auto-loop, add:
`Run ONE iteration only, then show me the audit_feedback.json and the diff before
continuing.`

## Tuning the loop
All behaviour lives in `CLAUDE.md`:
- **Jurisdiction priority** → Phase 1 §1A
- **Prior-art search matrix** → Phase 1 §1B
- **Auditor compliance checklist** → Phase 2 (§1–§4)
- **Convergence / stop conditions** → Phase 3 §3B (incl. the 8-loop safety stop)
- **Major-baseline behaviour** → Phase 4

## Status
Seeded 2026-06-23. Working copies extracted from
`TrustSquare_Provisional_Specification_DRAFT_2026-06-11.docx` (v6.0) and
`TrustSquare_WhitePaper_v3_5_DRAFT.docx` (v3.5). Loop not yet run.
