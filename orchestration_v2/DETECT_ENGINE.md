# Detect Engine — Orchestration v2 · Phase 1
**Status:** built · 🟢 green lane (reads & reasons — produces findings, applies NO fixes) · model-agnostic · reversible (files only)
*Part of the clean rewiring. Whole picture: `ORCHESTRATION_V2_DESIGN.html`.*

## What it is
The reusable, one-command version of the parallel sweep we ran by hand on 5 Jun 2026. Point it at a **scope**; it fans out agents in parallel, each audits one slice, then the findings are consolidated, adversarially cross-checked, and **gently re-verified** before anything is reported.

## Invoke
> "Run the Detect engine on `<scope>`."
> e.g. *"Run the Detect engine on demo mode, all cities, all home sections."*

## Inputs
- **Scope** — broken into independent **slices** (one per agent). Pick the dimension that gives clean, non-overlapping slices (home-section × all-cities, file-area, category…).
- **Second Brain** — read baselines + prior findings so we don't re-report what's known.

## Process (the green-lane loop)
1. **Slice** the scope into N independent units (aim 3–6 agents; more only if the work needs it).
2. **Fan out** one agent per slice, in parallel — each gets the shared context, its slice, the checklist (bleed / empty-state / data-quality / filter-sync / crash-risk / locale), and the OUTPUT SCHEMA. Agents **report only — never fix.**
3. **Consolidate** — merge findings, dedupe.
4. **Adversarial cross-check** — hunt contradictions & over-counts; resolve or down-grade. (On 5 Jun this caught "80 vs 60" and a false Pretoria undercount.)
5. **Gentle verify** — any finding that depends on a live external resource (a URL, an endpoint) must survive `detect_verify.py` (LOW concurrency + retry). **Never hammer** — aggressive parallel checks rate-limit and fool the tool into false positives (the 5 Jun scanner flaw). A finding isn't *real* until it passes a gentle check.
6. **Write** the prioritised list to the Second Brain (`findings/<date>.md`) and surface the summary to the cockpit.

## Output schema (one record per finding)
    SEV:        HIGH | MED | LOW
    SLICE:      which agent / area
    SYMPTOM:    what the user sees
    ROOT CAUSE: function/file/line, or data field
    FIX:        suggested — for the Fix stage, NOT done here
    LANE:       green | amber | red   (proposed)
    CONFIDENCE: confirmed | NEEDS-CONFIRM

## Guardrails
- **Green lane only.** Detect changes nothing. Fixes happen in the Fix stage under the lane rules.
- **Verify gently, always.** The detector never trusts its own first answer on anything live.
- **Model-agnostic.** Any reasoning model can run this — it's instructions + a helper. Off-grid ready.

## Next bricks (later phases, not built yet)
Triage formalised (P2) · Fix with lanes + poka-yokes (P3) · Prevent monitors (P4) · Orchestrator + Scheduler wiring & cutover from the old loop (P5).
