# DESIGN BACKLOG — the ONE gated lane for design changes

Fed by BOTH agents (Maintenance via recurrence rule 3; Feedback-Triage via design-change
items). Every dossier is scored against DESIGN_CHANGE_GUIDELINES.md (ten pass/fail criteria);
the GATE line must carry the approver before any build. Batched, never hotfixed.
Pre-launch (until 1 Sep): guidelines apply as a checklist, David is the gate by default.

---

## DCB-001 — Photo pipeline: batch upload, then order online (cover + AI-suggested sequence)

    DOSSIER: photo-batch-then-order        DATE: 2026-08-11   FEEDER: Feedback (F-011)
    PROBLEM: Sellers find upload-in-sequence too difficult on phones; order-at-upload forces
             pre-planning that testers do not do. (Solution-free statement; the ask below
             rides separately.)
    EVIDENCE: F-011 (David Jnr, sequencing "too difficult"); TS-0006 (duplicate-photo
             judgement); TS-0022/28/29/30 (Maroushka, cover/photo friction); TS-0030 (HEIC
             silence). ≥2 independent reporters; photo-pipeline friction is a THEME.
    PROPOSED DIRECTION (rides separately): batch-upload any order → grid view → tap ONE as
             cover → "AI order" button arranges the rest per canon (cover rules, exterior→
             interior→detail) → drag to adjust → publish. Consistency enforced at OUTPUT
             (defaults + existing gates: blur ceiling, cover checks), not at INPUT.
             David Jnr's ease and David's consistency are the same feature seen from two ends.
    SCOPE: sell flow photo step (ms.js), possibly a BEA order-suggestion call (photo set →
             suggested sequence). No schema change (photos already carry order).
    REVERT: one deploy (UI change; flag-gateable behind launch_switches).
    MEASUREMENT: time-to-publish for a photo set (before/after); cover-replacement rate;
             tester retest by David Jnr ("is it easy now?").
    SCORE: 1 PASS (evidence above) · 2 PASS · 3 PASS (scope named, no trust core) ·
             4 PASS (existing patterns; no fake controls) · 5 PASS (flag + revert) ·
             6 PASS (measures named) · 7 PENDING (phone-first mock to verify) ·
             8 PASS (batched) · 9 PENDING (copy pass) · 10 PENDING — GATE EMPTY.
    GATE: ____________________  (approver name, date, one line — absent = do not build)
